"""Modern interactive MorseToolkit shell."""

from __future__ import annotations

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel

from morse import Morse

from morse.cli.interactive.completer import MorseCompleter
from morse.cli.interactive.commands import InteractiveCommandRunner
from morse.cli.interactive.history import history_path


class InteractiveShell:
	def __init__(self, morse: Morse | None = None) -> None:
		self.morse = morse or Morse()
		self.console = Console()
		self.runner = InteractiveCommandRunner(self.morse, self.console)

		self.session = PromptSession(
			history=FileHistory(str(history_path())),
			completer=MorseCompleter(),
			complete_while_typing=True,
			multiline=False,
			key_bindings=self._key_bindings(),
			style=Style.from_dict(
				{
					"prompt": "ansigreen bold",
				}
			),
		)

	def _key_bindings(self) -> KeyBindings:
		bindings = KeyBindings()

		@bindings.add("c-l")
		def clear(event) -> None:
			event.app.renderer.clear()

		@bindings.add("c-c")
		def cancel(event) -> None:
			event.app.current_buffer.reset()

		@bindings.add("c-d")
		def exit_shell(event) -> None:
			event.app.exit(exception=EOFError)

		return bindings

	def run(self) -> None:
		self.console.print(
			Panel.fit(
				"[bold]MorseToolkit[/bold]\n"
				"[dim]Interactive Morse environment[/dim]\n\n"
				"Type [bold]help[/bold] for commands. "
				"Use ↑/↓ for history and Ctrl-R for reverse history search.",
				title="Morse",
			)
		)

		while True:
			try:
				line = self.session.prompt(
					[("class:prompt", "morse> ")]
				)
			except (EOFError, KeyboardInterrupt):
				self.console.print()
				break

			if not self.runner.run(line):
				break

		self.console.print("[dim]Goodbye.[/dim]")
