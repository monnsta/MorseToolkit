"""Validate command."""

from __future__ import annotations

import typer

from morse import Morse

from morse.cli.commands._input import resolve_input


def validate_command(
	value: str | None = typer.Argument(
		None,
		help="Morse to validate. If omitted, input is read from stdin.",
	),
	unspaced: bool = typer.Option(
		False,
		"--unspaced",
		help="Validate as continuous Morse instead of boundary-delimited Morse.",
	),
) -> None:
	"""Validate Morse syntax using the toolkit's parsers."""
	try:
		morse = Morse()
		text = resolve_input(value)

		if unspaced:
			morse.parse_unspaced(text)
		else:
			morse.parse(text)

	except (ValueError, TypeError) as exc:
		typer.echo(f"Invalid Morse: {exc}" if "No input supplied" not in str(exc) else str(exc))
		raise typer.Exit(code=1) from exc

	typer.echo("Valid Morse.")
