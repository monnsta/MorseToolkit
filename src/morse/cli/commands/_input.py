"""Shared input helpers for CLI commands."""

from __future__ import annotations

import sys


def resolve_input(value: str | None) -> str:
	"""Return explicit input or consume stdin when it is being piped."""
	if value:
		return value

	if not sys.stdin.isatty():
		input_data = sys.stdin.read().rstrip("\n")
		if input_data:
			return input_data

	raise ValueError("No input supplied. Pass a value or pipe text through stdin.")


def fail(message: str) -> None:
	raise ValueError(message)
