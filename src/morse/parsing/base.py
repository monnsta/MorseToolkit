from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class MorseParser(ABC, Generic[T]):
	"""Abstract base class for Morse string parsers."""

	@abstractmethod
	def parse(self, value: str) -> T:
		"""Parses a string into a target Morse structure.

		Args:
			value: The string value to parse.

		Returns:
			The parsed result of generic type T.
		"""
		raise NotImplementedError
