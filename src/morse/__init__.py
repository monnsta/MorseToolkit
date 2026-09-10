"""A flexible Morse code toolkit for Python."""

from collections.abc import Iterable

from morse.solving import MorseDictionary, MorseScorer
from morse.api import Morse


__version__ = "0.1.0"


_default = Morse()


def encode(text: str) -> str:
	"""Encodes plain text into human-readable Morse code.

	Args:
		text: Text to encode.

	Returns:
		A spaced Morse representation.

	Example:
		morse.encode("HELLO WORLD")
		# ".... . .-.. .-.. ---   .-- --- .-. .-.. -.."
	"""
	return _default.encode(text)


def encode_unspaced(text: str) -> str:
	"""Encodes text into continuous Morse without boundaries.

	This is useful for producing input suitable for ``solve()``.

	Args:
		text: Text to encode.

	Returns:
		A continuous Morse representation.

	Example:
		morse.encode_unspaced("HELLO")
		# "......-...-..---"
	"""
	return _default.encode_unspaced(text)


def decode(value: str) -> str:
	"""Decodes boundary-delimited Morse code.

	This method is intended for Morse where character boundaries are
	already known.

	Args:
		value: Spaced Morse representation.

	Returns:
		The decoded text.

	Example:
		morse.decode(".... . .-.. .-.. ---")
		# "HELLO"
	"""
	return _default.decode(value)


def solve(
	value: str,
	dictionary: MorseDictionary | Iterable[str],
	scorer: MorseScorer | None = None,
	max_word_length: int = 32,
	beam_width: int = 8,
):
	"""Solves an unspaced Morse sequence into its most likely text.

	Unlike ``decode()``, this method has to infer character and word
	boundaries.

	Args:
		value: Continuous Morse representation.
		dictionary: Dictionary or iterable of english words.
		scorer: Optional scoring strategy.
				Defaults to DictionaryScorer.
		max_word_length: Maximum dictionary word length.
		beam_width: Beam width for contextual scorers.

	Returns:
		The best candidate, or None if no solution exists.

	Example:
		result = morse.solve(
			"......-...-..----......-..",
			["hello", "world"],
		)

		print(result.text)
	"""
	return _default.solve(
		value,
		dictionary,
		scorer,
		max_word_length,
		beam_width,
	)


__all__ = (
	'Morse',
	'encode',
	'encode_unspaced',
	'decode',
	'solve',
)
