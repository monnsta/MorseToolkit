from dataclasses import dataclass, field
from collections.abc import Iterator

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


@dataclass(slots=True)
class _MorseTrieNode:
	"""Internal node structure for the Morse word trie."""
	children: dict[MorseSymbol, "_MorseTrieNode"] = field(
		default_factory=dict
	)
	words: list[tuple[str, int]] = field(
		default_factory=list
	)


class MorseWordIndex:
	"""A prefix-tree (Trie) index mapping Morse symbol sequences to valid words.

	Optimizes the search for matching dictionary words within a continuous Morse sequence.
	"""

	def __init__(
		self,
		word_codes: Iterator[
			tuple[str, tuple[MorseSymbol, ...]]
		],
	) -> None:
		"""Initializes the trie and populates it with word-symbol mappings.

		Args:
			word_codes: An iterator yielding tuples of a text word and its encoded Morse symbols.
		"""
		self._root = _MorseTrieNode()

		for word, symbols in word_codes:
			self.add(word, symbols)

	def add(
		self,
		word: str,
		symbols: tuple[MorseSymbol, ...],
	) -> None:
		"""Inserts a word and its corresponding Morse sequence into the trie.

		Args:
			word: The plain text word.
			symbols: The sequence of Morse symbols representing the word.

		Raises:
			ValueError: If the symbol sequence is empty.
		"""
		if not symbols:
			raise ValueError(
				"Cannot index an empty Morse sequence"
			)

		node = self._root

		for symbol in symbols:
			node = node.children.setdefault(
				symbol,
				_MorseTrieNode(),
			)

		node.words.append(
			(word, len(word))
		)

	def matches(
		self,
		sequence: tuple[MorseSymbol, ...],
		position: int,
		max_word_length: int,
	) -> Iterator[MorseWordMatch]:
		"""Finds all valid dictionary words that match the sequence starting at a given position.

		Args:
			sequence: The full sequence of Morse symbols being evaluated.
			position: The starting index within the sequence to check for matches.
			max_word_length: The maximum allowed length of a matching text word.

		Yields:
			MorseWordMatch instances representing valid words found.
		"""
		if position >= len(sequence):
			return

		node = self._root

		for end in range(position, len(sequence)):
			node = node.children.get(sequence[end])

			if node is None:
				return

			for word, word_length in node.words:
				if word_length <= max_word_length:
					yield MorseWordMatch(
						word=word,
						end=end + 1,
					)
