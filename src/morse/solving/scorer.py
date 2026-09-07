from abc import ABC, abstractmethod
from collections.abc import Mapping

from morse.solving.dictionary import MorseDictionary


class MorseScorer(ABC):
	"""Abstract base class for evaluating the likelihood of candidate words."""

	@property
	@abstractmethod
	def context_size(self) -> int:
		"""Defines how many previous words this scorer needs for context.

		Returns:
			The integer number of previous words required.
		"""
		raise NotImplementedError

	@abstractmethod
	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		"""Assigns a score to a word given its surrounding context.

		Args:
			word: The target word to score.
			context: A tuple of preceding words, constrained by context_size.

		Returns:
			A float representing the assigned score (higher is better).
		"""
		raise NotImplementedError


class DictionaryScorer(MorseScorer):
	"""Scores words strictly based on their presence in a dictionary without context."""

	def __init__(self, dictionary: MorseDictionary) -> None:
		"""Initializes the scorer with a MorseDictionary.

		Args:
			dictionary: The dictionary to check words against.
		"""
		self.dictionary = dictionary

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		"""Scores the word by checking dictionary inclusion.

		Args:
			word: The word to evaluate.
			context: Ignored by this scorer.

		Returns:
			1.0 if the word is in the dictionary, 0.0 otherwise.
		"""
		_ = context
		return 1.0 if self.dictionary.contains(word) else 0.0

	@property
	def context_size(self) -> int:
		"""Context size for DictionaryScorer is 0."""
		return 0


class FrequencyScorer(MorseScorer):
	"""Scores words based on predefined frequency weights to favor common vocabulary."""

	def __init__(
		self,
		frequencies: Mapping[str, float],
		default_score: float = 0.0,
	) -> None:
		"""Initializes the frequency scorer.

		Args:
			frequencies: A mapping of lowercase words to their positive float scores.
			default_score: Score to assign if a word is missing from the mapping.

		Raises:
			ValueError: If default_score or any frequency values are negative.
		"""
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
		"""Looks up the assigned frequency score of a word.

		Args:
			word: The word to evaluate.
			context: Ignored by this scorer.

		Returns:
			The specific frequency score for the word, or the default score.
		"""
		_ = context
		return self._frequencies.get(
			word.strip().lower(),
			self._default_score,
		)

	@property
	def context_size(self) -> int:
		"""Context size for FrequencyScorer is 0."""
		return 0
