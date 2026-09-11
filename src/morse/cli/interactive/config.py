"""Persistent configuration for the interactive MorseToolkit shell."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from morse.parsing import MorseBoundarySyntax

from morse.cli.interactive.paths import config_path, expand_path


@dataclass(slots=True)
class InteractiveConfig:
	"""Stores persistent settings for the interactive MorseToolkit shell.

	Attributes:
		dictionary: Path to the dictionary used by the solve command.
		results: Default number of solver candidates to display.
		scorer: Name of the configured solver scorer.
		character_boundary: Representation used between Morse characters.
		word_boundary: Representation used between Morse words.
		max_word_length: Maximum dictionary word length considered by the solver.
		beam_width: Maximum contextual solver beam width.
		history_enabled: Whether interactive command history is persisted.
	"""

	dictionary: str | None = None
	results: int = 5
	scorer: str = "english"
	character_boundary: str = " "
	word_boundary: str = "   "
	max_word_length: int = 32
	beam_width: int = 8
	history_enabled: bool = True

	@classmethod
	def load(cls) -> "InteractiveConfig":
		"""Loads persistent configuration from disk.

		If the configuration file does not exist or cannot be decoded, default
		settings are returned.

		Returns:
			The loaded or default interactive configuration.
		"""
		path = config_path()

		if not path.exists():
			return cls()

		try:
			data = json.loads(path.read_text(encoding="utf-8"))
		except (OSError, json.JSONDecodeError):
			return cls()

		if not isinstance(data, dict):
			return cls()

		config = cls()

		for field in (
			"dictionary",
			"results",
			"scorer",
			"character_boundary",
			"word_boundary",
			"max_word_length",
			"beam_width",
			"history_enabled",
		):
			if field in data:
				setattr(
					config,
					field,
					data[field],
				)

		try:
			config.validate()
		except (TypeError, ValueError):
			return cls()

		return config

	def save(self) -> None:
		"""Writes the current configuration to persistent storage."""
		path = config_path()
		path.parent.mkdir(
			parents=True,
			exist_ok=True,
		)

		path.write_text(
			json.dumps(
				asdict(self),
				indent=2,
			)
			+ "\n",
			encoding="utf-8",
		)

	def reset(self) -> None:
		"""Restores all settings to their default values."""
		defaults = type(self)()

		for field in (
			"dictionary",
			"results",
			"scorer",
			"character_boundary",
			"word_boundary",
			"max_word_length",
			"beam_width",
			"history_enabled",
		):
			setattr(
				self,
				field,
				getattr(defaults, field),
			)

	def validate(self) -> None:
		"""Validates all interactive configuration values.

		Raises:
			ValueError: If any configuration value is invalid.
		"""
		if not isinstance(self.results, int) or self.results < 1:
			raise ValueError("Result count must be at least 1")

		if self.scorer not in {"english", "dictionary"}:
			raise ValueError("Scorer must be 'english' or 'dictionary'")

		if (
			not isinstance(self.max_word_length, int)
			or self.max_word_length < 1
		):
			raise ValueError("Maximum word length must be at least 1")

		if not isinstance(self.beam_width, int) or self.beam_width < 1:
			raise ValueError("Beam width must be at least 1")

		if not isinstance(self.character_boundary, str):
			raise ValueError("Character boundary must be a string")

		if not isinstance(self.word_boundary, str):
			raise ValueError("Word boundary must be a string")

		MorseBoundarySyntax(
			character_boundary=self.character_boundary,
			word_boundary=self.word_boundary,
		)

		if self.dictionary is not None:
			self.dictionary = str(expand_path(self.dictionary))

		if not isinstance(self.history_enabled, bool):
			raise ValueError("History enabled must be a boolean")
