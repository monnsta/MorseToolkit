"""Solve command."""

from __future__ import annotations

from pathlib import Path

import typer

from morse import Morse
from morse.cli.commands._input import resolve_input
from morse.solving import EnglishFrequencyScorer


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
	limit: int = typer.Option(
		5,
		"--limit",
		"-n",
		min=1,
		help="Number of candidate interpretations to show.",
	),
) -> None:
	"""Solve continuous Morse by inferring character boundaries."""
	try:
		text = resolve_input(value)

		words = (
			line.strip()
			for line in dictionary.read_text(encoding="utf-8").splitlines()
			if line.strip()
		)

		toolkit = Morse()
		morse_dict = toolkit.dictionary(words)

		try:
			scorer = EnglishFrequencyScorer()
		except ImportError as exc:
			raise typer.BadParameter(str(exc)) from exc

		results = toolkit.solve_candidates(
			text,
			dictionary=morse_dict,
			scorer=scorer,
			max_word_length=max_word_length,
			beam_width=beam_width,
			limit=limit,
		)

		if not results:
			typer.echo("No solution found.", err=True)
			raise typer.Exit(code=1)

		for index, result in enumerate(results, 1):
			typer.echo(f"{index}. {result.text}")

	except typer.Exit:
		raise
	except (ValueError, TypeError, OSError) as exc:
		raise typer.BadParameter(str(exc)) from exc
