from collections.abc import Iterable, Iterator


class MorseDictionary:
	"""Normalized word dictionary used by Morse solving and scoring."""

	def __init__(self, words: Iterable[str]) -> None:
		"""Initializes the dictionary with a collection of valid words.

		Args:
			words: An iterable of strings to populate the dictionary.
		"""
		self._words: set[str] = set()
		self._prefixes: set[str] | None = None

		for word in words:
			normalized = self._normalize(word)
			if normalized:
				self._words.add(normalized)

	def _normalize(self, word: str) -> str:
		"""Normalizes a string for storage and comparison.

		Args:
			word: The string to normalize.

		Returns:
			The lowercase, stripped string.
		"""
		return word.strip().lower()

	def contains(self, word: str) -> bool:
		"""Checks if a normalized word exists in the dictionary.

		Args:
			word: The word to check.

		Returns:
			True if the word is in the dictionary, False otherwise.
		"""
		return self._normalize(word) in self._words

	def has_prefix(self, prefix: str) -> bool:
		"""Checks if the given string is a valid prefix of any word in the dictionary.

		Args:
			prefix: The prefix string to evaluate.

		Returns:
			True if the prefix exists, False otherwise.
		"""
		prefix = self._normalize(prefix)

		if self._prefixes is None:
			self._build_prefixes()

		if self._prefixes is None:
			return False

		return prefix in self._prefixes

	def _build_prefixes(self) -> None:
		"""Lazily builds the set of all valid word prefixes."""
		prefixes = {""}

		for word in self._words:
			for length in range(1, len(word) + 1):
				prefixes.add(word[:length])

		self._prefixes = prefixes

	def words(self) -> Iterator[str]:
		"""Returns an iterator over all normalized words in the dictionary.

		Returns:
			An iterator yielding string words.
		"""
		return iter(self._words)

	def __contains__(self, word: str) -> bool:
		"""Enables the 'in' operator for dictionary inclusion checks.

		Args:
			word: The word to check.

		Returns:
			True if the word is included, False otherwise.
		"""
		return self.contains(word)

	def __len__(self) -> int:
		"""Returns the total number of unique normalized words in the dictionary.

		Returns:
			The integer count of words.
		"""
		return len(self._words)
