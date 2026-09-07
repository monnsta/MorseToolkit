from morse.core import MorseSequence
from morse.representations import MorseRepresentation

from .base import MorseParser


class UnspacedParser(MorseParser[MorseSequence]):
	def __init__(
		self,
		representation: MorseRepresentation,
	) -> None:
		self.representation = representation

	def parse(self, value: str) -> MorseSequence:
		symbols = self.representation.decode_sequence(value)

		return MorseSequence.from_symbols(symbols)
