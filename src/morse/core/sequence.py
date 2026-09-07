from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from .symbols import MorseSymbol


@dataclass(frozen=True, slots=True)
class MorseSequence:
	"""Immutable container representing a sequence of Morse code symbols.

	Attributes:
		symbols: Tuple of MorseSymbol instances comprising the sequence.
	"""

	symbols: tuple[MorseSymbol, ...]

	def __iter__(self) -> Iterator[MorseSymbol]:
		"""Returns an iterator over the underlying symbols.

		Returns:
			An iterator yielding MorseSymbol items.
		"""
		return iter(self.symbols)

	def __len__(self) -> int:
		"""Returns the total number of symbols in the sequence.

		Returns:
			The length of the symbol tuple.
		"""
		return len(self.symbols)

	def __getitem__(self, index: int) -> MorseSymbol:
		"""Retrieves the MorseSymbol at the specified index position.

		Args:
			index: The zero-based integer index or slice.

		Returns:
			The MorseSymbol at the specified index.
		"""
		return self.symbols[index]

	@classmethod
	def from_symbols(
		cls,
		symbols: Iterable[MorseSymbol],
	) -> "MorseSequence":
		"""Constructs a MorseSequence from an iterable of symbols.

		Args:
			symbols: An iterable yielding MorseSymbol objects.

		Returns:
			A new instantiated MorseSequence instance.
		"""
		return cls(tuple(symbols))


@dataclass(frozen=True, slots=True)
class MorseSegmentation:
	"""A possible division of a Morse sequence into characters.

	Attributes:
		characters: Tuple of character symbol sequences.
	"""

	characters: tuple[tuple[MorseSymbol, ...], ...]

	def __iter__(
		self,
	) -> Iterator[tuple[MorseSymbol, ...]]:
		"""Returns an iterator over character symbol sequences.

		Returns:
			An iterator yielding tuples of MorseSymbol instances for each character.
		"""
		return iter(self.characters)

	def __len__(self) -> int:
		"""Returns total count of segmented characters.

		Returns:
			The integer number of character groups in the segmentation.
		"""
		return len(self.characters)

	def __getitem__(
		self,
		index: int,
	) -> tuple[MorseSymbol, ...]:
		"""Retrieves the symbol sequence for a character at specified index position.

		Args:
			index: The zero-based integer index or slice.

		Returns:
			A tuple of MorseSymbol instances for the character at the given index.
		"""
		return self.characters[index]

	@classmethod
	def from_characters(
		cls,
		characters: Iterable[Iterable[MorseSymbol]],
	) -> "MorseSegmentation":
		"""Constructs a MorseSegmentation from an iterable of character symbol iterables.

		Args:
			characters: An iterable producing iterables of MorseSymbol objects.

		Returns:
			A new instantiated MorseSegmentation instance.
		"""
		return cls(
			tuple(
				tuple(character)
				for character in characters
			)
		)
