from collections.abc import Iterator

from morse.core import (
	MorseAlphabet,
	MorseSegmentation,
	MorseSequence,
	MorseSymbol,
)


class MorseSegmenter:
	"""Splits continuous Morse sequences into valid character segmentations."""

	def __init__(
		self,
		alphabet: MorseAlphabet,
		max_character_length: int = 6,
	) -> None:
		"""Initializes the segmenter.

		Args:
			alphabet: The alphabet used to validate potential character symbol sequences.
			max_character_length: Maximum allowed symbols per individual character.

		Raises:
			ValueError: If max_character_length is less than 1.
		"""
		if max_character_length < 1:
			raise ValueError("Maximum character length must be at least 1")

		self.alphabet = alphabet
		self.max_character_length = max_character_length

	def segment(
		self,
		sequence: MorseSequence,
	) -> Iterator[MorseSegmentation]:
		"""Generates all valid character segmentations for a given sequence.

		Args:
			sequence: The target Morse sequence to segment.

		Yields:
			Valid MorseSegmentation instances.
		"""
		if not sequence:
			yield MorseSegmentation(())
			return

		yield from self._segment_from(
			sequence,
			0,
			(),
		)

	def _segment_from(
		self,
		sequence: MorseSequence,
		position: int,
		characters: tuple[tuple[MorseSymbol, ...], ...],
	) -> Iterator[MorseSegmentation]:
		"""Recursively finds valid character segmentations from a given position."""
		if position == len(sequence):
			yield MorseSegmentation(characters)
			return

		end = min(
			position + self.max_character_length,
			len(sequence),
		)

		for next_position in range(position + 1, end + 1):
			symbols = sequence.symbols[position:next_position]

			if not self.alphabet.can_decode(symbols):
				continue

			yield from self._segment_from(
				sequence,
				next_position,
				(*characters, symbols),
			)
