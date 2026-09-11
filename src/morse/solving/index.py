from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from morse.core import MorseSymbol


@dataclass(frozen=True, slots=True)
class MorseWordMatch:
	"""Represents a matched word within a Morse sequence.

	Attributes:
		word: The matched plain text word.
		end: The exclusive index in the sequence where the match ends.
	"""

	word: str
	end: int


class MorseWordIndex:
	"""Compact integer-based index for matching encoded Morse words.

	Each Morse sequence is represented by an integer whose leading ``1`` bit
	acts as a length delimiter. This allows sequences of different lengths to
	be stored in the same dictionary without collisions.
	"""

	def __init__(
		self,
		word_codes: Iterable[tuple[str, tuple[MorseSymbol, ...]]] = (),
	) -> None:
		"""Initializes the index and populates it with encoded word mappings.

		Args:
			word_codes: An iterable yielding tuples of a text word and its
				encoded Morse symbols.
		"""
		self._words: dict[int, list[str]] = {}
		self._max_symbols = 0

		for word, symbols in word_codes:
			self.add(word, symbols)

	def add(
		self,
		word: str,
		symbols: tuple[MorseSymbol, ...],
	) -> None:
		"""Inserts a word and its corresponding Morse sequence into the index.

		This method accepts the normal symbol representation and is useful
		when adding already-encoded Morse sequences.

		Args:
			word: The plain text word.
			symbols: The sequence of Morse symbols representing the word.

		Raises:
			ValueError: If the symbol sequence is empty.
		"""
		if not symbols:
			raise ValueError("Cannot index an empty Morse sequence")

		self.add_encoded(
			word,
			self._encode_symbols(symbols),
			len(symbols),
		)

	def add_encoded(
		self,
		word: str,
		key: int,
		symbol_length: int,
	) -> None:
		"""Inserts a word using an already-encoded integer Morse key.

		This avoids converting an integer representation back through
		``MorseSymbol`` objects when dictionary words are being indexed.

		Args:
			word: The plain text word.
			key: The integer key representing the complete Morse sequence.
			symbol_length: The number of Morse symbols represented by ``key``.

		Raises:
			ValueError: If the symbol length is less than 1.
		"""
		if symbol_length < 1:
			raise ValueError("Morse symbol length must be at least 1")

		words = self._words.get(key)

		if words is None:
			self._words[key] = [word]
		else:
			words.append(word)

		if symbol_length > self._max_symbols:
			self._max_symbols = symbol_length

	def _encode_symbols(
		self,
		symbols: tuple[MorseSymbol, ...],
	) -> int:
		"""Encodes a Morse sequence into a single integer key.

		A leading ``1`` bit acts as a length delimiter, so sequences of
		different lengths can never collide.

		For example:

			DOT       -> 10
			DASH      -> 11
			DOT DOT   -> 100
			DOT DASH  -> 101

		Args:
			symbols: The Morse symbols to encode.

		Returns:
			A compact integer key.
		"""
		key = 1

		for symbol in symbols:
			key <<= 1

			if symbol is MorseSymbol.DASH:
				key |= 1

		return key

	def matches(
		self,
		sequence: tuple[MorseSymbol, ...],
		position: int,
		max_word_length: int,
	) -> Iterator[MorseWordMatch]:
		"""Finds all dictionary words matching from a sequence position.

		The sequence is traversed once from the requested position while its
		prefix is incrementally converted into the same integer representation
		used by the index.

		Args:
			sequence: The full Morse sequence.
			position: Starting sequence position.
			max_word_length: Maximum allowed text word length.

		Yields:
			Matching MorseWordMatch instances.
		"""
		if position >= len(sequence):
			return

		key = 1
		max_end = min(
			len(sequence),
			position + self._max_symbols,
		)

		for end in range(position, max_end):
			key <<= 1

			if sequence[end] is MorseSymbol.DASH:
				key |= 1

			words = self._words.get(key)

			if words is None:
				continue

			for word in words:
				if len(word) <= max_word_length:
					yield MorseWordMatch(
						word=word,
						end=end + 1,
					)
