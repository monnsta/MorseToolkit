from abc import ABC, abstractmethod
from collections.abc import Mapping

from morse.solving.dictionary import MorseDictionary


class MorseScorer(ABC):
	@property
	@abstractmethod
	def context_size(self) -> int:
		raise NotImplementedError

	@abstractmethod
	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		raise NotImplementedError


class DictionaryScorer(MorseScorer):
	def __init__(self, dictionary: MorseDictionary) -> None:
		self.dictionary = dictionary

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		return 1.0 if self.dictionary.contains(word) else 0.0

	@property
	def context_size(self) -> int:
		return 0


class FrequencyScorer(MorseScorer):
	def __init__(
		self,
		frequencies: Mapping[str, float],
		default_score: float = 0.0,
	) -> None:
		if default_score < 0.0:
			raise ValueError(
				"Default score cannot be negative"
			)

		self._frequencies = {
			word.strip().lower(): score
			for word, score in frequencies.items()
			if word.strip()
		}
		self._default_score = default_score

		if any(score < 0.0 for score in self._frequencies.values()):
			raise ValueError(
				"Word frequencies cannot be negative"
			)

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		return self._frequencies.get(
			word.strip().lower(),
			self._default_score,
		)

	@property
	def context_size(self) -> int:
		return 0
