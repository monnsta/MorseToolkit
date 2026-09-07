from collections.abc import Iterator
from dataclasses import dataclass

from morse.core import MorseAlphabet, MorseCandidate, MorseSequence, MorseSymbol
from morse.solving.dictionary import MorseDictionary
from morse.solving.index import MorseWordIndex
from morse.solving.scorer import MorseScorer


@dataclass(frozen=True, slots=True)
class _WordMatch:
	word: str
	end: int
	score: float


@dataclass(frozen=True, slots=True)
class _SolverState:
	text: str
	score: float
	context: tuple[str, ...]


class MorseSolver:
	def __init__(
		self,
		alphabet: MorseAlphabet,
		dictionary: MorseDictionary,
		scorer: MorseScorer,
		max_word_length: int = 32,
	) -> None:
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
		size = self.scorer.context_size

		if size == 0:
			return ()

		return (
			*context,
			word,
		)[-size:]
