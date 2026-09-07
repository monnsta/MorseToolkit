from morse.core import MorseSymbol
from morse.representations import TextRepresentation


def test_text_encode() -> None:
	representation = TextRepresentation()

	assert representation.encode(MorseSymbol.DOT) == "."
	assert representation.encode(MorseSymbol.DASH) == "-"


def test_text_decode() -> None:
	representation = TextRepresentation()

	assert representation.decode(".") is MorseSymbol.DOT
	assert representation.decode("-") is MorseSymbol.DASH
