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
	"""Internal state representing one possible decoding path."""

	score: float
	context: tuple[str, ...]
	word: str | None
	previous: "_SolverState | None"


class MorseSolver:
	"""Resolves unspaced Morse sequences into optimal text candidates.

	Uses a trie-backed dictionary index and dynamic programming.

	Context-independent scorers use a single best state per Morse position.

	Context-aware scorers use a bounded beam of states per Morse position so
	that different linguistic contexts can survive long enough to influence
	future decisions.
	"""

	def __init__(
		self,
		alphabet: MorseAlphabet,
		dictionary: MorseDictionary,
		scorer: MorseScorer,
		max_word_length: int = 32,
		beam_width: int = 8,
	) -> None:
		"""Initializes the solver.

		Args:
			alphabet: The alphabet to use for character mapping.
			dictionary: Dictionary of valid target words.
			scorer: Scoring algorithm to evaluate word candidates.
			max_word_length: Limit on text word character count to optimize trie traversal.
			beam_width: Maximum number of competing contextual states retained
				at each Morse position.

		Raises:
			ValueError: If max_word_length or beam_width is less than 1.
		"""
		if max_word_length < 1:
			raise ValueError(
				"Maximum word length must be at least 1"
			)

		if beam_width < 1:
			raise ValueError(
				"Beam width must be at least 1"
			)

		self.alphabet = alphabet
		self.dictionary = dictionary
		self.scorer = scorer
		self.max_word_length = max_word_length
		self.beam_width = beam_width

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

		if self.scorer.context_size == 0:
			return self._solve_without_context(sequence)

		return self._solve_with_context(sequence)

	def _solve_without_context(
		self,
		sequence: MorseSequence,
	) -> MorseCandidate | None:
		"""Solves using one optimal state per Morse position."""

		best: list[_SolverState | None] = [
			None
		] * (len(sequence) + 1)

		best[0] = _SolverState(
			score=0.0,
			context=(),
			word=None,
			previous=None,
		)

		for position in range(len(sequence)):
			current = best[position]

			if current is None:
				continue

			for match in self._matches(sequence, position):
				score = current.score + self.scorer.score(
					match.word,
					(),
				)

				candidate = _SolverState(
					score=score,
					context=(),
					word=match.word,
					previous=current,
				)

				previous = best[match.end]

				if (
					previous is None
					or candidate.score > previous.score
				):
					best[match.end] = candidate

		return self._candidate_from_state(best[-1])

	def _solve_with_context(
		self,
		sequence: MorseSequence,
	) -> MorseCandidate | None:
		"""Solves using a bounded beam of contextual states per position."""

		states: list[list[_SolverState]] = [
			[]
			for _ in range(len(sequence) + 1)
		]

		states[0].append(
			_SolverState(
				score=0.0,
				context=(),
				word=None,
				previous=None,
			)
		)

		for position in range(len(sequence)):
			if not states[position]:
				continue

			matches = tuple(
				self._matches(sequence, position)
			)

			for current in states[position]:
				for match in matches:
					score = current.score + self.scorer.score(
						match.word,
						current.context,
					)

					candidate = _SolverState(
						score=score,
						context=self._next_context(
							current.context,
							match.word,
						),
						word=match.word,
						previous=current,
					)

					states[match.end].append(candidate)

			for end in range(position + 1, len(sequence) + 1):
				if len(states[end]) > self.beam_width * 2:
					states[end] = self._prune_states(
						states[end]
					)

		if not states[-1]:
			return None

		best = max(
			states[-1],
			key=lambda state: state.score,
		)

		return self._candidate_from_state(best)

	def _prune_states(
		self,
		states: list[_SolverState],
	) -> list[_SolverState]:
		"""Retains only the highest-scoring contextual states."""

		best_by_context: dict[
			tuple[str, ...],
			_SolverState,
		] = {}

		for state in states:
			previous = best_by_context.get(state.context)

			if (
				previous is None
				or state.score > previous.score
			):
				best_by_context[state.context] = state

		return sorted(
			best_by_context.values(),
			key=lambda state: state.score,
			reverse=True,
		)[:self.beam_width]

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

	def _candidate_from_state(
		self,
		state: _SolverState | None,
	) -> MorseCandidate | None:
		"""Reconstructs a public candidate from a terminal solver state."""

		if state is None:
			return None

		words: list[str] = []
		current = state

		while current.word is not None:
			words.append(current.word)

			if current.previous is None:
				break

			current = current.previous

		words.reverse()

		return MorseCandidate(
			text=" ".join(words),
			score=state.score,
		)
