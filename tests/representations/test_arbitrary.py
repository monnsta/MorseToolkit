from morse.core import MorseSymbol
from morse.representations import ArbitraryRepresentation


def test_arbitrary_representation() -> None:
	representation = ArbitraryRepresentation({
		MorseSymbol.DOT: "e",
		MorseSymbol.DASH: "r",
	})

	assert representation.encode(MorseSymbol.DOT) == "e"
	assert representation.encode(MorseSymbol.DASH) == "r"

	assert representation.decode("e") is MorseSymbol.DOT
	assert representation.decode("r") is MorseSymbol.DASH
