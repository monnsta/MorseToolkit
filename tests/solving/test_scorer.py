from morse.solving.dictionary import MorseDictionary
from morse.solving.scorer import (
	DictionaryScorer,
	FrequencyScorer,
)


def test_dictionary_scorer_accepts_dictionary_words() -> None:
	dictionary = MorseDictionary([
		"hello",
		"world",
	])

	scorer = DictionaryScorer(dictionary)

	assert scorer.score("hello") == 1.0
	assert scorer.score("world") == 1.0


def test_dictionary_scorer_rejects_unknown_words() -> None:
	dictionary = MorseDictionary([
		"hello",
	])

	scorer = DictionaryScorer(dictionary)

	assert scorer.score("python") == 0.0


def test_dictionary_scorer_is_case_insensitive() -> None:
	dictionary = MorseDictionary([
		"hello",
	])

	scorer = DictionaryScorer(dictionary)

	assert scorer.score("HELLO") == 1.0


def test_frequency_scorer_returns_frequency() -> None:
	scorer = FrequencyScorer({
		"hello": 10.0,
		"world": 5.0,
	})

	assert scorer.score("hello") == 10.0
	assert scorer.score("world") == 5.0


def test_frequency_scorer_is_case_insensitive() -> None:
	scorer = FrequencyScorer({
		"hello": 10.0,
	})

	assert scorer.score("HELLO") == 10.0


def test_frequency_scorer_uses_default_score() -> None:
	scorer = FrequencyScorer(
		{"hello": 10.0},
		default_score=0.5,
	)

	assert scorer.score("python") == 0.5


def test_frequency_scorer_rejects_negative_frequency() -> None:
	try:
		FrequencyScorer({
			"hello": -1.0,
		})
	except ValueError:
		pass
	else:
		raise AssertionError(
			"Expected ValueError"
		)


def test_frequency_scorer_rejects_negative_default_score() -> None:
	try:
		FrequencyScorer(
			{},
			default_score=-1.0,
		)
	except ValueError:
		pass
	else:
		raise AssertionError(
			"Expected ValueError"
	)
