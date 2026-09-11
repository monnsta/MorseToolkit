from collections.abc import Iterable, Mapping

from morse.alphabets import InternationalMorse
from morse.core import (
	MorseCandidate,
	MorseSequence,
	MorseStream,
	MorseSymbol,
	MorseTokenType,
)
from morse.encoding import MorseDecoder, MorseEncoder
from morse.parsing import (
	MorseBoundarySyntax,
	SpacedParser,
	UnspacedParser,
)
from morse.representations import (
	MorseRepresentation,
	TextRepresentation,
)
from morse.solving import (
	BigramScorer,
	DictionaryScorer,
	FrequencyScorer,
	MorseDictionary,
	MorseScorer,
	MorseSolver,
)


class Morse:
	"""High-level interface for working with Morse code.

	This class provides a convenient API over the lower-level MorseToolkit
	components while still allowing those components to be customized.

	Example:
		morse = Morse()

		encoded = morse.encode("HELLO WORLD")
		decoded = morse.decode(encoded)

		print(encoded)
		print(decoded)
	"""

	def __init__(
		self,
		alphabet=None,
		representation: MorseRepresentation | None = None,
		boundaries: MorseBoundarySyntax | None = None,
		dictionary: MorseDictionary | Iterable[str] | None = None,
		scorer: MorseScorer | None = None,
		max_word_length: int = 32,
		beam_width: int = 8,
	) -> None:
		"""Initializes a Morse toolkit instance.

		Args:
			alphabet: Morse alphabet implementation. Defaults to International Morse.
			representation: String representation for dots and dashes.
			                Defaults to standard '.' and '-'.
			boundaries: Character and word boundary syntax.
			            Defaults to one space between characters and three between words.
			dictionary: Dictionary or word iterable used for solving unspaced Morse.
			scorer: Scorer strategy used for candidate evaluation.
			max_word_length: Upper limit on dictionary word length.
			beam_width: Maximum search state beam width for contextual solving.
		"""
		self.alphabet = alphabet or InternationalMorse()
		self.representation = representation or TextRepresentation()
		self.boundaries = boundaries or MorseBoundarySyntax()

		self.encoder = MorseEncoder(self.alphabet)
		self.decoder = MorseDecoder(self.alphabet)

		self.spaced_parser = SpacedParser(
			self.representation,
			self.boundaries,
		)
		self.unspaced_parser = UnspacedParser(
			self.representation,
		)

		self.word_dictionary = dictionary
		self.scorer = scorer
		self.max_word_length = max_word_length
		self.beam_width = beam_width

	def encode(self, text: str) -> str:
		"""Encodes plain text into human-readable Morse code.

		Args:
			text: Text to encode.

		Returns:
			A spaced Morse representation.

		Example:
			morse.encode("HELLO WORLD")
			# ".... . .-.. .-.. ---   .-- --- .-. .-.. -.."
		"""
		stream = self.encoder.encode(text)

		return self._format_stream(stream)

	def encode_unspaced(self, text: str) -> str:
		"""Encodes text into continuous Morse without boundaries.

		This is useful for producing input suitable for ``solve()``.

		Args:
			text: Text to encode.

		Returns:
			A continuous Morse representation.

		Example:
			morse.encode_unspaced("HELLO")
			# "......-...-..---"
		"""
		symbols: list[MorseSymbol] = []

		for character in text:
			if character == " ":
				continue

			symbols.extend(self.alphabet.encode(character))

		return "".join(self.representation.encode(symbol) for symbol in symbols)

	def decode(self, value: str) -> str:
		"""Decodes boundary-delimited Morse code.

		This method is intended for Morse where character boundaries are
		already known.

		Args:
			value: Spaced Morse representation.

		Returns:
			The decoded text.

		Example:
			morse.decode(".... . .-.. .-.. ---")
			# "HELLO"
		"""
		stream = self.spaced_parser.parse(value)

		return self.decoder.decode(stream)

	def parse(self, value: str) -> MorseStream:
		"""Parses spaced Morse into a MorseStream.

		This exposes the structured representation for users who need
		lower-level control.
		"""
		return self.spaced_parser.parse(value)

	def parse_unspaced(self, value: str) -> MorseSequence:
		"""Parses continuous Morse into a MorseSequence."""
		return self.unspaced_parser.parse(value)

	def solve(
		self,
		value: str,
		dictionary: MorseDictionary | Iterable[str] | None = None,
		scorer: MorseScorer | None = None,
		max_word_length: int | None = None,
		beam_width: int | None = None,
	) -> MorseCandidate | None:
		"""Solves an unspaced Morse sequence into its most likely text.

		Unlike ``decode()``, this method has to infer character and word
		boundaries.

		Args:
			value: Continuous Morse representation.
			dictionary: Dictionary or iterable of english words.
			scorer: Optional scoring strategy.
			        Defaults to DictionaryScorer.
			max_word_length: Maximum dictionary word length.
			beam_width: Beam width for contextual scorers.

		Returns:
			The best candidate, or None if no solution exists.

		Example:
			result = morse.solve(
				"......-...-..----......-..",
				["hello", "world"],
			)

			print(result.text)
		"""

		sequence = self.parse_unspaced(value)

		active_dictionary = dictionary or self.word_dictionary

		if active_dictionary is None:
			raise ValueError("A dictionary is required to solve unspaced Morse")

		if not isinstance(active_dictionary, MorseDictionary):
			active_dictionary = MorseDictionary(active_dictionary)

		active_scorer = scorer or self.scorer

		if active_scorer is None:
			active_scorer = DictionaryScorer(active_dictionary)

		solver = MorseSolver(
			self.alphabet,
			active_dictionary,
			active_scorer,
			max_word_length=(
				max_word_length
				if max_word_length is not None
				else self.max_word_length
			),
			beam_width=(
				beam_width if beam_width is not None else self.beam_width
			),
		)

		return solver.solve(sequence)

	def solve_candidates(
		self,
		value: str,
		dictionary: MorseDictionary | Iterable[str] | None = None,
		scorer: MorseScorer | None = None,
		max_word_length: int | None = None,
		beam_width: int | None = None,
		limit: int = 10,
	) -> list[MorseCandidate]:
		"""Returns ranked candidates for an unspaced Morse sequence.

		Args:
			value: Continuous Morse representation.
			dictionary: Dictionary or iterable of English words.
			scorer: Optional scoring strategy.
			        Defaults to DictionaryScorer.
			max_word_length: Maximum dictionary word length.
			beam_width: Beam width for contextual scorers.
			limit: Maximum number of ranked candidates to return.

		Returns:
			A list of ranked MorseCandidate objects, up to ``limit``.

		Raises:
			ValueError: If no dictionary is provided or candidate limit is < 1.
		"""
		sequence = self.parse_unspaced(value)

		active_dictionary = dictionary or self.word_dictionary

		if active_dictionary is None:
			raise ValueError("A dictionary is required to solve unspaced Morse")

		if not isinstance(active_dictionary, MorseDictionary):
			active_dictionary = MorseDictionary(active_dictionary)

		active_scorer = scorer or self.scorer

		if active_scorer is None:
			active_scorer = DictionaryScorer(active_dictionary)

		solver = MorseSolver(
			self.alphabet,
			active_dictionary,
			active_scorer,
			max_word_length=(
				max_word_length
				if max_word_length is not None
				else self.max_word_length
			),
			beam_width=(
				beam_width if beam_width is not None else self.beam_width
			),
		)

		return solver.solve_candidates(
			sequence,
			limit=limit,
		)

	def dictionary(
		self,
		words: Iterable[str],
	) -> MorseDictionary:
		"""Creates a MorseDictionary using this toolkit's conventions."""
		return MorseDictionary(words)

	def frequency_scorer(
		self,
		frequencies: Mapping[str, float],
		default_score: float = 0.0,
	) -> FrequencyScorer:
		"""Creates a FrequencyScorer."""
		return FrequencyScorer(
			frequencies,
			default_score=default_score,
		)

	def bigram_scorer(
		self,
		transitions: Mapping[tuple[str, str], float],
		default_score: float = 0.0,
	) -> BigramScorer:
		"""Creates a BigramScorer."""
		return BigramScorer(
			transitions,
			default_score=default_score,
		)

	def _format_stream(
		self,
		stream: MorseStream,
	) -> str:
		"""Converts a MorseStream into its configured textual representation."""
		parts: list[str] = []

		for token in stream:
			if token.type is MorseTokenType.SYMBOL:
				if token.symbol is None:
					raise ValueError("Symbol token is missing a Morse symbol")

				parts.append(self.representation.encode(token.symbol))
				continue

			if token.type is MorseTokenType.CHARACTER_BOUNDARY:
				parts.append(self.boundaries.character_boundary)
				continue

			if token.type is MorseTokenType.WORD_BOUNDARY:
				parts.append(self.boundaries.word_boundary)
				continue

			raise ValueError(f"Unknown Morse token type: {token.type!r}")

		return "".join(parts)
