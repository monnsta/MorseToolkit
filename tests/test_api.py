import morse

from morse import Morse
from morse.core import MorseSymbol
from morse.representations import ArbitraryRepresentation


def test_encode() -> None:
	assert morse.encode("HELLO") == ".... . .-.. .-.. ---"


def test_decode() -> None:
	assert morse.decode(".... . .-.. .-.. ---") == "HELLO"


def test_round_trip() -> None:
	text = "HELLO WORLD"

	encoded = morse.encode(text)
	decoded = morse.decode(encoded)

	assert decoded == text


def test_encode_unspaced() -> None:
	assert morse.encode_unspaced("HELLO") == "......-...-..---"


def test_custom_representation() -> None:
	representation = ArbitraryRepresentation(
		{
			MorseSymbol.DOT: "e",
			MorseSymbol.DASH: "r",
		}
	)

	morse_toolkit = Morse(
		representation=representation,
	)

	assert morse_toolkit.encode("E") == "e"
	assert morse_toolkit.encode("T") == "r"


def test_custom_representation_round_trip() -> None:
	representation = ArbitraryRepresentation(
		{
			MorseSymbol.DOT: "e",
			MorseSymbol.DASH: "r",
		}
	)

	morse_toolkit = Morse(
		representation=representation,
	)

	encoded = morse_toolkit.encode("HELLO")
	decoded = morse_toolkit.decode(encoded)

	assert decoded == "HELLO"


def test_solve_unspaced() -> None:
	result = morse.solve(
		"......-...-..---.-----.-..-..-..",
		["hello", "world"],
	)

	assert result is not None
	assert result.text == "hello world"


def test_solve_multiple_words() -> None:
	toolkit = Morse()

	result = toolkit.solve(
		toolkit.encode_unspaced("eggandtoast"),
		["egg", "and", "toast"],
	)

	assert result is not None
	assert result.text == "egg and toast"


def test_configured_dictionary() -> None:
	toolkit = Morse()

	dictionary = toolkit.dictionary(
		[
			"hello",
			"world",
		]
	)

	result = toolkit.solve(
		toolkit.encode_unspaced("hello world"),
		dictionary,
	)

	assert result is not None
	assert result.text == "hello world"
