from morse.solving.dictionary import MorseDictionary


def test_dictionary_contains_words() -> None:
	dictionary = MorseDictionary([
		"hello",
		"world",
	])

	assert dictionary.contains("hello")
	assert dictionary.contains("world")
	assert not dictionary.contains("bruh")


def test_dictionary_is_case_insensitive() -> None:
	dictionary = MorseDictionary([
		"Hello",
	])

	assert dictionary.contains("hello")
	assert dictionary.contains("HELLO")
	assert dictionary.contains("HeLlO")


def test_dictionary_strips_whitespace() -> None:
	dictionary = MorseDictionary([
		"  hello  ",
	])

	assert dictionary.contains("hello")


def test_dictionary_supports_contains_operator() -> None:
	dictionary = MorseDictionary([
		"hello",
	])

	assert "hello" in dictionary
	assert "bruh" not in dictionary


def test_dictionary_has_prefix() -> None:
	dictionary = MorseDictionary([
		"hello",
		"help",
		"world",
	])

	assert dictionary.has_prefix("h")
	assert dictionary.has_prefix("he")
	assert dictionary.has_prefix("hel")
	assert dictionary.has_prefix("hello")
	assert dictionary.has_prefix("help")

	assert not dictionary.has_prefix("hex")
	assert not dictionary.has_prefix("bruh")


def test_dictionary_is_case_insensitive_for_prefixes() -> None:
	dictionary = MorseDictionary([
		"Hello",
	])

	assert dictionary.has_prefix("h")
	assert dictionary.has_prefix("HE")
	assert dictionary.has_prefix("Hel")


def test_empty_words_are_ignored() -> None:
	dictionary = MorseDictionary([
		"",
		"   ",
		"hello",
	])

	assert len(dictionary) == 1
