"""Encode command."""

from __future__ import annotations

import typer

from morse import Morse

from morse.cli.commands._input import resolve_input


def encode_command(
	text: str | None = typer.Argument(
		None,
		help="Text to encode. If omitted, text is read from stdin.",
	),
	unspaced: bool = typer.Option(
		False,
		"--unspaced",
		help="Encode without character or word boundaries.",
	),
) -> None:
	"""Encode plain text into Morse code."""
	try:
		value = resolve_input(text)
		morse = Morse()
		result = (
			morse.encode_unspaced(value) if unspaced else morse.encode(value)
		)
	except (ValueError, TypeError) as exc:
		raise typer.BadParameter(str(exc)) from exc

	typer.echo(result)
