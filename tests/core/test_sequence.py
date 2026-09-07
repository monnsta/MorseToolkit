from morse.core import MorseSequence, MorseSymbol


def test_sequence_stores_symbols():
	sequence = MorseSequence(
		(
			MorseSymbol.DOT,
			MorseSymbol.DASH,
			MorseSymbol.DOT,
		)
	)

	assert tuple(sequence) == (
		MorseSymbol.DOT,
		MorseSymbol.DASH,
		MorseSymbol.DOT,
	)


def test_sequence_length():
	sequence = MorseSequence(
		(
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		)
	)

	assert len(sequence) == 2


def test_sequence_indexing():
	sequence = MorseSequence(
		(
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		)
	)

	assert sequence[0] is MorseSymbol.DOT
	assert sequence[1] is MorseSymbol.DASH


def test_sequence_from_symbols():
	sequence = MorseSequence.from_symbols(
		[
			MorseSymbol.DOT,
			MorseSymbol.DASH,
		]
	)

	assert sequence.symbols == (
		MorseSymbol.DOT,
		MorseSymbol.DASH,
	)
