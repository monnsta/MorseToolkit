from morse.alphabets import InternationalMorse
from morse.core import MorseSequence, MorseSymbol, MorseSegmentation
from morse.parsing import UnspacedParser
from morse.representations import TextRepresentation
from morse.solving.segmenter import MorseSegmenter


def test_segment_single_character():
	parser = UnspacedParser(TextRepresentation())
	sequence = parser.parse("....")

	segmenter = MorseSegmenter(InternationalMorse())

	results = list(segmenter.segment(sequence))

	assert (
		MorseSegmentation(
			(
				(
					MorseSymbol.DOT,
					MorseSymbol.DOT,
					MorseSymbol.DOT,
					MorseSymbol.DOT,
				),
			)
		)
		in results
	)


def test_segment_hello():
	parser = UnspacedParser(TextRepresentation())
	sequence = parser.parse("......-...-..---")

	segmenter = MorseSegmenter(InternationalMorse())

	results = list(segmenter.segment(sequence))

	assert any(
		result.characters
		== (
			(
				MorseSymbol.DOT,
				MorseSymbol.DOT,
				MorseSymbol.DOT,
				MorseSymbol.DOT,
			),
			(MorseSymbol.DOT,),
			(
				MorseSymbol.DOT,
				MorseSymbol.DASH,
				MorseSymbol.DOT,
				MorseSymbol.DOT,
			),
			(
				MorseSymbol.DOT,
				MorseSymbol.DASH,
				MorseSymbol.DOT,
				MorseSymbol.DOT,
			),
			(
				MorseSymbol.DASH,
				MorseSymbol.DASH,
				MorseSymbol.DASH,
			),
		)
		for result in results
	)


def test_segment_uses_only_valid_morse_characters():
	sequence = MorseSequence(
		(
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		)
	)

	segmenter = MorseSegmenter(InternationalMorse())

	results = list(segmenter.segment(sequence))

	assert results
	assert all(
		all(
			InternationalMorse().can_decode(character)
			for character in result.characters
		)
		for result in results
	)


def test_segment_empty_sequence():
	segmenter = MorseSegmenter(InternationalMorse())

	results = list(segmenter.segment(MorseSequence(())))

	assert results == [MorseSegmentation(())]


def test_segment_respects_maximum_character_length():
	sequence = MorseSequence(
		(
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
			MorseSymbol.DOT,
		)
	)

	segmenter = MorseSegmenter(
		InternationalMorse(),
		max_character_length=3,
	)

	results = list(segmenter.segment(sequence))

	assert all(
		all(len(character) <= 3 for character in result) for result in results
	)


def test_invalid_maximum_character_length():
	try:
		MorseSegmenter(
			InternationalMorse(),
			max_character_length=0,
		)
	except ValueError:
		pass
	else:
		raise AssertionError("Expected ValueError")
