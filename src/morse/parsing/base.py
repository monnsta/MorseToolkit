from abc import ABC, abstractmethod
from typing import Generic, TypeVar


T = TypeVar("T")


class MorseParser(ABC, Generic[T]):
	@abstractmethod
	def parse(self, value: str) -> T:
		raise NotImplementedError
