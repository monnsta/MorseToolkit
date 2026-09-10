"""Modern interactive MorseToolkit shell."""

from __future__ import annotations

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel

from morse import Morse
from morse.parsing import MorseBoundarySyntax

from morse.cli.interactive.commands import InteractiveCommandRunner
from morse.cli.interactive.completer import MorseCompleter
from morse.cli.interactive.config import InteractiveConfig
from morse.cli.interactive.history import history_path


class InteractiveShell:
	"""Runs the persistent interactive MorseToolkit environment."""

	def __init__(self, morse: Morse | None = None) -> None:
		"""Initializes the interactive shell.

		Args:
			morse: Optional preconfigured Morse instance. When omitted,
				persistent interactive configuration is loaded automatically.
		"""
		self.console = Console()
		self.config = InteractiveConfig.load()

		if morse is None:
			morse = self._create_morse()

		self.morse = morse
		self.runner = InteractiveCommandRunner(
			self.morse,
			self.console,
			self.config,
		)

		history = None

		if self.config.history_enabled:
			history = FileHistory(
				str(history_path())
			)

		self.session = PromptSession(
			history=history,
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

	def _create_morse(self) -> Morse:
		"""Creates a Morse instance from persistent interactive settings.

		Returns:
			A configured Morse instance.
		"""
		boundaries = MorseBoundarySyntax(
			character_boundary=self.config.character_boundary,
			word_boundary=self.config.word_boundary,
		)

		return Morse(
			boundaries=boundaries,
			max_word_length=self.config.max_word_length,
			beam_width=self.config.beam_width,
		)

	def _key_bindings(self) -> KeyBindings:
		"""Creates the interactive keyboard bindings.

		Returns:
			Configured prompt-toolkit key bindings.
		"""
		bindings = KeyBindings()

		@bindings.add("c-l")
		def _(event) -> None:
			event.app.renderer.clear()

		@bindings.add("c-c")
		def _(event) -> None:
			event.app.current_buffer.reset()

		@bindings.add("c-d")
		def _(event) -> None:
			event.app.exit(exception=EOFError)

		return bindings

	def run(self) -> None:
		"""Runs the interactive shell until the user exits."""
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
