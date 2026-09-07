from dataclasses import dataclass
from collections.abc import Iterator, Iterable

from .tokens import MorseToken


@dataclass(frozen=True, slots=True)
class MorseStream:
	"""Immutable sequence container for streaming or batch processing of Morse tokens.

	Attributes:
		tokens: Tuple of MorseToken instances representing the stream sequence.
	"""

	tokens: tuple[MorseToken, ...]

	def __iter__(self) -> Iterator[MorseToken]:
		"""Returns an iterator over the underlying tokens.

		Returns:
			An iterator yielding MorseToken items.
		"""
		return iter(self.tokens)

	def __len__(self) -> int:
		"""Returns total count of tokens in the stream.

		Returns:
			The integer length of the token sequence.
		"""
		return len(self.tokens)

	def __getitem__(self, index: int) -> MorseToken:
		"""Retrieves token at specified index position.

		Args:
			index: The zero-based integer index or slice.

		Returns:
			The MorseToken at the specified index.
		"""
		return self.tokens[index]

	@classmethod
	def from_tokens(cls, tokens: Iterable[MorseToken]) -> "MorseStream":
		"""Constructs a MorseStream from an iterator of tokens.

		Args:
			tokens: An iterator producing MorseToken elements.

		Returns:
			A new instantiated MorseStream instance.
		"""
		return cls(tuple(tokens))
