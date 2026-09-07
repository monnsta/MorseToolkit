import pytest

from morse.core import MorseSymbol
from morse.representations import ArbitraryRepresentation


def test_decode_single_symbol() -> None:
	representation = ArbitraryRepresentation({
		MorseSymbol.DOT: "dot",
		MorseSymbol.DASH: "dash",
	})

	assert representation.decode("dot") is MorseSymbol.DOT
	assert representation.decode("dash") is MorseSymbol.DASH


def test_decode_sequence_with_multi_character_symbols() -> None:
	representation = ArbitraryRepresentation({
		MorseSymbol.DOT: "dot",
		MorseSymbol.DASH: "dash",
	})

	assert representation.decode_sequence("dotdotdash") == (
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DASH,
	)


def test_decode_sequence_with_single_character_symbols() -> None:
	representation = ArbitraryRepresentation({
		MorseSymbol.DOT: "e",
		MorseSymbol.DASH: "r",
	})

	assert representation.decode_sequence("eer") == (
		MorseSymbol.DOT,
		MorseSymbol.DOT,
		MorseSymbol.DASH,
	)


def test_decode_sequence_rejects_invalid_value() -> None:
	representation = ArbitraryRepresentation({
		MorseSymbol.DOT: "dot",
		MorseSymbol.DASH: "dash",
	})

	with pytest.raises(ValueError, match="Invalid Morse representation"):
		representation.decode_sequence("dotwat")


def test_empty_representation_is_rejected() -> None:
	with pytest.raises(
		ValueError,
		match="Symbol representations cannot be empty",
	):
		ArbitraryRepresentation({
			MorseSymbol.DOT: "",
			MorseSymbol.DASH: "dash",
		})


def test_prefix_ambiguity_is_rejected() -> None:
	with pytest.raises(
		ValueError,
		match="cannot be prefixes of each other",
	):
		ArbitraryRepresentation({
			MorseSymbol.DOT: "d",
			MorseSymbol.DASH: "dot",
		})


def test_duplicate_representation_is_rejected() -> None:
	with pytest.raises(
		ValueError,
		match="must be different",
	):
		ArbitraryRepresentation({
			MorseSymbol.DOT: "x",
			MorseSymbol.DASH: "x",
		})


def test_missing_dot_is_rejected() -> None:
	with pytest.raises(
		ValueError,
		match="must define DOT",
	):
		ArbitraryRepresentation({
			MorseSymbol.DASH: "dash",
		})


def test_missing_dash_is_rejected() -> None:
	with pytest.raises(
		ValueError,
		match="must define DASH",
	):
		ArbitraryRepresentation({
			MorseSymbol.DOT: "dot",
		})
