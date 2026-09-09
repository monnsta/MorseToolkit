"""Parse command."""

from __future__ import annotations

import typer

from morse import Morse
from morse.core import MorseTokenType

from morse.cli.commands._input import resolve_input


def parse_command(
	value: str | None = typer.Argument(
		None,
		help="Spaced Morse to parse. If omitted, input is read from stdin.",
	),
) -> None:
	"""Inspect the structured token stream produced from spaced Morse."""
	try:
		stream = Morse().parse(resolve_input(value))
	except (ValueError, TypeError) as exc:
		raise typer.BadParameter(str(exc)) from exc

	for token in stream:
		if token.type is MorseTokenType.SYMBOL:
			detail = repr(token.symbol)
		elif token.type is MorseTokenType.CHARACTER_BOUNDARY:
			detail = "character boundary"
		elif token.type is MorseTokenType.WORD_BOUNDARY:
			detail = "word boundary"
		else:
			detail = repr(token.type)

		typer.echo(f"{token.type.name.lower():<20} {detail}")
