"""Interactive command completion."""

from __future__ import annotations

from prompt_toolkit.completion import Completer, Completion

from morse.cli.interactive.paths import path_completions


COMMANDS = (
	"encode",
	"decode",
	"solve",
	"parse",
	"validate",
	"help",
	"clear",
	"history",
	"set",
	"show",
	"reset",
	"exit",
	"quit",
)

SETTINGS = (
	"dictionary",
	"results",
	"scorer",
	"word-boundary",
	"character-boundary",
	"max-word-length",
	"beam-width",
	"history",
)

SCORERS = (
	"english",
	"dictionary",
)

HISTORY_VALUES = (
	"on",
	"off",
)


class MorseCompleter(Completer):
	"""Provides completion for interactive commands and settings."""

	def get_completions(self, document, complete_event):
		"""Yields completion candidates for the current prompt.

		Args:
			document: Current prompt-toolkit document.
			complete_event: Prompt-toolkit completion event.
		"""
		_ = complete_event
		text = document.text_before_cursor

		if not text.strip():
			for command in COMMANDS:
				yield Completion(
					command,
					start_position=0,
				)
			return

		parts = text.split()

		if len(parts) == 1 and not text.endswith(" "):
			word = parts[0]

			for command in COMMANDS:
				if command.startswith(word):
					yield Completion(
						command,
						start_position=-len(word),
					)

			return

		command = parts[0].lower()
		arguments = parts[1:]

		if command == "set":
			yield from self._complete_set(
				arguments,
				text,
			)
			return

		if command == "solve":
			yield from self._complete_solve(
				arguments,
			)

	def _complete_set(
		self,
		arguments: list[str],
		text: str,
	):
		"""Completes setting names and setting values."""
		if not arguments:
			for setting in SETTINGS:
				yield Completion(
					setting,
					start_position=0,
				)
			return

		if len(arguments) == 1 and not text.endswith(" "):
			value = arguments[0]

			for setting in SETTINGS:
				if setting.startswith(value):
					yield Completion(
						setting,
						start_position=-len(value),
					)

			return

		setting = arguments[0].lower()
		value = arguments[-1] if len(arguments) > 1 else ""

		if setting == "dictionary":
			for candidate in path_completions(value):
				yield Completion(
					candidate,
					start_position=-len(value),
				)
			return

		if setting == "scorer":
			for scorer in SCORERS:
				if scorer.startswith(value):
					yield Completion(
						scorer,
						start_position=-len(value),
					)
			return

		if setting == "history":
			for option in HISTORY_VALUES:
				if option.startswith(value.lower()):
					yield Completion(
						option,
						start_position=-len(value),
					)

	def _complete_solve(
		self,
		arguments: list[str],
	):
		"""Completes the optional solve result count."""
		if len(arguments) == 1:
			yield Completion(
				"10",
				start_position=0,
				display="10 results",
			)
			yield Completion(
				"20",
				start_position=0,
				display="20 results",
			)
			yield Completion(
				"50",
				start_position=0,
				display="50 results",
			)
