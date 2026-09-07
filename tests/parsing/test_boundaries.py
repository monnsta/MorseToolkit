import pytest

from morse.parsing.boundaries import MorseBoundarySyntax


def test_default_boundaries() -> None:
	boundaries = MorseBoundarySyntax()

	assert boundaries.character_boundary == " "
	assert boundaries.word_boundary == "   "


def test_custom_boundaries() -> None:
	boundaries = MorseBoundarySyntax(
		character_boundary="|",
		word_boundary="||",
	)

	assert boundaries.character_boundary == "|"
	assert boundaries.word_boundary == "||"


def test_character_boundary_cannot_be_empty() -> None:
	with pytest.raises(ValueError, match="Character boundary cannot be empty"):
		MorseBoundarySyntax(character_boundary="")


def test_word_boundary_cannot_be_empty() -> None:
	with pytest.raises(ValueError, match="Word boundary cannot be empty"):
		MorseBoundarySyntax(word_boundary="")


def test_boundaries_must_be_different() -> None:
	with pytest.raises(
		ValueError,
		match="Character and word boundaries must be different",
	):
		MorseBoundarySyntax(
			character_boundary="|",
			word_boundary="|",
		)
