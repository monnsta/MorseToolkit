from morse.core import MorseStream, MorseToken
from morse.representations import MorseRepresentation

from .base import MorseParser
from .boundaries import MorseBoundarySyntax
from .tokenizer import MorseTokenizer, TokenType


class SpacedParser(MorseParser[MorseStream]):
	"""Parses boundary-delimited string representations into a fully structured MorseStream."""

	def __init__(
		self,
		representation: MorseRepresentation,
		boundaries: MorseBoundarySyntax | None = None,
		tokenizer: MorseTokenizer | None = None,
	) -> None:
		"""Initializes the spaced parser.

		Args:
			representation: Decoder for translating values into symbols.
			boundaries: Optional custom boundary syntax definition.
			tokenizer: Optional custom tokenizer instance.
		"""
		self.representation = representation
		self.boundaries = boundaries or MorseBoundarySyntax()
		self.tokenizer = tokenizer or MorseTokenizer(self.boundaries)

	def parse(self, value: str) -> MorseStream:
		"""Tokenizes and parses a delimited string into a Morse stream.

		Args:
			value: The spaced Morse string input.

		Returns:
			A fully constructed MorseStream with discrete symbol, character, and word tokens.

		Raises:
			ValueError: If an unexpected raw token type is encountered or if sequence decoding fails.
		"""
		raw_tokens = self.tokenizer.tokenize(value)
		tokens: list[MorseToken] = []

		for raw_token in raw_tokens:
			if raw_token.type is TokenType.CHARACTER_BOUNDARY:
				tokens.append(MorseToken.character_boundary())
				continue

			if raw_token.type is TokenType.WORD_BOUNDARY:
				tokens.append(MorseToken.word_boundary())
				continue

			if raw_token.type is not TokenType.VALUE:
				raise ValueError(f"Unknown raw token type: {raw_token.type!r}")

			symbols = self.representation.decode_sequence(raw_token.value)

			tokens.extend(MorseToken.symbol_token(symbol) for symbol in symbols)

		return MorseStream.from_tokens(iter(tokens))
