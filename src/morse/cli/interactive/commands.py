"""Command parsing and execution for the interactive shell."""

from __future__ import annotations

import shlex

from rich.console import Console
from rich.table import Table

from morse import Morse
from morse.parsing import MorseBoundarySyntax, SpacedParser
from morse.solving import (
	DictionaryScorer,
	EnglishFrequencyScorer,
	MorseDictionary,
	MorseSolver,
)

from morse.cli.interactive.config import InteractiveConfig
from morse.cli.interactive.paths import expand_path


class InteractiveCommandRunner:
	"""Parses and executes commands for the interactive Morse shell.

	Expensive Morse solvers are cached for the lifetime of the interactive
	session. The cache is automatically invalidated when its dictionary or
	solver configuration changes.
	"""

	def __init__(
		self,
		morse: Morse,
		console: Console,
		config: InteractiveConfig,
	) -> None:
		"""Initializes the command runner.

		Args:
			morse: The MorseToolkit instance used to execute commands.
			console: Rich console used for interactive output.
			config: Persistent interactive shell configuration.
		"""
		self.morse = morse
		self.console = console
		self.config = config

		self._solver_cache: dict[
			tuple[str, int, int, int, int, str],
			MorseSolver,
		] = {}

	def run(self, line: str) -> bool:
		"""Parses and executes a single interactive command.

		Args:
			line: The raw command line entered by the user.

		Returns:
			False when the shell should exit, otherwise True.
		"""
		try:
			parts = shlex.split(line)
		except ValueError as exc:
			self.console.print(f"[red]Parse error:[/red] {exc}")
			return True

		if not parts:
			return True

		command = parts[0].lower()
		args = parts[1:]

		if command in {"exit", "quit"}:
			return False

		if command == "help":
			self.help()
			return True

		if command == "clear":
			self.console.clear()
			return True

		if command == "history":
			self._history()
			return True

		try:
			self._dispatch(
				command,
				args,
				self._raw_arguments(line),
			)
		except Exception as exc:
			self.console.print(f"[red]Error:[/red] {exc}")

		return True

	def _raw_arguments(self, line: str) -> str:
		"""Extracts the original argument text without collapsing whitespace.

		Args:
			line: The raw command line.

		Returns:
			The argument portion of the command with its original whitespace.
		"""
		stripped = line.lstrip()

		if not stripped:
			return ""

		index = 0

		while index < len(stripped) and not stripped[index].isspace():
			index += 1

		while index < len(stripped) and stripped[index].isspace():
			index += 1

		return stripped[index:]

	def _dispatch(
		self,
		command: str,
		args: list[str],
		raw_args: str,
	) -> None:
		"""Dispatches a parsed command to its implementation."""
		if command == "encode":
			self._encode(args)
		elif command == "decode":
			self._decode(raw_args)
		elif command == "solve":
			self._solve(args)
		elif command == "parse":
			self._parse(raw_args)
		elif command == "validate":
			self._validate(raw_args)
		elif command == "set":
			self._set(args)
		elif command == "reset":
			self._reset()
		elif command == "show":
			self._show()
		else:
			self.console.print(
				f"[yellow]Unknown command:[/yellow] {command}. "
				"Type [bold]help[/bold] for available commands."
			)

	def _encode(self, args: list[str]) -> None:
		"""Encodes plain text supplied to the interactive command.

		Args:
			args: Command arguments containing the text to encode.
		"""
		if not args:
			raise ValueError("Usage: encode <text>")

		value = " ".join(args)
		self.console.print(self.morse.encode(value))

	def _decode(self, value: str) -> None:
		"""Decodes spaced Morse supplied to the interactive command.

		Args:
			value: The Morse representation to decode.
		"""
		if not value.strip():
			raise ValueError("Usage: decode <morse>")

		self.console.print(self.morse.decode(value))

	def _solve(self, args: list[str]) -> None:
		"""Solves unspaced Morse using the configured dictionary and scorer.

		The configured result count is used by default. A positive integer may
		be supplied as the final argument to override the result count for only
		the current command.

		Examples:
			``solve ......-...-..---``
			``solve ......-...-..--- 20``

		Args:
			args: Morse input followed optionally by a temporary result limit.
		"""
		if not args:
			raise ValueError("Usage: solve <unspaced-morse> [results]")

		value = args[0]
		limit = self.config.results

		if len(args) > 2:
			raise ValueError("Usage: solve <unspaced-morse> [results]")

		if len(args) == 2:
			try:
				limit = int(args[1])
			except ValueError as exc:
				raise ValueError("Result count must be an integer") from exc

			if limit < 1:
				raise ValueError("Result count must be at least 1")

		solver = self._get_solver()
		sequence = self.morse.parse_unspaced(value)

		results = solver.solve_candidates(
			sequence,
			limit=limit,
		)

		if not results:
			self.console.print("[yellow]No solution found.[/yellow]")
			return

		for index, result in enumerate(results, 1):
			self.console.print(f"{index}. {result.text}")

	def _get_solver(self) -> MorseSolver:
		"""Returns the cached solver for the current configuration.

		Returns:
			A configured and potentially cached MorseSolver.

		Raises:
			ValueError: If no dictionary is configured or the dictionary is
				invalid.
		"""
		if not self.config.dictionary:
			raise ValueError(
				"No dictionary configured. Use: set dictionary <path>"
			)

		path = expand_path(self.config.dictionary).resolve()

		if not path.exists():
			raise ValueError(f"Dictionary does not exist: {path}")

		if not path.is_file():
			raise ValueError(f"Dictionary is not a file: {path}")

		try:
			stat = path.stat()
		except OSError as exc:
			raise ValueError(f"Unable to access dictionary: {path}") from exc

		cache_key = (
			str(path),
			stat.st_mtime_ns,
			stat.st_size,
			self.morse.max_word_length,
			self.morse.beam_width,
			self.config.scorer,
		)

		solver = self._solver_cache.get(cache_key)

		if solver is not None:
			return solver

		words = (
			line.strip()
			for line in path.read_text(encoding="utf-8").splitlines()
			if line.strip()
		)

		morse_dict = self.morse.dictionary(words)
		scorer = self._create_scorer(morse_dict)

		solver = MorseSolver(
			self.morse.alphabet,
			morse_dict,
			scorer,
			max_word_length=self.morse.max_word_length,
			beam_width=self.morse.beam_width,
		)

		self._solver_cache = {
			key: cached
			for key, cached in self._solver_cache.items()
			if key[0] != str(path)
		}

		self._solver_cache[cache_key] = solver

		return solver

	def _create_scorer(
		self,
		dictionary: MorseDictionary,
	):
		"""Creates the scorer selected by interactive configuration.

		Args:
			dictionary: Dictionary available to the solver.

		Returns:
			The configured scorer.

		Raises:
			ValueError: If the selected scorer cannot be initialized.
		"""
		if self.config.scorer == "dictionary":
			return DictionaryScorer(dictionary)

		if self.config.scorer == "english":
			try:
				return EnglishFrequencyScorer()
			except ImportError as exc:
				raise ValueError(str(exc)) from exc

		raise ValueError(f"Unknown scorer: {self.config.scorer}")

	def _parse(self, value: str) -> None:
		"""Parses and displays the tokens in a Morse input.

		Args:
			value: The Morse representation to parse.
		"""
		if not value.strip():
			raise ValueError("Usage: parse <morse>")

		stream = self.morse.parse(value)

		for token in stream:
			self.console.print(f"{token.type.name.lower():<20} {token}")

	def _validate(self, value: str) -> None:
		"""Validates a spaced Morse input.

		Args:
			value: The Morse representation to validate.
		"""
		if not value.strip():
			raise ValueError("Usage: validate <morse>")

		self.morse.parse(value)
		self.console.print("[green]Valid Morse.[/green]")

	def _set(self, args: list[str]) -> None:
		"""Changes and persists an interactive configuration setting.

		Args:
			args: Setting name followed by its new value.
		"""
		if len(args) < 2:
			raise ValueError("Usage: set <setting> <value>")

		setting = args[0].lower()
		value = " ".join(args[1:])

		if setting == "dictionary":
			self._set_dictionary(value)
		elif setting in {"results", "limit"}:
			self._set_results(value)
		elif setting == "scorer":
			self._set_scorer(value)
		elif setting in {"word-boundary", "word_boundary"}:
			self._set_word_boundary(value)
		elif setting in {"character-boundary", "character_boundary"}:
			self._set_character_boundary(value)
		elif setting in {"max-word-length", "max_word_length"}:
			self._set_max_word_length(value)
		elif setting in {"beam-width", "beam_width"}:
			self._set_beam_width(value)
		elif setting in {"history", "history-enabled", "history_enabled"}:
			self._set_history(value)
		else:
			raise ValueError(f"Unknown setting: {setting}")

	def _set_dictionary(self, value: str) -> None:
		"""Sets and persists the dictionary path."""
		path = expand_path(value).resolve()

		if not path.exists():
			raise ValueError(f"Dictionary does not exist: {path}")

		if not path.is_file():
			raise ValueError(f"Dictionary is not a file: {path}")

		self.config.dictionary = str(path)
		self.config.save()
		self._solver_cache.clear()

		self.console.print(f"[green]Dictionary set to:[/green] {path}")

	def _set_results(self, value: str) -> None:
		"""Sets and persists the default result count."""
		try:
			results = int(value)
		except ValueError as exc:
			raise ValueError("Result count must be an integer") from exc

		if results < 1:
			raise ValueError("Result count must be at least 1")

		self.config.results = results
		self.config.save()

		self.console.print(
			f"[green]Default result count set to:[/green] {results}"
		)

	def _set_scorer(self, value: str) -> None:
		"""Sets and persists the solver scorer."""
		scorer = value.lower()

		if scorer not in {"english", "dictionary"}:
			raise ValueError("Scorer must be 'english' or 'dictionary'")

		self.config.scorer = scorer
		self.config.save()
		self._solver_cache.clear()

		self.console.print(f"[green]Scorer set to:[/green] {scorer}")

	def _set_word_boundary(self, value: str) -> None:
		"""Sets and persists the Morse word boundary."""
		self._set_boundaries(
			character_boundary=self.config.character_boundary,
			word_boundary=value,
		)

		self.console.print(f"[green]Word boundary set to:[/green] {value!r}")

	def _set_character_boundary(self, value: str) -> None:
		"""Sets and persists the Morse character boundary."""
		self._set_boundaries(
			character_boundary=value,
			word_boundary=self.config.word_boundary,
		)

		self.console.print(
			f"[green]Character boundary set to:[/green] {value!r}"
		)

	def _set_boundaries(
		self,
		character_boundary: str,
		word_boundary: str,
	) -> None:
		"""Applies and persists a new Morse boundary configuration."""
		boundaries = MorseBoundarySyntax(
			character_boundary=character_boundary,
			word_boundary=word_boundary,
		)

		self.config.character_boundary = boundaries.character_boundary
		self.config.word_boundary = boundaries.word_boundary

		self.morse.boundaries = boundaries
		self.morse.spaced_parser = SpacedParser(
			self.morse.representation,
			boundaries,
		)

		self.config.save()

	def _set_max_word_length(self, value: str) -> None:
		"""Sets and persists the maximum solver word length."""
		try:
			length = int(value)
		except ValueError as exc:
			raise ValueError("Maximum word length must be an integer") from exc

		if length < 1:
			raise ValueError("Maximum word length must be at least 1")

		self.config.max_word_length = length
		self.morse.max_word_length = length
		self.config.save()
		self._solver_cache.clear()

		self.console.print(f"[green]Max word length set to:[/green] {length}")

	def _set_beam_width(self, value: str) -> None:
		"""Sets and persists the solver beam width."""
		try:
			width = int(value)
		except ValueError as exc:
			raise ValueError("Beam width must be an integer") from exc

		if width < 1:
			raise ValueError("Beam width must be at least 1")

		self.config.beam_width = width
		self.morse.beam_width = width
		self.config.save()
		self._solver_cache.clear()

		self.console.print(f"[green]Beam width set to:[/green] {width}")

	def _set_history(self, value: str) -> None:
		"""Sets and persists whether command history is enabled."""
		normalized = value.lower()

		if normalized in {"on", "true", "yes", "1", "enabled"}:
			enabled = True
		elif normalized in {"off", "false", "no", "0", "disabled"}:
			enabled = False
		else:
			raise ValueError("History must be on or off")

		self.config.history_enabled = enabled
		self.config.save()

		self.console.print(
			f"[green]History {'enabled' if enabled else 'disabled'}.[/green]"
		)
		self.console.print(
			"[dim]Restart the shell for the history mode change to take effect.[/dim]"
		)

	def _reset(self) -> None:
		"""Restores interactive configuration to its defaults."""
		self.config.reset()

		self.morse.boundaries = MorseBoundarySyntax(
			character_boundary=self.config.character_boundary,
			word_boundary=self.config.word_boundary,
		)
		self.morse.spaced_parser = SpacedParser(
			self.morse.representation,
			self.morse.boundaries,
		)
		self.morse.max_word_length = self.config.max_word_length
		self.morse.beam_width = self.config.beam_width

		self._solver_cache.clear()
		self.config.save()

		self.console.print(
			"[green]Interactive configuration reset to defaults.[/green]"
		)

	def _history(self) -> None:
		"""Displays the current history configuration."""
		status = "enabled" if self.config.history_enabled else "disabled"

		self.console.print(
			f"History is [bold]{status}[/bold]. Use ↑/↓ or Ctrl-R to search history."
		)

	def _show(self) -> None:
		"""Displays the current MorseToolkit configuration."""
		table = Table(title="MorseToolkit")
		table.add_column("Setting")
		table.add_column("Value")

		table.add_row(
			"Alphabet",
			type(self.morse.alphabet).__name__,
		)
		table.add_row(
			"Representation",
			type(self.morse.representation).__name__,
		)
		table.add_row(
			"Character boundary",
			repr(self.config.character_boundary),
		)
		table.add_row(
			"Word boundary",
			repr(self.config.word_boundary),
		)
		table.add_row(
			"Dictionary",
			self.config.dictionary or "[dim]not configured[/dim]",
		)
		table.add_row(
			"Scorer",
			self.config.scorer,
		)
		table.add_row(
			"Results",
			str(self.config.results),
		)
		table.add_row(
			"Max word length",
			str(self.config.max_word_length),
		)
		table.add_row(
			"Beam width",
			str(self.config.beam_width),
		)
		table.add_row(
			"History",
			"enabled" if self.config.history_enabled else "disabled",
		)

		self.console.print(table)

	def help(self) -> None:
		"""Displays the available interactive commands."""
		table = Table(title="Commands")
		table.add_column("Command", style="bold")
		table.add_column("Description")

		table.add_row(
			"encode <text>",
			"Encode plain text.",
		)
		table.add_row(
			"decode <morse>",
			"Decode spaced Morse.",
		)
		table.add_row(
			"solve <morse> [results]",
			"Solve unspaced Morse using configured settings.",
		)
		table.add_row(
			"parse <morse>",
			"Inspect parsed tokens.",
		)
		table.add_row(
			"validate <morse>",
			"Validate spaced Morse.",
		)
		table.add_row(
			"set <setting> <value>",
			"Change and save an interactive setting.",
		)
		table.add_row(
			"show",
			"Show current configuration.",
		)
		table.add_row(
			"reset",
			"Restore default configuration.",
		)
		table.add_row(
			"clear",
			"Clear the terminal.",
		)
		table.add_row(
			"history",
			"Show history status.",
		)
		table.add_row(
			"help",
			"Show this help.",
		)
		table.add_row(
			"exit / quit",
			"Leave the shell.",
		)

		self.console.print(table)
