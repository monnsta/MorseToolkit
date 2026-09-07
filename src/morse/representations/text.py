from morse.core import MorseSymbol

from .base import MorseRepresentation


class TextRepresentation(MorseRepresentation):
	"""Standard text representation mapping DOT to '.' and DASH to '-'."""

	def encode(self, symbol: MorseSymbol) -> str:
		"""Encodes a MorseSymbol to standard text characters.

		Args:
			symbol: The target MorseSymbol instance.

		Returns:
			String literal '.' for DOT or '-' for DASH.
		"""
		return symbol.value

	def decode(self, value: str) -> MorseSymbol:
		"""Decodes standard dot/dash characters to a MorseSymbol.

		Args:
			value: The string literal to decode.

		Returns:
			The matching MorseSymbol instance.

		Raises:
			ValueError: If value is not '.' or '-'.
		"""
		if value == ".":
			return MorseSymbol.DOT

		if value == "-":
			return MorseSymbol.DASH

		raise ValueError(
			f"Invalid Morse representation: {value!r}"
		)

	def decode_sequence(self, value: str) -> tuple[MorseSymbol, ...]:
		"""Decodes a continuous string of '.' and '-' characters into a tuple of MorseSymbols.

		Args:
			value: String sequence composed of '.' and '-' characters.

		Returns:
			A tuple of decoded MorseSymbol instances.

		Raises:
			ValueError: If any character in the sequence is not '.' or '-'.
		"""
		return tuple(
			self.decode(character)
			for character in value
		)

	def can_decode(self, value: str) -> bool:
		"""Checks if a string is a standard Morse character.

		Args:
			value: The string literal to evaluate.

		Returns:
			True if value is '.' or '-', False otherwise.
		"""
		return value in {".", "-"}
