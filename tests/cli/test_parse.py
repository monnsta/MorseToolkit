from typer.testing import CliRunner

from morse.cli.app import app


def test_parse_symbols(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["parse", "... ---"],
	)

	assert result.exit_code == 0
	assert "symbol" in result.stdout
	assert "DOT" in result.stdout
	assert "DASH" in result.stdout


def test_parse_character_boundary(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["parse", "... ---"],
	)

	assert result.exit_code == 0
	assert "character_boundary" in result.stdout


def test_parse_word_boundary(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["parse", "...   ---"],
	)

	assert result.exit_code == 0
	assert "word_boundary" in result.stdout


def test_parse_from_stdin(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["parse"],
		input=".... . .-.. .-.. ---\n",
	)

	assert result.exit_code == 0
	assert "symbol" in result.stdout


def test_parse_invalid_morse(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["parse", ".... ^ .-.."],
	)

	assert result.exit_code != 0
