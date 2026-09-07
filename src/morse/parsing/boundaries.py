from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MorseBoundarySyntax:
	"""Defines how character and word boundaries are represented in Morse input.

	Attributes:
		character_boundary: The string indicating separation between individual characters.
		word_boundary: The string indicating separation between complete words.
	"""

	character_boundary: str = " "
	word_boundary: str = "   "

	def __post_init__(self) -> None:
		"""Validates the boundaries to ensure they are valid and distinguishable.

		Raises:
			ValueError: If boundaries are empty strings or identical to each other.
		"""
		if not self.character_boundary:
			raise ValueError("Character boundary cannot be empty")

		if not self.word_boundary:
			raise ValueError("Word boundary cannot be empty")

		if self.character_boundary == self.word_boundary:
			raise ValueError(
				"Character and word boundaries must be different"
			)
