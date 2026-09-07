from morse.core import MorseSequence
from morse.representations import MorseRepresentation

from .base import MorseParser


class UnspacedParser(MorseParser[MorseSequence]):
	"""Parses continuous, unspaced string representations into a MorseSequence."""

	def __init__(
		self,
		representation: MorseRepresentation,
	) -> None:
		"""Initializes the parser with a specific string representation format.

		Args:
			representation: The MorseRepresentation used to decode string chunks into symbols.
		"""
		self.representation = representation

	def parse(self, value: str) -> MorseSequence:
		"""Decodes a continuous string of symbols directly into a sequence.

		Args:
			value: A string without boundary spaces or separators.

		Returns:
			A MorseSequence container populated with the decoded symbols.
		"""
		symbols = self.representation.decode_sequence(value)

		return MorseSequence.from_symbols(symbols)
