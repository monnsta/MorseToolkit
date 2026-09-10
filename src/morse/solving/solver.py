from collections.abc import Iterator
from dataclasses import dataclass

from morse.core import (
	MorseAlphabet,
	MorseCandidate,
	MorseSequence,
	MorseSymbol,
)
from morse.solving.dictionary import MorseDictionary
from morse.solving.index import MorseWordIndex, MorseWordMatch
from morse.solving.scorer import MorseScorer


@dataclass(frozen=True, slots=True)
class _SolverState:
	"""Internal state representing one possible decoding path."""

	score: float
	word_count: int
	context: tuple[str, ...]
	word: str | None
	previous: "_SolverState | None"


class MorseSolver:
	"""Resolves unspaced Morse sequences into ranked text candidates.

	Uses a compact integer-based dictionary index and dynamic programming.

	Context-independent scorers use a bounded set of states per Morse
	position. Context-aware scorers use a larger beam so that different
	linguistic contexts can survive long enough to influence future decisions.
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
			max_word_length: Limit on text word character count to optimize
				dictionary indexing and matching.
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

		self._character_codes: dict[
			str,
			tuple[int, int],
		] = {}

		self._word_index = MorseWordIndex()

		self._build_word_index()

	def _build_word_index(self) -> None:
		"""Builds the dictionary index using compact integer Morse codes.

		Each distinct character is encoded once and cached as a pair containing
		its raw Morse bits and symbol length. Dictionary words are then assembled
		directly into the integer representation used by ``MorseWordIndex``,
		avoiding intermediate ``MorseSymbol`` tuples and lists.
		"""
		character_codes = self._character_codes
		encode = self.alphabet.encode
		max_word_length = self.max_word_length
		index = self._word_index

		for word in self.dictionary.words():
			if len(word) > max_word_length:
				continue

			word_key = 1
			symbol_length = 0
			valid = True

			for character in word:
				code = character_codes.get(character)

				if code is None:
					try:
						symbols = encode(character)
					except ValueError:
						symbols = ()

					if symbols:
						bits = 0

						for symbol in symbols:
							bits <<= 1

							if symbol is MorseSymbol.DASH:
								bits |= 1

						code = (bits, len(symbols))
					else:
						code = (0, 0)

					character_codes[character] = code

				bits, length = code

				if length == 0:
					valid = False
					break

				word_key = (
					word_key << length
				) | bits

				symbol_length += length

			if valid and symbol_length:
				index.add_encoded(
					word,
					word_key,
					symbol_length,
				)

	def _build_word_codes(
		self,
	) -> Iterator[
		tuple[str, tuple[MorseSymbol, ...]]
	]:
		"""Encodes dictionary words as Morse symbol tuples.

		This compatibility helper retains the traditional symbol-based
		representation for callers that need it. The solver itself uses
		``_build_word_index()`` so dictionary indexing does not require
		intermediate symbol tuples.
		"""
		character_codes: dict[
			str,
			tuple[MorseSymbol, ...],
		] = {}
		encode = self.alphabet.encode
		max_word_length = self.max_word_length

		for word in self.dictionary.words():
			if len(word) > max_word_length:
				continue

			symbols: list[MorseSymbol] = []
			valid = True

			for character in word:
				code = character_codes.get(character)

				if code is None:
					try:
						code = encode(character)
					except ValueError:
						code = ()

					character_codes[character] = code

				if not code:
					valid = False
					break

				symbols.extend(code)

			if valid and symbols:
				yield word, tuple(symbols)

	def solve(
		self,
		sequence: MorseSequence,
	) -> MorseCandidate | None:
		"""Finds the most likely sentence or phrase for a continuous Morse sequence.

		Args:
			sequence: The continuous MorseSequence to decrypt.

		Returns:
			A MorseCandidate representing the best scoring text match, or None
			if unsolvable.
		"""
		candidates = self.solve_candidates(
			sequence,
			limit=1,
		)

		return candidates[0] if candidates else None

	def solve_candidates(
		self,
		sequence: MorseSequence,
		limit: int = 10,
	) -> list[MorseCandidate]:
		"""Returns up to ``limit`` ranked candidates for a continuous Morse sequence.

		Args:
			sequence: The continuous MorseSequence to decrypt.
			limit: Maximum number of candidate solutions to return.

		Returns:
			A list of ranked MorseCandidate solutions up to the requested limit.

		Raises:
			ValueError: If limit is less than 1.
		"""
		if limit < 1:
			raise ValueError(
				"Candidate limit must be at least 1"
			)

		if not sequence:
			return [
				MorseCandidate("", 0.0)
			]

		if self.scorer.context_size == 0:
			states = self._solve_without_context(
				sequence,
				limit,
			)
		else:
			states = self._solve_with_context(
				sequence,
				limit,
			)

		return [
			candidate
			for candidate in (
				self._candidate_from_state(state)
				for state in states
			)
			if candidate is not None
		]

	def _solve_without_context(
		self,
		sequence: MorseSequence,
		limit: int,
	) -> list[_SolverState]:
		"""Keeps the top N paths reaching each Morse position."""
		states: list[list[_SolverState]] = [
			[]
			for _ in range(len(sequence) + 1)
		]

		states[0].append(
			_SolverState(
				score=0.0,
				word_count=0,
				context=(),
				word=None,
				previous=None,
			)
		)

		for position in range(len(sequence)):
			current_states = states[position]

			if not current_states:
				continue

			matches = tuple(
				self._matches(
					sequence,
					position,
				)
			)

			for current in current_states:
				for match in matches:
					candidate = self._extend(
						current,
						match.word,
						(),
					)

					target = states[match.end]
					target.append(candidate)

					if len(target) > limit:
						states[match.end] = self._rank_states(
							target,
							limit,
						)

		return self._rank_states(
			states[-1],
			limit,
		)

	def _solve_with_context(
		self,
		sequence: MorseSequence,
		limit: int,
	) -> list[_SolverState]:
		"""Keeps a bounded set of top contextual paths per position."""
		states: list[list[_SolverState]] = [
			[]
			for _ in range(len(sequence) + 1)
		]

		states[0].append(
			_SolverState(
				score=0.0,
				word_count=0,
				context=(),
				word=None,
				previous=None,
			)
		)

		capacity = max(
			limit,
			self.beam_width * limit,
		)

		for position in range(len(sequence)):
			current_states = states[position]

			if not current_states:
				continue

			matches = tuple(
				self._matches(
					sequence,
					position,
				)
			)

			for current in current_states:
				for match in matches:
					next_context = self._next_context(
						current.context,
						match.word,
					)

					candidate = self._extend(
						current,
						match.word,
						next_context,
					)

					target = states[match.end]
					target.append(candidate)

					if len(target) > capacity:
						states[match.end] = (
							self._prune_contextual_states(
								target,
								capacity,
							)
						)

		return self._prune_contextual_states(
			states[-1],
			limit,
		)

	def _extend(
		self,
		current: _SolverState,
		word: str,
		context: tuple[str, ...],
	) -> _SolverState:
		"""Creates an extended solver state with updated scoring metrics."""
		return _SolverState(
			score=current.score + self.scorer.score(
				word,
				current.context,
			),
			word_count=current.word_count + 1,
			context=context,
			word=word,
			previous=current,
		)

	def _rank_states(
		self,
		states: list[_SolverState],
		limit: int,
	) -> list[_SolverState]:
		"""Sorts states deterministically and caps them at the specified limit."""
		return sorted(
			states,
			key=self._state_sort_key,
			reverse=True,
		)[:limit]

	def _prune_contextual_states(
		self,
		states: list[_SolverState],
		limit: int,
	) -> list[_SolverState]:
		"""Retains the top ranked states grouped across context boundaries."""
		best_by_context: dict[
			tuple[str, ...],
			list[_SolverState],
		] = {}

		for state in states:
			best_by_context.setdefault(
				state.context,
				[],
			).append(state)

		result: list[_SolverState] = []

		for bucket in best_by_context.values():
			result.extend(
				self._rank_states(
					bucket,
					limit,
				)
			)

		return self._rank_states(
			result,
			limit,
		)

	def _state_sort_key(
		self,
		state: _SolverState,
	) -> tuple[float, int, str]:
		"""Generates a tuple for deterministic sorting of solver states."""
		return (
			state.score,
			-state.word_count,
			self._text_from_state(state),
		)

	def _matches(
		self,
		sequence: MorseSequence,
		position: int,
	) -> Iterator[MorseWordMatch]:
		"""Yields all matching words starting at the given sequence position."""
		return self._word_index.matches(
			sequence.symbols,
			position,
			self.max_word_length,
		)

	def _next_context(
		self,
		context: tuple[str, ...],
		word: str,
	) -> tuple[str, ...]:
		"""Updates trailing word context bounds based on the scorer configuration."""
		size = self.scorer.context_size

		if size == 0:
			return ()

		return (
			*context,
			word,
		)[-size:]

	def _text_from_state(
		self,
		state: _SolverState,
	) -> str:
		"""Reconstructs the full decoded string representation from a solver state."""
		words: list[str] = []
		current = state

		while current.word is not None:
			words.append(current.word)

			if current.previous is None:
				break

			current = current.previous

		words.reverse()

		return " ".join(words)

	def _candidate_from_state(
		self,
		state: _SolverState | None,
	) -> MorseCandidate | None:
		"""Reconstructs a public candidate from a terminal solver state."""
		if state is None:
			return None

		return MorseCandidate(
			text=self._text_from_state(state),
			score=state.score,
		)
