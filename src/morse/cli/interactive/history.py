"""Persistent history support for the interactive shell."""

from __future__ import annotations

from pathlib import Path

from morse.cli.interactive.paths import data_directory


def history_path() -> Path:
	"""Return the platform-appropriate MorseToolkit history path."""
	path = data_directory()
	return path / "history"
