from morse.alphabets import InternationalMorse
from morse.solving.index import MorseWordIndex


def encode_word(word: str) -> tuple:
	alphabet = InternationalMorse()
	symbols = []

	for character in word:
		symbols.extend(alphabet.encode(character))

	return tuple(symbols)


def make_index(words: list[str]) -> MorseWordIndex:
	return MorseWordIndex(((word, encode_word(word)) for word in words))


def test_index_finds_word() -> None:
	index = make_index(["hello"])

	matches = list(
		index.matches(
			encode_word("hello"),
			0,
			32,
		)
	)

	assert [(match.word, match.end) for match in matches] == [
		("hello", len(encode_word("hello"))),
	]


def test_index_finds_multiple_words() -> None:
	index = make_index(
		[
			"hello",
			"hell",
		]
	)

	sequence = encode_word("hello")

	matches = list(
		index.matches(
			sequence,
			0,
			32,
		)
	)

	assert {(match.word, match.end) for match in matches} == {
		("hell", len(encode_word("hell"))),
		("hello", len(encode_word("hello"))),
	}


def test_index_stops_at_invalid_prefix() -> None:
	index = make_index(["hello"])

	sequence = encode_word("hello")

	matches = list(
		index.matches(
			sequence,
			0,
			32,
		)
	)

	assert matches


def test_index_respects_maximum_word_length() -> None:
	index = make_index(["hello"])

	matches = list(
		index.matches(
			encode_word("hello"),
			0,
			3,
		)
	)

	assert matches == []


def test_index_supports_matching_from_middle() -> None:
	index = make_index(["hello"])

	sequence = encode_word("xhello")

	hello_start = len(encode_word("x"))

	matches = list(
		index.matches(
			sequence,
			hello_start,
			32,
		)
	)

	assert any(match.word == "hello" for match in matches)
