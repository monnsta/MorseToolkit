from dataclasses import dataclass, field
from collections.abc import Iterator

from morse.core import MorseSymbol


@dataclass(frozen=True, slots=True)
class MorseWordMatch:
	word: str
	end: int


@dataclass(slots=True)
class _MorseTrieNode:
	children: dict[MorseSymbol, "_MorseTrieNode"] = field(
		default_factory=dict
	)
	words: list[tuple[str, int]] = field(
		default_factory=list
	)


class MorseWordIndex:
	def __init__(
		self,
		word_codes: Iterator[
			tuple[str, tuple[MorseSymbol, ...]]
		],
	) -> None:
		self._root = _MorseTrieNode()

		for word, symbols in word_codes:
			self.add(word, symbols)

	def add(
		self,
		word: str,
		symbols: tuple[MorseSymbol, ...],
	) -> None:
		if not symbols:
			raise ValueError(
				"Cannot index an empty Morse sequence"
			)

		node = self._root

		for symbol in symbols:
			node = node.children.setdefault(
				symbol,
				_MorseTrieNode(),
			)

		node.words.append(
			(word, len(word))
		)

	def matches(
		self,
		sequence: tuple[MorseSymbol, ...],
		position: int,
		max_word_length: int,
	) -> Iterator[MorseWordMatch]:
		if position >= len(sequence):
			return

		node = self._root

		for end in range(position, len(sequence)):
			node = node.children.get(sequence[end])

			if node is None:
				return

			for word, word_length in node.words:
				if word_length <= max_word_length:
					yield MorseWordMatch(
						word=word,
						end=end + 1,
					)
