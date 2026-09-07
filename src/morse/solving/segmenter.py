from collections.abc import Iterator

from morse.core import (
	MorseAlphabet,
	MorseSegmentation,
	MorseSequence,
	MorseSymbol,
)


class MorseSegmenter:
	def __init__(
		self,
		alphabet: MorseAlphabet,
		max_character_length: int = 6,
	) -> None:
		if max_character_length < 1:
			raise ValueError(
				"Maximum character length must be at least 1"
			)

		self.alphabet = alphabet
		self.max_character_length = max_character_length

	def segment(
		self,
		sequence: MorseSequence,
	) -> Iterator[MorseSegmentation]:
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
