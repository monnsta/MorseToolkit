from morse.core import MorseSymbol, MorseTokenType
from morse.encoding import MorseDecoder
from morse.alphabets import InternationalMorse
from morse.parsing import (
	MorseBoundarySyntax,
	SpacedParser
)
from morse.representations import (
	TextRepresentation,
	ArbitraryRepresentation
)


def test_parse_spaced_morse() -> None:
	parser = SpacedParser(TextRepresentation())

	stream = parser.parse("... --- ...")

	assert [token.type for token in stream] == [
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
		MorseTokenType.CHARACTER_BOUNDARY,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
		MorseTokenType.CHARACTER_BOUNDARY,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
	]


def test_parse_custom_word_boundary() -> None:
	parser = SpacedParser(
		TextRepresentation(),
		boundaries=MorseBoundarySyntax(
			character_boundary=" ",
			word_boundary="/",
		),
	)

	stream = parser.parse(
		".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
	)

	assert any(
		token.type is MorseTokenType.WORD_BOUNDARY
		for token in stream
	)


def test_parse_custom_character_and_word_boundaries() -> None:
	parser = SpacedParser(
		TextRepresentation(),
		boundaries=MorseBoundarySyntax(
			character_boundary="|",
			word_boundary="||",
		),
	)

	stream = parser.parse(
		"....|.|.-..|.-..|---||.--|---|.-.|.-..|-.."
	)

	assert sum(
		token.type is MorseTokenType.CHARACTER_BOUNDARY
		for token in stream
	) == 8

	assert sum(
		token.type is MorseTokenType.WORD_BOUNDARY
		for token in stream
	) == 1


def test_parse_symbols_without_boundaries() -> None:
	parser = SpacedParser(TextRepresentation())

	stream = parser.parse("...")

	assert len(stream) == 3
	assert all(
		token.type is MorseTokenType.SYMBOL
		for token in stream
	)


def test_parse_empty_value() -> None:
	parser = SpacedParser(TextRepresentation())

	stream = parser.parse("")

	assert len(stream) == 0


def test_parse_multi_character_representation() -> None:
	representation = ArbitraryRepresentation({
		MorseSymbol.DOT: "dot",
		MorseSymbol.DASH: "dash",
	})

	parser = SpacedParser(representation)

	stream = parser.parse("dotdotdash")

	assert [token.type for token in stream] == [
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
	]

	assert [token.symbol for token in stream] == [
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DASH,
	]


def test_parse_multi_character_representation_with_boundaries() -> None:
	representation = ArbitraryRepresentation({
		MorseSymbol.DOT: "dot",
		MorseSymbol.DASH: "dash",
	})

	parser = SpacedParser(representation)

	stream = parser.parse(
		"dotdotdash dashdotdot dotdash"
	)

	assert [token.type for token in stream] == [
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
		MorseTokenType.CHARACTER_BOUNDARY,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
		MorseTokenType.CHARACTER_BOUNDARY,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
	]

	assert [token.symbol for token in stream if token.symbol is not None] == [
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DASH,
		MorseSymbol.DASH,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DASH,
	]


def test_parse_and_decode_multi_character_representation() -> None:
	representation = ArbitraryRepresentation({
		MorseSymbol.DOT: "dot",
		MorseSymbol.DASH: "dash",
	})

	parser = SpacedParser(representation)
	decoder = MorseDecoder(InternationalMorse())

	stream = parser.parse(
		"dotdotdot dashdashdash dotdotdot"
	)

	assert decoder.decode(stream) == "SOS"
