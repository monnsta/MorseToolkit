from morse.alphabets import InternationalMorse
from morse.encoding import MorseDecoder
from morse.parsing.spaced import SpacedParser
from morse.representations import TextRepresentation


def test_decode_sos() -> None:
	parser = SpacedParser(TextRepresentation())
	decoder = MorseDecoder(InternationalMorse())

	stream = parser.parse("... --- ...")

	assert decoder.decode(stream) == "SOS"


def test_decode_word_boundary() -> None:
	parser = SpacedParser(TextRepresentation())
	decoder = MorseDecoder(InternationalMorse())

	stream = parser.parse("... --- ...   .-")

	assert decoder.decode(stream) == "SOS A"


def test_decode_single_character() -> None:
	parser = SpacedParser(TextRepresentation())
	decoder = MorseDecoder(InternationalMorse())

	stream = parser.parse("....")

	assert decoder.decode(stream) == "H"


def test_decode_without_trailing_boundary() -> None:
	parser = SpacedParser(TextRepresentation())
	decoder = MorseDecoder(InternationalMorse())

	stream = parser.parse(".... .")

	assert decoder.decode(stream) == "HE"


def test_decode_empty_stream() -> None:
	parser = SpacedParser(TextRepresentation())
	decoder = MorseDecoder(InternationalMorse())

	stream = parser.parse("")

	assert decoder.decode(stream) == ""
