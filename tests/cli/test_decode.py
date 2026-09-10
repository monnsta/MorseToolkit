from typer.testing import CliRunner

from morse.cli.app import app


def test_decode_morse(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["decode", ".... . .-.. .-.. ---"],
	)

	assert result.exit_code == 0
	assert result.stdout.strip() == "HELLO"


def test_decode_words(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["decode", ".... . .-.. .-.. ---   - .... . .-. ."],
	)

	assert result.exit_code == 0
	assert result.stdout.strip() == "HELLO THERE"


def test_decode_from_stdin(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["decode"],
		input=".... . .-.. .-.. ---\n",
	)

	assert result.exit_code == 0
	assert result.stdout.strip() == "HELLO"


def test_decode_invalid_morse(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["decode", ".... ^ .-.."],
	)

	assert result.exit_code != 0


def test_decode_without_input(runner: CliRunner, monkeypatch) -> None:
	monkeypatch.setattr("sys.stdin.isatty", lambda: True)

	result = runner.invoke(app, ["decode"])

	assert result.exit_code != 0
	assert "No input supplied" in result.output
