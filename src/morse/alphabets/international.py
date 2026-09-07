from collections.abc import Mapping, Sequence

from morse.core import MorseAlphabet, MorseSymbol


class InternationalMorse(MorseAlphabet):
	"""Implementation of the standard International Morse Code alphabet.

	Supports alphanumeric characters (A-Z, 0-9) and standard punctuation symbols.
	Case-insensitive during encoding.
	"""

	_CODES: Mapping[str, str] = {
		"A": ".-",
		"B": "-...",
		"C": "-.-.",
		"D": "-..",
		"E": ".",
		"F": "..-.",
		"G": "--.",
		"H": "....",
		"I": "..",
		"J": ".---",
		"K": "-.-",
		"L": ".-..",
		"M": "--",
		"N": "-.",
		"O": "---",
		"P": ".--.",
		"Q": "--.-",
		"R": ".-.",
		"S": "...",
		"T": "-",
		"U": "..-",
		"V": "...-",
		"W": ".--",
		"X": "-..-",
		"Y": "-.--",
		"Z": "--..",

		"0": "-----",
		"1": ".----",
		"2": "..---",
		"3": "...--",
		"4": "....-",
		"5": ".....",
		"6": "-....",
		"7": "--...",
		"8": "---..",
		"9": "----.",

		".": ".-.-.-",
		",": "--..--",
		"?": "..--..",
		"'": ".----.",
		"!": "-.-.--",
		"/": "-..-.",
		"(": "-.--.",
		")": "-.--.-",
		"&": ".-...",
		":": "---...",
		";": "-.-.-.",
		"=": "-...-",
		"+": ".-.-.",
		"-": "-....-",
		"_": "..--.-",
		'"': ".-..-.",
		"$": "...-..-",
		"@": ".--.-.",
	}

	def __init__(self) -> None:
		"""Initializes the reverse lookup mapping table for decoding optimization."""
		self._reverse_codes = {
			code: character
			for character, code in self._CODES.items()
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
			code = self._CODES[character.upper()]
		except KeyError as exc:
			raise ValueError(
				f"Unsupported character: {character!r}"
			) from exc

		return tuple(
			MorseSymbol.DOT if symbol == "." else MorseSymbol.DASH
			for symbol in code
		)

	def decode(self, symbols: Sequence[MorseSymbol]) -> str:
		"""Decodes a sequence of Morse symbols into its uppercase character equivalent.

		Args:
			symbols: A sequence of MorseSymbol instances.

		Returns:
			The decoded uppercase string character or punctuation symbol.

		Raises:
			ValueError: If the symbol sequence does not map to a valid character.
		"""
		code = "".join(symbol.value for symbol in symbols)

		try:
			return self._reverse_codes[code]
		except KeyError as exc:
			raise ValueError(
				f"Unsupported Morse sequence: {code!r}"
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
		code = "".join(symbol.value for symbol in symbols)

		return code in self._reverse_codes
