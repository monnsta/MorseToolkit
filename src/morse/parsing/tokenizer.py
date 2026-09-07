from dataclasses import dataclass
from enum import Enum, auto

from .boundaries import MorseBoundarySyntax


class TokenType(Enum):
	"""Categorizes parsed tokens from raw Morse input strings.

	Attributes:
		VALUE: An active signal sequence (dots/dashes).
		CHARACTER_BOUNDARY: A separator between characters.
		WORD_BOUNDARY: A separator between words.
	"""
	VALUE = auto()
	CHARACTER_BOUNDARY = auto()
	WORD_BOUNDARY = auto()


@dataclass(frozen=True, slots=True)
class RawToken:
	"""A raw parsed segment of a Morse string before symbol decoding.

	Attributes:
		type: The categorization of the raw token.
		value: The string chunk extracted from the input.
	"""
	type: TokenType
	value: str


class MorseTokenizer:
	"""Splits string input into raw boundary and value tokens."""

	def __init__(
		self,
		boundaries: MorseBoundarySyntax | None = None,
	) -> None:
		"""Initializes the tokenizer with specific boundary configurations.

		Args:
			boundaries: Boundary syntax settings. Defaults to standard spaces.
		"""
		self.boundaries = boundaries or MorseBoundarySyntax()

	def tokenize(self, value: str) -> tuple[RawToken, ...]:
		"""Scans a string and segments it into raw tokens based on boundaries.

		Args:
			value: The input string to scan.

		Returns:
			A tuple of ordered RawToken instances.
		"""
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
