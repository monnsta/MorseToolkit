from collections.abc import Iterator
from dataclasses import dataclass

from morse.core import MorseAlphabet, MorseCandidate, MorseSequence, MorseSymbol
from morse.solving.dictionary import MorseDictionary
from morse.solving.index import MorseWordIndex
from morse.solving.scorer import MorseScorer


@dataclass(frozen=True, slots=True)
class _WordMatch:
	"""Internal record of a successful word match and its score."""
	word: str
	end: int
	score: float


@dataclass(frozen=True, slots=True)
class _SolverState:
	"""Internal state container tracking DP path scores during solving."""
	text: str
	score: float
	context: tuple[str, ...]


class MorseSolver:
	"""Resolves unspaced Morse sequences into optimal text candidates.

	Uses dynamic programming and a trie-based dictionary index to find the 
	highest-scoring sequence of valid words.
	"""

	def __init__(
		self,
		alphabet: MorseAlphabet,
		dictionary: MorseDictionary,
		scorer: MorseScorer,
		max_word_length: int = 32,
	) -> None:
		"""Initializes the solver.

		Args:
			alphabet: The alphabet to use for character mapping.
			dictionary: Dictionary of valid target words.
			scorer: Scoring algorithm to evaluate word candidates.
			max_word_length: Limit on text word character count to optimize trie traversal.

		Raises:
			ValueError: If max_word_length is less than 1.
		"""
		if max_word_length < 1:
			raise ValueError(
				"Maximum word length must be at least 1"
			)

		self.alphabet = alphabet
		self.dictionary = dictionary
		self.scorer = scorer
		self.max_word_length = max_word_length

		self._word_index = MorseWordIndex(
			self._build_word_codes()
		)

	def _build_word_codes(
		self,
	) -> Iterator[
		tuple[str, tuple[MorseSymbol, ...]]
	]:
		"""Encodes dictionary words into valid symbol sequences for trie indexing."""
		for word in self.dictionary.words():
			symbols: list[MorseSymbol] = []

			try:
				for character in word:
					symbols.extend(
						self.alphabet.encode(character)
					)
			except ValueError:
				continue

			if not symbols:
				continue

			yield word, tuple(symbols)

	def solve(
		self,
		sequence: MorseSequence,
	) -> MorseCandidate | None:
		"""Finds the most likely sentence/phrase for a continuous Morse sequence.

		Args:
			sequence: The continuous MorseSequence to decrypt.

		Returns:
			A MorseCandidate representing the best scoring text match, or None if unsolvable.
		"""
		if not sequence:
			return MorseCandidate("", 0.0)

		best: list[_SolverState | None] = [
			None
		] * (len(sequence) + 1)

		best[0] = _SolverState(
			text="",
			score=0.0,
			context=()
		)

		for position in range(len(sequence)):
			current = best[position]

			if current is None:
				continue

			for match in self._matches(sequence, position):
				score = self.scorer.score(
					match.word,
					current.context,
				)

				candidate_text = (
					match.word
					if not current.text
					else f"{current.text} {match.word}"
				)

				candidate = _SolverState(
					text=candidate_text,
					score=current.score + score,
					context=self._next_context(
						current.context,
						match.word,
					),
				)

				previous = best[match.end]

				if (
					previous is None
					or candidate.score > previous.score
				):
					best[match.end] = candidate

		result = best[-1]

		if result is None:
			return None

		return MorseCandidate(
			text=result.text,
			score=result.score,
		)

	def _matches(
		self,
		sequence: MorseSequence,
		position: int,
	) -> Iterator[_WordMatch]:
		"""Yields all matching words starting at the given position."""
		for match in self._word_index.matches(
			sequence.symbols,
			position,
			self.max_word_length,
		):
			yield _WordMatch(
				word=match.word,
				end=match.end,
				score=self.scorer.score(match.word),
			)

	def _next_context(
		self,
		context: tuple[str, ...],
		word: str,
	) -> tuple[str, ...]:
		"""Updates trailing word context bounds based on the scorer's configuration."""
		size = self.scorer.context_size

		if size == 0:
			return ()

		return (
			*context,
			word,
		)[-size:]
