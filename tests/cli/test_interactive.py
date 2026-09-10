from pathlib import Path

from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document
from rich.console import Console

from morse import Morse
from morse.cli.interactive.commands import InteractiveCommandRunner
from morse.cli.interactive.completer import MorseCompleter
from morse.cli.interactive.config import InteractiveConfig


def test_interactive_config_defaults() -> None:
	config = InteractiveConfig()
	assert config.results == 5
	assert config.scorer == "english"
	assert config.history_enabled is True
	config.validate()


def test_interactive_config_validation_error() -> None:
	config = InteractiveConfig(results=0)
	try:
		config.validate()
		assert False, "Should have raised ValueError"
	except ValueError:
		pass


def test_interactive_command_runner_encode_and_decode() -> None:
	console = Console(record=True)
	config = InteractiveConfig()
	runner = InteractiveCommandRunner(Morse(), console, config)

	assert runner.run("encode hello") is True
	output = console.export_text()
	assert ".... . .-.. .-.. ---" in output

	console.clear()
	assert runner.run("decode .... . .-.. .-.. ---") is True
	output = console.export_text()
	assert "HELLO" in output


def test_interactive_command_runner_solve(
	dictionary_file: Path,
) -> None:
	console = Console(record=True)
	config = InteractiveConfig(dictionary=str(dictionary_file))
	runner = InteractiveCommandRunner(Morse(), console, config)

	assert runner.run("solve ......-...-..---") is True
	output = console.export_text()
	assert "1. hello" in output


def test_interactive_command_runner_settings() -> None:
	console = Console(record=True)
	config = InteractiveConfig()
	runner = InteractiveCommandRunner(Morse(), console, config)

	assert runner.run("set results 10") is True
	assert config.results == 10

	assert runner.run("show") is True
	assert runner.run("reset") is True
	assert config.results == 5


def test_interactive_command_runner_exit() -> None:
	console = Console()
	config = InteractiveConfig()
	runner = InteractiveCommandRunner(Morse(), console, config)

	assert runner.run("exit") is False
	assert runner.run("quit") is False


def test_completer_commands() -> None:
	completer = MorseCompleter()
	doc = Document("enc")
	event = CompleteEvent()
	completions = list(completer.get_completions(doc, event))
	assert any(c.text == "encode" for c in completions)


def test_completer_settings() -> None:
	completer = MorseCompleter()
	doc = Document("set sco")
	event = CompleteEvent()
	completions = list(completer.get_completions(doc, event))
	assert any(c.text == "scorer" for c in completions)
