from collections.abc import Mapping

from morse.core.symbols import MorseSymbol

from .base import MorseRepresentation


class ArbitraryRepresentation(MorseRepresentation):
	"""Configurable string representation supporting custom mappings for Morse symbols."""

	def __init__(
		self,
		mapping: Mapping[MorseSymbol, str],
	) -> None:
		"""Initializes the custom representation using a mapping table.

		Args:
			mapping: Mapping containing entries for both MorseSymbol.DOT and MorseSymbol.DASH.

		Raises:
			ValueError: If DOT or DASH key is missing, representations are empty,
			            identical, or one representation is a prefix of the other.
		"""
		self._mapping = dict(mapping)

		if MorseSymbol.DOT not in self._mapping:
			raise ValueError("Representation must define DOT")

		if MorseSymbol.DASH not in self._mapping:
			raise ValueError("Representation must define DASH")

		values = tuple(self._mapping.values())

		if any(not value for value in values):
			raise ValueError(
				"Symbol representations cannot be empty"
			)

		if len(set(values)) != len(values):
			raise ValueError(
				"Dot and dash representations must be different"
			)

		for first in values:
			for second in values:
				if first != second and second.startswith(first):
					raise ValueError(
						"Symbol representations cannot be prefixes of each other"
					)

		self._reverse_mapping = {
			value: symbol
			for symbol, value in self._mapping.items()
		}

	def encode(self, symbol: MorseSymbol) -> str:
		"""Encodes a MorseSymbol into its mapped custom string representation.

		Args:
			symbol: The target MorseSymbol instance.

		Returns:
			The mapped string value for the given symbol.
		"""
		return self._mapping[symbol]

	def decode(self, value: str) -> MorseSymbol:
		"""Decodes a custom string value back into its MorseSymbol equivalent.

		Args:
			value: The custom string value to decode.

		Returns:
			The corresponding MorseSymbol instance.

		Raises:
			ValueError: If the string value does not match any configured symbol representation.
		"""
		try:
			return self._reverse_mapping[value]
		except KeyError as exc:
			raise ValueError(
				f"Invalid Morse representation: {value!r}"
			) from exc

	def decode_sequence(self, value: str) -> tuple[MorseSymbol, ...]:
		"""Parses and decodes a continuous sequence string of custom representations.

		Args:
			value: The sequence string representation to decode.

		Returns:
			A tuple of decoded MorseSymbol instances.

		Raises:
			ValueError: If an unrecognized token sequence is encountered at any position.
		"""
		symbols: list[MorseSymbol] = []
		position = 0

		while position < len(value):
			for representation, symbol in self._reverse_mapping.items():
				if value.startswith(representation, position):
					symbols.append(symbol)
					position += len(representation)
					break
			else:
				raise ValueError(
					f"Invalid Morse representation at position "
					f"{position}: {value[position:]!r}"
				)

		return tuple(symbols)

	def can_decode(self, value: str) -> bool:
		"""Checks whether a given string value matches a configured symbol representation.

		Args:
			value: The string representation to evaluate.

		Returns:
			True if value exists in reverse lookup table, False otherwise.
		"""
		return value in self._reverse_mapping
