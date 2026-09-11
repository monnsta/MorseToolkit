from collections.abc import Mapping, Sequence

from morse.core import MorseAlphabet, MorseSymbol


class InternationalMorse(MorseAlphabet):
	"""Implementation of the standard International Morse Code alphabet.

	Supports alphanumeric characters (A-Z, 0-9) and standard punctuation symbols.
	Case-insensitive during encoding.
	"""

	_CODES: Mapping[str, tuple[MorseSymbol, ...]] = {
		"A": (MorseSymbol.DOT, MorseSymbol.DASH),
		"B": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"C": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
		"D": (MorseSymbol.DASH, MorseSymbol.DOT, MorseSymbol.DOT),
		"E": (MorseSymbol.DOT,),
		"F": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
		"G": (MorseSymbol.DASH, MorseSymbol.DASH, MorseSymbol.DOT),
		"H": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"I": (MorseSymbol.DOT, MorseSymbol.DOT),
		"J": (
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
		),
		"K": (MorseSymbol.DASH, MorseSymbol.DOT, MorseSymbol.DASH),
		"L": (
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"M": (MorseSymbol.DASH, MorseSymbol.DASH),
		"N": (MorseSymbol.DASH, MorseSymbol.DOT),
		"O": (MorseSymbol.DASH, MorseSymbol.DASH, MorseSymbol.DASH),
		"P": (
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
		"Q": (
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		),
		"R": (MorseSymbol.DOT, MorseSymbol.DASH, MorseSymbol.DOT),
		"S": (MorseSymbol.DOT, MorseSymbol.DOT, MorseSymbol.DOT),
		"T": (MorseSymbol.DASH,),
		"U": (MorseSymbol.DOT, MorseSymbol.DOT, MorseSymbol.DASH),
		"V": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		),
		"W": (MorseSymbol.DOT, MorseSymbol.DASH, MorseSymbol.DASH),
		"X": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		),
		"Y": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
		),
		"Z": (
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"É": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"0": (
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
		),
		"1": (
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
		),
		"2": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
		),
		"3": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
		),
		"4": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		),
		"5": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"6": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"7": (
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"8": (
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"9": (
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
		".": (
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		),
		",": (
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
		),
		"?": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		"'": (
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
		"!": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
		),
		"/": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
		"(": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
		")": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		),
		"&": (
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		":": (
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		),
		";": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
		"=": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		),
		"+": (
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
		"-": (
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		),
		"_": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		),
		'"': (
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
		"$": (
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		),
		"@": (
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		),
	}

	def __init__(self) -> None:
		"""Initializes the reverse lookup mapping table for decoding optimization."""
		self._reverse_codes = {
			code: character for character, code in self._CODES.items()
		}

	def encode(self, character: str) -> tuple[MorseSymbol, ...]:
		"""Encodes a single supported character into standard Morse symbols.

		Args:
			character: A single string character to encode. Case-insensitive.

		Returns:
			A tuple of MorseSymbol objects corresponding to the character.

		Raises:
			ValueError: If the character is not supported by standard International Morse.
		"""
		try:
			return self._CODES[character.upper()]
		except KeyError as exc:
			raise ValueError(f"Unsupported character: {character!r}") from exc

	def decode(self, symbols: Sequence[MorseSymbol]) -> str:
		"""Decodes a sequence of Morse symbols into its uppercase character equivalent.

		Args:
			symbols: A sequence of MorseSymbol instances.

		Returns:
			The decoded uppercase string character or punctuation symbol.

		Raises:
			ValueError: If the symbol sequence does not map to a valid character.
		"""
		code = tuple(symbols)

		try:
			return self._reverse_codes[code]
		except KeyError as exc:
			raise ValueError(
				f"Unsupported Morse sequence: {symbols!r}"
			) from exc

	def can_encode(self, character: str) -> bool:
		"""Checks whether a character is supported by International Morse.

		Args:
			character: The text character to evaluate.

		Returns:
			True if character can be encoded, False otherwise.
		"""
		return character.upper() in self._CODES

	def can_decode(self, symbols: Sequence[MorseSymbol]) -> bool:
		"""Checks whether a sequence of Morse symbols represents a valid character.

		Args:
			symbols: A sequence of MorseSymbol instances.

		Returns:
			True if symbols can be decoded, False otherwise.
		"""
		return tuple(symbols) in self._reverse_codes
