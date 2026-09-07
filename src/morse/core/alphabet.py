from abc import ABC, abstractmethod
from collections.abc import Sequence

from .symbols import MorseSymbol


class MorseAlphabet(ABC):
	"""Abstract base class defining translation mapping interface between characters and Morse symbols."""

	@abstractmethod
	def encode(self, character: str) -> tuple[MorseSymbol, ...]:
		"""Encodes a single character into a sequence of Morse symbols.

		Args:
			character: The text character to encode.

		Returns:
			A tuple of MorseSymbol objects representing the character.

		Raises:
			NotImplementedError: Must be implemented by subclasses.
		"""
		raise NotImplementedError

	@abstractmethod
	def decode(self, symbols: Sequence[MorseSymbol]) -> str:
		"""Decodes a sequence of Morse symbols into a single text character.

		Args:
			symbols: A sequence of MorseSymbol instances.

		Returns:
			The decoded string character.

		Raises:
			NotImplementedError: Must be implemented by subclasses.
		"""
		raise NotImplementedError

	@abstractmethod
	def can_encode(self, character: str) -> bool:
		"""Checks whether a character is supported by this alphabet instance.

		Args:
			character: The text character to check.

		Returns:
			True if character can be encoded, False otherwise.
		"""
		raise NotImplementedError

	@abstractmethod
	def can_decode(self, symbols: Sequence[MorseSymbol]) -> bool:
		"""Checks whether a sequence of Morse symbols maps to a valid character.

		Args:
			symbols: A sequence of MorseSymbol instances to evaluate.

		Returns:
			True if symbols can be decoded, False otherwise.
		"""
		raise NotImplementedError
