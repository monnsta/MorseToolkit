from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping

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
			raise ValueError("Default score cannot be negative")

		self._frequencies = {
			word.strip().lower(): score
			for word, score in frequencies.items()
			if word.strip()
		}
		self._default_score = default_score

		if any(score < 0.0 for score in self._frequencies.values()):
			raise ValueError("Word frequencies cannot be negative")

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


class BigramScorer(MorseScorer):
	"""Scores words using optional previous-word transition weights.

	This scorer is intentionally small and deterministic. It does not try to
	model language; it simply allows callers to express preferences such as
	"new york" being preferable to "new cat".
	"""

	def __init__(
		self,
		transitions: Mapping[tuple[str, str], float],
		default_score: float = 0.0,
	) -> None:
		"""Initializes the bigram scorer.

		Args:
			transitions: A mapping of (previous_word, target_word) tuples to scores.
			default_score: Score to assign if a transition is missing from the mapping.

		Raises:
			ValueError: If default_score or any transition scores are negative.
		"""
		if default_score < 0.0:
			raise ValueError("Default score cannot be negative")

		self._transitions = {
			(
				previous.strip().lower(),
				word.strip().lower(),
			): score
			for (previous, word), score in transitions.items()
			if previous.strip() and word.strip()
		}
		self._default_score = default_score

		if any(score < 0.0 for score in self._transitions.values()):
			raise ValueError("Transition scores cannot be negative")

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		"""Scores the word given the preceding context word.

		Args:
			word: The target word to evaluate.
			context: A tuple containing preceding words.

		Returns:
			The score for the transition if context is present, or default score.
		"""
		normalized_word = word.strip().lower()

		if not context:
			return self._default_score

		previous = context[-1].strip().lower()

		return self._transitions.get(
			(previous, normalized_word),
			self._default_score,
		)

	@property
	def context_size(self) -> int:
		"""Context size for BigramScorer is 1."""
		return 1


class CallableFrequencyScorer(MorseScorer):
	"""Scores words using a caller-provided scoring function."""

	def __init__(
		self,
		frequency: Callable[[str], float],
	) -> None:
		"""Initializes the callable frequency scorer.

		Args:
			frequency: A callable returning a float frequency score for a given word.
		"""
		self._frequency = frequency

	def score(
		self,
		word: str,
		context: tuple[str, ...] = (),
	) -> float:
		"""Evaluates the candidate word via the frequency callback.

		Args:
			word: The target word to score.
			context: Ignored by this scorer.

		Returns:
			The computed frequency score returned by the provider.
		"""
		_ = context

		return self._frequency(word.strip().lower())

	@property
	def context_size(self) -> int:
		"""Context size for CallableFrequencyScorer is 0."""
		return 0


class EnglishFrequencyScorer(CallableFrequencyScorer):
	"""Scores English words using the optional ``wordfreq`` corpus.

	Zipf frequency is logarithmic. A Zipf value minus 9 is an additive
	log-probability-like score, meaning that multiple words naturally pay
	the probability cost of being separate words.
	"""

	def __init__(self) -> None:
		"""Initializes the English frequency scorer using wordfreq.

		Raises:
			ImportError: If the optional 'wordfreq' dependency is not installed.
		"""
		try:
			from wordfreq import zipf_frequency
		except ImportError as exc:
			raise ImportError(
				"EnglishFrequencyScorer requires the optional "
				"'wordfreq' package. Install it with "
				"'pip install wordfreq'."
			) from exc

		super().__init__(
			frequency=lambda word: zipf_frequency(word, "en") - 9.0,
		)
