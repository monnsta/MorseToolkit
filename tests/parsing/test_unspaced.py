from morse.core import MorseSymbol
from morse.parsing import UnspacedParser
from morse.representations import (
	ArbitraryRepresentation,
	TextRepresentation,
)


def test_parse_unspaced_morse():
	parser = UnspacedParser(TextRepresentation())

	sequence = parser.parse("...---...")

	assert sequence.symbols == (
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DASH,
		MorseSymbol.DASH,
		MorseSymbol.DASH,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
	)


def test_parse_unspaced_arbitrary_representation():
	parser = UnspacedParser(
		ArbitraryRepresentation(
			{
				MorseSymbol.DOT: "e",
				MorseSymbol.DASH: "r",
			}
		)
	)

	sequence = parser.parse("eeerrr")

	assert sequence.symbols == (
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DASH,
		MorseSymbol.DASH,
		MorseSymbol.DASH,
	)


def test_parse_empty_unspaced_morse():
	parser = UnspacedParser(TextRepresentation())

	sequence = parser.parse("")

	assert sequence.symbols == ()
