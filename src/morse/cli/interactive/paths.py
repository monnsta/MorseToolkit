"""Filesystem path helpers for the interactive shell."""

from __future__ import annotations

import os
from pathlib import Path


def data_directory() -> Path:
	"""Return the platform-appropriate MorseToolkit data directory."""
	from platformdirs import user_data_dir

	path = Path(user_data_dir("morse"))
	path.mkdir(
		parents=True,
		exist_ok=True,
	)
	return path


def config_path() -> Path:
	"""Return the persistent interactive configuration path."""
	return data_directory() / "config.json"


def expand_path(value: str) -> Path:
	"""Expand shell-style user and environment references.

	Args:
		value: Path containing optional environment variables or ``~``.

	Returns:
		The expanded filesystem path.
	"""
	return Path(os.path.expandvars(os.path.expanduser(value)))


def path_completions(value: str) -> list[str]:
	"""Return filesystem completion candidates while preserving user syntax.

	Args:
		value: The incomplete filesystem path.

	Returns:
		Matching files and directories.
	"""
	if not value:
		value = "."

	expanded = os.path.expandvars(os.path.expanduser(value))

	path = Path(expanded)

	if value.endswith(("/", "\\")):
		directory = path
		prefix = ""
	else:
		directory = path.parent
		prefix = path.name

	if not directory.exists() or not directory.is_dir():
		return []

	try:
		entries = sorted(
			directory.iterdir(),
			key=lambda entry: (
				not entry.is_dir(),
				entry.name.lower(),
			),
		)
	except OSError:
		return []

	result: list[str] = []

	for entry in entries:
		if prefix and not entry.name.startswith(prefix):
			continue

		display = _replace_path_component(
			value,
			entry.name,
		)

		if entry.is_dir():
			display += "/"

		result.append(display)

	return result


def _replace_path_component(
	value: str,
	name: str,
) -> str:
	"""Replace the incomplete final path component."""
	if value.endswith(("/", "\\")):
		return f"{value}{name}"

	index = max(
		value.rfind("/"),
		value.rfind("\\"),
	)

	if index == -1:
		return name

	return f"{value[: index + 1]}{name}"
