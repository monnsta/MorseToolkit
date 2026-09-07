from enum import Enum


class MorseSymbol(Enum):
	"""Fundamental Morse code signals.

	Attributes:
		DOT: Represents the short signal element (dit).
		DASH: Represents the long signal element (dah).
	"""

	DOT = "."
	DASH = "-"
