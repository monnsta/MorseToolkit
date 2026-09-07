from morse.alphabets import InternationalMorse
from morse.core.symbols import MorseSymbol


def test_encode_letter() -> None:
	alphabet = InternationalMorse()

	assert alphabet.encode("A") == (
		MorseSymbol.DOT,
		MorseSymbol.DASH,
	)


def test_decode_letter() -> None:
	alphabet = InternationalMorse()

	assert alphabet.decode((
		MorseSymbol.DOT,
		MorseSymbol.DASH,
	)) == "A"


def test_encode_is_case_insensitive() -> None:
	alphabet = InternationalMorse()

	assert alphabet.encode("a") == alphabet.encode("A")


def test_can_encode() -> None:
	alphabet = InternationalMorse()

	assert alphabet.can_encode("A")
	assert alphabet.can_encode("5")
	assert not alphabet.can_encode("^")
