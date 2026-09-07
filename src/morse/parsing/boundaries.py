from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MorseBoundarySyntax:
	"""Defines how character and word boundaries are represented in Morse input."""

	character_boundary: str = " "
	word_boundary: str = "   "

	def __post_init__(self) -> None:
		if not self.character_boundary:
			raise ValueError("Character boundary cannot be empty")

		if not self.word_boundary:
			raise ValueError("Word boundary cannot be empty")

		if self.character_boundary == self.word_boundary:
			raise ValueError(
				"Character and word boundaries must be different"
			)
