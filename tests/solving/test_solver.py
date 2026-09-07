from morse.alphabets import InternationalMorse
from morse.core import MorseSequence, MorseSymbol
from morse.solving import (
	MorseDictionary,
	DictionaryScorer,
	MorseSolver,
	FrequencyScorer,
	BigramScorer,
)


def make_solver(words: list[str]) -> MorseSolver:
	dictionary = MorseDictionary(words)
	scorer = DictionaryScorer(dictionary)

	return MorseSolver(
		InternationalMorse(),
		dictionary,
		scorer,
	)


def encode_unspaced(text: str) -> MorseSequence:
	alphabet = InternationalMorse()

	symbols = []

	for character in text.lower():
		if character == " ":
			continue

		symbols.extend(
			alphabet.encode(character)
		)

	return MorseSequence.from_symbols(symbols)


def test_solve_single_word() -> None:
	solver = make_solver([
		"hello",
	])

	sequence = encode_unspaced("hello")

	result = solver.solve(sequence)

	assert result is not None
	assert result.text == "hello"


def test_solve_multiple_words() -> None:
	solver = make_solver([
		"hello",
		"world",
	])

	sequence = encode_unspaced("helloworld")

	result = solver.solve(sequence)

	assert result is not None
	assert result.text == "hello world"


def test_solve_egg_and_toast() -> None:
	solver = make_solver([
		"egg",
		"and",
		"toast",
	])

	sequence = encode_unspaced("eggandtoast")

	result = solver.solve(sequence)

	assert result is not None
	assert result.text == "egg and toast"


def test_unsolvable_sequence_returns_none() -> None:
	solver = make_solver([
		"hello",
		"world",
	])

	sequence = MorseSequence((
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DOT,
	))

	assert solver.solve(sequence) is None


def test_empty_sequence() -> None:
	solver = make_solver([
		"hello",
	])

	result = solver.solve(MorseSequence(()))

	assert result is not None
	assert result.text == ""
	assert result.score == 0.0


def test_solver_respects_maximum_word_length() -> None:
	solver = MorseSolver(
		InternationalMorse(),
		MorseDictionary(["hello"]),
		DictionaryScorer(
			MorseDictionary(["hello"])
		),
		max_word_length=3,
	)

	sequence = encode_unspaced("hello")

	assert solver.solve(sequence) is None


def test_solver_prefers_higher_scoring_candidate() -> None:
	solver = make_solver([
		"hello",
	])

	sequence = encode_unspaced("hello")

	result = solver.solve(sequence)

	assert result is not None
	assert result.text == "hello"
	assert result.score == 1.0


def test_solver_prefers_higher_scoring_word() -> None:
	dictionary = MorseDictionary([
		"hello",
	])

	scorer = FrequencyScorer({
		"hello": 10.0,
	})

	solver = MorseSolver(
		InternationalMorse(),
		dictionary,
		scorer,
	)

	sequence = encode_unspaced("hello")

	result = solver.solve(sequence)

	assert result is not None
	assert result.text == "hello"
	assert result.score == 10.0


def test_solver_prefers_higher_scoring_segmentation() -> None:
	dictionary = MorseDictionary([
		"e",
		"t",
		"et",
	])

	scorer = FrequencyScorer({
		"e": 1.0,
		"t": 1.0,
		"et": 5.0,
	})

	solver = MorseSolver(
		InternationalMorse(),
		dictionary,
		scorer,
	)

	sequence = encode_unspaced("et")

	result = solver.solve(sequence)

	assert result is not None
	assert result.text == "et"
	assert result.score == 5.0


def test_contextual_solver_uses_previous_word() -> None:
	dictionary = MorseDictionary([
		"new",
		"york",
		"cat",
	])

	scorer = BigramScorer({
		("new", "york"): 10.0,
		("new", "cat"): 1.0,
	})

	solver = MorseSolver(
		InternationalMorse(),
		dictionary,
		scorer,
	)

	sequence = encode_unspaced("newyork")

	result = solver.solve(sequence)

	assert result is not None
	assert result.text == "new york"


def test_solver_rejects_invalid_beam_width() -> None:
	dictionary = MorseDictionary(["hello"])
	scorer = DictionaryScorer(dictionary)

	try:
		MorseSolver(
			InternationalMorse(),
			dictionary,
			scorer,
			beam_width=0,
		)
	except ValueError:
		pass
	else:
		raise AssertionError(
			"Expected ValueError"
	)


def test_context_free_solver_does_not_reject_repeated_words() -> None:
	dictionary = MorseDictionary([
		"the",
		"cat",
	])

	solver = MorseSolver(
		InternationalMorse(),
		dictionary,
		DictionaryScorer(dictionary),
	)

	sequence = encode_unspaced("thethecat")

	result = solver.solve(sequence)

	assert result is not None
	assert result.text == "the the cat"
