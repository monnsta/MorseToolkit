from dataclasses import dataclass
from enum import Enum, auto

from .symbols import MorseSymbol


class MorseTokenType(Enum):
	"""Types of stream units within encoded Morse signals.

	Attributes:
		SYMBOL: Represents an active Morse symbol (DOT or DASH).
		CHARACTER_BOUNDARY: Indicates separation between characters.
		WORD_BOUNDARY: Indicates separation between words.
	"""

	SYMBOL = auto()
	CHARACTER_BOUNDARY = auto()
	WORD_BOUNDARY = auto()


@dataclass(frozen=True, slots=True)
class MorseToken:
	"""Individual atomic unit within a Morse stream sequence.

	Attributes:
		type: Category of the stream token.
		symbol: Associated MorseSymbol value if type is SYMBOL, otherwise None.
	"""

	type: MorseTokenType
	symbol: MorseSymbol | None = None

	@classmethod
	def symbol_token(cls, symbol: MorseSymbol) -> "MorseToken":
		"""Creates a symbol token container for a specific MorseSymbol.

		Args:
			symbol: The target MorseSymbol instance.

		Returns:
			A MorseToken configured as a SYMBOL type.
		"""
		return cls(
			type=MorseTokenType.SYMBOL,
			symbol=symbol,
		)

	@classmethod
	def character_boundary(cls) -> "MorseToken":
		"""Creates a character boundary marker token.

		Returns:
			A MorseToken configured as CHARACTER_BOUNDARY.
		"""
		return cls(type=MorseTokenType.CHARACTER_BOUNDARY)

	@classmethod
	def word_boundary(cls) -> "MorseToken":
		"""Creates a word boundary marker token.

		Returns:
			A MorseToken configured as WORD_BOUNDARY.
		"""
		return cls(type=MorseTokenType.WORD_BOUNDARY)
