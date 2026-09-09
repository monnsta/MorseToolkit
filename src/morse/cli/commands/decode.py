"""Decode command."""

from __future__ import annotations

import typer

from morse import Morse

from morse.cli.commands._input import resolve_input


def decode_command(
	value: str | None = typer.Argument(
		None,
		help="Spaced Morse to decode. If omitted, input is read from stdin.",
	),
) -> None:
	"""Decode boundary-delimited Morse code."""
	try:
		morse = Morse()
		result = morse.decode(resolve_input(value))
	except (ValueError, TypeError) as exc:
		raise typer.BadParameter(str(exc)) from exc

	typer.echo(result)
