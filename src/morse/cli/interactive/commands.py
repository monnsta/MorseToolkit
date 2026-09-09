"""Command parsing and execution for the interactive shell."""

from __future__ import annotations

import shlex
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from morse import Morse

from morse.cli.commands.decode import decode_command
from morse.cli.commands.encode import encode_command
from morse.cli.commands.parse import parse_command
from morse.cli.commands.solve import solve_command
from morse.cli.commands.validate import validate_command


class InteractiveCommandRunner:
	def __init__(self, morse: Morse, console: Console) -> None:
		self.morse = morse
		self.console = console

	def run(self, line: str) -> bool:
		try:
			parts = shlex.split(line)
		except ValueError as exc:
			self.console.print(f"[red]Parse error:[/red] {exc}")
			return True

		if not parts:
			return True

		command, args = parts[0].lower(), parts[1:]

		if command in {"exit", "quit"}:
			return False

		if command == "help":
			self.help()
			return True

		if command == "clear":
			self.console.clear()
			return True

		if command == "history":
			self.console.print(
				"[dim]Use the ↑/↓ keys or Ctrl-R to search command history.[/dim]"
			)
			return True

		try:
			self._dispatch(command, args)
		except Exception as exc:
			self.console.print(f"[red]Error:[/red] {exc}")

		return True

	def _dispatch(self, command: str, args: list[str]) -> None:
		if command == "encode":
			self._encode(args)
		elif command == "decode":
			self._decode(args)
		elif command == "solve":
			self._solve(args)
		elif command == "parse":
			self._parse(args)
		elif command == "validate":
			self._validate(args)
		elif command == "show":
			self._show()
		else:
			self.console.print(
				f"[yellow]Unknown command:[/yellow] {command}. "
				"Type [bold]help[/bold] for available commands."
			)

	def _encode(self, args: list[str]) -> None:
		if not args:
			raise ValueError("Usage: encode <text>")

		value = " ".join(args)
		self.console.print(self.morse.encode(value))

	def _decode(self, args: list[str]) -> None:
		if not args:
			raise ValueError("Usage: decode <morse>")

		self.console.print(self.morse.decode(" ".join(args)))

	def _solve(self, args: list[str]) -> None:
		if not args:
			raise ValueError("Usage: solve <unspaced-morse> <dictionary-file>")

		if len(args) < 2:
			raise ValueError("Usage: solve <unspaced-morse> <dictionary-file>")

		value = args[0]
		path = Path(args[1])

		words = (
			line.strip()
			for line in path.read_text(encoding="utf-8").splitlines()
			if line.strip()
		)

		result = self.morse.solve(value, dictionary=words)

		if result is None:
			self.console.print("[yellow]No solution found.[/yellow]")
		else:
			self.console.print(result.text)

	def _parse(self, args: list[str]) -> None:
		if not args:
			raise ValueError("Usage: parse <morse>")

		stream = self.morse.parse(" ".join(args))
		for token in stream:
			self.console.print(f"{token.type.name.lower():<20} {token}")

	def _validate(self, args: list[str]) -> None:
		if not args:
			raise ValueError("Usage: validate <morse>")

		self.morse.parse(" ".join(args))
		self.console.print("[green]Valid Morse.[/green]")

	def _show(self) -> None:
		table = Table(title="MorseToolkit")
		table.add_column("Setting")
		table.add_column("Value")
		table.add_row("Alphabet", type(self.morse.alphabet).__name__)
		table.add_row("Representation", type(self.morse.representation).__name__)
		table.add_row("Boundaries", type(self.morse.boundaries).__name__)
		table.add_row("Max word length", str(self.morse.max_word_length))
		table.add_row("Beam width", str(self.morse.beam_width))
		self.console.print(table)

	def help(self) -> None:
		table = Table(title="Commands")
		table.add_column("Command", style="bold")
		table.add_column("Description")
		table.add_row("encode <text>", "Encode plain text.")
		table.add_row("decode <morse>", "Decode spaced Morse.")
		table.add_row("solve <morse> <dict>", "Solve unspaced Morse.")
		table.add_row("parse <morse>", "Inspect parsed tokens.")
		table.add_row("validate <morse>", "Validate spaced Morse.")
		table.add_row("show", "Show current toolkit configuration.")
		table.add_row("clear", "Clear the terminal.")
		table.add_row("history", "Show history help.")
		table.add_row("help", "Show this help.")
		table.add_row("exit / quit", "Leave the shell.")
		self.console.print(table)
