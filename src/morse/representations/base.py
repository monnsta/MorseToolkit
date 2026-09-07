from abc import ABC, abstractmethod

from morse.core import MorseSymbol


class MorseRepresentation(ABC):
	"""Abstract base class defining custom string serialization for MorseSymbol objects."""

	@abstractmethod
	def encode(self, symbol: MorseSymbol) -> str:
		"""Serializes a MorseSymbol into its string representation.

		Args:
			symbol: The target MorseSymbol instance.

		Returns:
			The custom string representation of the symbol.

		Raises:
			NotImplementedError: Must be implemented by subclasses.
		"""
		raise NotImplementedError

	@abstractmethod
	def decode(self, value: str) -> MorseSymbol:
		"""Deserializes a custom string value into a corresponding MorseSymbol.

		Args:
			value: The string representation to decode.

		Returns:
			The decoded MorseSymbol instance.

		Raises:
			NotImplementedError: Must be implemented by subclasses.
		"""
		raise NotImplementedError

	@abstractmethod
	def decode_sequence(self, value: str) -> tuple[MorseSymbol, ...]:
		"""Deserializes a string representing multiple symbols into a tuple of MorseSymbols.

		Args:
			value: The sequence string representation to decode.

		Returns:
			A tuple of decoded MorseSymbol instances.

		Raises:
			NotImplementedError: Must be implemented by subclasses.
		"""
		raise NotImplementedError

	@abstractmethod
	def can_decode(self, value: str) -> bool:
		"""Checks whether a given string value can be decoded.

		Args:
			value: The string representation to evaluate.

		Returns:
			True if the string value is valid, False otherwise.
		"""
		raise NotImplementedError

