"""Interactive command completion."""

from __future__ import annotations

from prompt_toolkit.completion import Completer, Completion


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
	"exit",
	"quit",
)


class MorseCompleter(Completer):
	def get_completions(self, document, complete_event):
		text = document.text_before_cursor

		if text.startswith(" "):
			return

		word = text.split()[-1] if text.split() else text

		for command in COMMANDS:
			if command.startswith(word):
				yield Completion(
					command,
					start_position=-len(word),
				)
