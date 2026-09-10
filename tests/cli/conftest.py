"""Shared fixtures for MorseToolkit CLI tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
	"""Return a Typer CLI test runner."""
	return CliRunner()


@pytest.fixture
def dictionary_file(tmp_path: Path) -> Path:
	"""Create a small deterministic Morse dictionary for solver tests."""
	path = tmp_path / "dictionary.txt"
	path.write_text(
		"hello\n"
		"there\n"
		"help\n"
		"her\n"
		"hell\n"
		"he\n"
		"the\n"
		"other\n",
		encoding="utf-8",
	)
	return path
