"""Solve command."""

from __future__ import annotations

from pathlib import Path

import typer

from morse import Morse


def solve_command(
	value: str | None = typer.Argument(
		None,
		help="Unspaced Morse to solve. If omitted, input is read from stdin.",
	),
	dictionary: Path = typer.Option(
		...,
		"--dictionary",
		"-d",
		exists=True,
		file_okay=True,
		dir_okay=False,
		readable=True,
		resolve_path=True,
		help="Path to a newline-separated word dictionary.",
	),
	max_word_length: int = typer.Option(
		32,
		"--max-word-length",
		min=1,
		help="Maximum dictionary word length.",
	),
	beam_width: int = typer.Option(
		8,
		"--beam-width",
		min=1,
		help="Solver beam width.",
	),
) -> None:
	"""Solve continuous Morse by inferring character boundaries."""
	try:
		if value is None:
			import sys
			if sys.stdin.isatty():
				raise ValueError(
					"No Morse input supplied. Pass a value or pipe Morse through stdin."
				)
			value = sys.stdin.read().rstrip("\n")

		words = (
			line.strip()
			for line in dictionary.read_text(encoding="utf-8").splitlines()
			if line.strip()
		)

		result = Morse().solve(
			value,
			dictionary=words,
			max_word_length=max_word_length,
			beam_width=beam_width,
		)

		if result is None:
			typer.echo("No solution found.", err=True)
			raise typer.Exit(code=1)

	except (ValueError, TypeError, OSError) as exc:
		raise typer.BadParameter(str(exc)) from exc

	typer.echo(result.text)
