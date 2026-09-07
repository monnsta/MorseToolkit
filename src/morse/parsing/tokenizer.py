from dataclasses import dataclass
from enum import Enum, auto

from .boundaries import MorseBoundarySyntax


class TokenType(Enum):
	VALUE = auto()
	CHARACTER_BOUNDARY = auto()
	WORD_BOUNDARY = auto()


@dataclass(frozen=True, slots=True)
class RawToken:
	type: TokenType
	value: str


class MorseTokenizer:
	def __init__(
		self,
		boundaries: MorseBoundarySyntax | None = None,
	) -> None:
		self.boundaries = boundaries or MorseBoundarySyntax()

	def tokenize(self, value: str) -> tuple[RawToken, ...]:
		tokens: list[RawToken] = []
		position = 0

		while position < len(value):
			if value.startswith(
				self.boundaries.word_boundary,
				position,
			):
				tokens.append(
					RawToken(
						type=TokenType.WORD_BOUNDARY,
						value=self.boundaries.word_boundary,
					)
				)
				position += len(self.boundaries.word_boundary)
				continue

			if value.startswith(
				self.boundaries.character_boundary,
				position,
			):
				tokens.append(
					RawToken(
						type=TokenType.CHARACTER_BOUNDARY,
						value=self.boundaries.character_boundary,
					)
				)
				position += len(self.boundaries.character_boundary)
				continue

			start = position

			while position < len(value):
				if value.startswith(
					self.boundaries.word_boundary,
					position,
				):
					break

				if value.startswith(
					self.boundaries.character_boundary,
					position,
				):
					break

				position += 1

			tokens.append(
				RawToken(
					type=TokenType.VALUE,
					value=value[start:position],
				)
			)

		return tuple(tokens)
