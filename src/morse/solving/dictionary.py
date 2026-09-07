from collections.abc import Iterable, Iterator


class MorseDictionary:
	def __init__(
		self,
		words: Iterable[str],
	) -> None:
		self._words: set[str] = set()
		self._prefixes: set[str] = {""}

		for word in words:
			normalized = self._normalize(word)

			if not normalized:
				continue

			self._words.add(normalized)

			for length in range(1, len(normalized) + 1):
				self._prefixes.add(normalized[:length])

	def _normalize(self, word: str) -> str:
		return word.strip().lower()

	def contains(self, word: str) -> bool:
		return self._normalize(word) in self._words

	def has_prefix(self, prefix: str) -> bool:
		return self._normalize(prefix) in self._prefixes

	def words(self) -> Iterator[str]:
		return iter(self._words)

	def __contains__(self, word: str) -> bool:
		return self.contains(word)

	def __len__(self) -> int:
		return len(self._words)
