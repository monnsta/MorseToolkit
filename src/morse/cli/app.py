"""Main command-line application for MorseToolkit."""

from __future__ import annotations

import sys

import typer

from morse.cli.commands.decode import decode_command
from morse.cli.commands.encode import encode_command
from morse.cli.commands.parse import parse_command
from morse.cli.commands.solve import solve_command
from morse.cli.commands.validate import validate_command
from morse.cli.interactive.shell import InteractiveShell

app = typer.Typer(
	name="morse",
	help="A flexible command-line interface for MorseToolkit.",
	no_args_is_help=False,
	add_completion=True,
	rich_markup_mode="rich",
)

app.command("encode")(encode_command)
app.command("decode")(decode_command)
app.command("solve")(solve_command)
app.command("parse")(parse_command)
app.command("validate")(validate_command)


@app.command("interactive")
@app.command("shell", hidden=True)
def interactive_command() -> None:
	"""Start the interactive MorseToolkit shell."""
	InteractiveShell().run()


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context) -> None:
	"""Work with Morse code from the command line."""
	if ctx.invoked_subcommand is not None:
		return

	if sys.stdin.isatty() and sys.stdout.isatty():
		InteractiveShell().run()
		return

	typer.echo(ctx.get_help())


def main() -> None:
	"""CLI entry point."""
	app()
