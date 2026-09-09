"""Persistent history support for the interactive shell."""

from __future__ import annotations

from pathlib import Path


def history_path() -> Path:
	"""Return the platform-appropriate MorseToolkit history path."""
	from platformdirs import user_data_dir

	path = Path(user_data_dir("morse"))
	path.mkdir(parents=True, exist_ok=True)
	return path / "history"
