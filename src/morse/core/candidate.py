from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MorseCandidate:
	"""Represents a potential decoding candidate with confidence scoring.

	Attributes:
		text: Decoded text representation.
		score: Probability or score assigned to this candidate solution.
	"""

	text: str
	score: float
