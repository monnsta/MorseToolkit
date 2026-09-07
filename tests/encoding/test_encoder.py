from morse.alphabets import InternationalMorse
from morse.core import MorseSymbol, MorseTokenType, MorseStream
from morse.encoding import MorseEncoder


def test_encode_single_character() -> None:
	encoder = MorseEncoder(InternationalMorse())

	stream = encoder.encode("A")

	assert [token.type for token in stream] == [
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
	]

	assert [token.symbol for token in stream] == [
		MorseSymbol.DOT,
		MorseSymbol.DASH,
	]


def test_encode_multiple_characters() -> None:
	encoder = MorseEncoder(InternationalMorse())

	stream = encoder.encode("SOS")

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


def test_encode_word_boundary() -> None:
	encoder = MorseEncoder(InternationalMorse())

	stream = encoder.encode("SOS A")

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
		MorseTokenType.WORD_BOUNDARY,
		MorseTokenType.SYMBOL,
		MorseTokenType.SYMBOL,
	]


def test_encode_empty_string() -> None:
	encoder = MorseEncoder(InternationalMorse())

	assert encoder.encode("") == MorseStream(())
