from morse.parsing.boundaries import MorseBoundarySyntax
from morse.parsing.tokenizer import MorseTokenizer, TokenType


def test_tokenize_default_character_boundaries() -> None:
	tokenizer = MorseTokenizer()

	tokens = tokenizer.tokenize("... --- ...")

	assert [token.type for token in tokens] == [
		TokenType.VALUE,
		TokenType.CHARACTER_BOUNDARY,
		TokenType.VALUE,
		TokenType.CHARACTER_BOUNDARY,
		TokenType.VALUE,
	]

	assert [token.value for token in tokens] == [
		"...",
		" ",
		"---",
		" ",
		"...",
	]


def test_tokenize_default_word_boundary() -> None:
	tokenizer = MorseTokenizer()

	tokens = tokenizer.tokenize("... ---   ...")

	assert [token.type for token in tokens] == [
		TokenType.VALUE,
		TokenType.CHARACTER_BOUNDARY,
		TokenType.VALUE,
		TokenType.WORD_BOUNDARY,
		TokenType.VALUE,
	]


def test_tokenize_custom_word_boundary_without_whitespace() -> None:
	boundaries = MorseBoundarySyntax(
		character_boundary=" ",
		word_boundary="/",
	)

	tokenizer = MorseTokenizer(boundaries)

	tokens = tokenizer.tokenize("... ---/...")

	assert [token.type for token in tokens] == [
		TokenType.VALUE,
		TokenType.CHARACTER_BOUNDARY,
		TokenType.VALUE,
		TokenType.WORD_BOUNDARY,
		TokenType.VALUE,
	]


def test_tokenize_custom_word_boundary() -> None:
	boundaries = MorseBoundarySyntax(
		character_boundary=" ",
		word_boundary="/",
	)

	tokenizer = MorseTokenizer(boundaries)

	tokens = tokenizer.tokenize("... --- / ...")

	assert [token.type for token in tokens] == [
		TokenType.VALUE,
		TokenType.CHARACTER_BOUNDARY,
		TokenType.VALUE,
		TokenType.CHARACTER_BOUNDARY,
		TokenType.WORD_BOUNDARY,
		TokenType.CHARACTER_BOUNDARY,
		TokenType.VALUE,
	]


def test_tokenize_custom_boundaries() -> None:
	boundaries = MorseBoundarySyntax(
		character_boundary="|",
		word_boundary="||",
	)

	tokenizer = MorseTokenizer(boundaries)

	tokens = tokenizer.tokenize("...|---||...")

	assert [token.type for token in tokens] == [
		TokenType.VALUE,
		TokenType.CHARACTER_BOUNDARY,
		TokenType.VALUE,
		TokenType.WORD_BOUNDARY,
		TokenType.VALUE,
	]


def test_word_boundary_is_checked_before_character_boundary() -> None:
	boundaries = MorseBoundarySyntax(
		character_boundary="|",
		word_boundary="||",
	)

	tokenizer = MorseTokenizer(boundaries)

	tokens = tokenizer.tokenize("...||---")

	assert tokens[1].type is TokenType.WORD_BOUNDARY
	assert tokens[1].value == "||"


def test_tokenize_empty_value() -> None:
	tokenizer = MorseTokenizer()

	assert tokenizer.tokenize("") == ()


def test_tokenize_preserves_value_tokens() -> None:
	tokenizer = MorseTokenizer()

	tokens = tokenizer.tokenize("...---...")

	assert len(tokens) == 1
	assert tokens[0].type is TokenType.VALUE
	assert tokens[0].value == "...---..."
