from morse.core import MorseStream, MorseToken
from morse.representations import MorseRepresentation

from .base import MorseParser
from .boundaries import MorseBoundarySyntax
from .tokenizer import MorseTokenizer, TokenType


class SpacedParser(MorseParser[MorseStream]):
	def __init__(
		self,
		representation: MorseRepresentation,
		boundaries: MorseBoundarySyntax | None = None,
		tokenizer: MorseTokenizer | None = None,
	) -> None:
		self.representation = representation
		self.boundaries = boundaries or MorseBoundarySyntax()
		self.tokenizer = tokenizer or MorseTokenizer(self.boundaries)

	def parse(self, value: str) -> MorseStream:
		raw_tokens = self.tokenizer.tokenize(value)
		tokens: list[MorseToken] = []

		for raw_token in raw_tokens:
			if raw_token.type is TokenType.CHARACTER_BOUNDARY:
				tokens.append(
					MorseToken.character_boundary()
				)
				continue

			if raw_token.type is TokenType.WORD_BOUNDARY:
				tokens.append(
					MorseToken.word_boundary()
				)
				continue

			if raw_token.type is not TokenType.VALUE:
				raise ValueError(
					f"Unknown raw token type: {raw_token.type!r}"
				)

			symbols = self.representation.decode_sequence(
				raw_token.value
			)

			tokens.extend(
				MorseToken.symbol_token(symbol)
				for symbol in symbols
			)

		return MorseStream.from_tokens(iter(tokens))
