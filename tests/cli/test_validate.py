from typer.testing import CliRunner

from morse.cli.app import app


def test_validate_spaced_morse(runner: CliRunner) -> None:
	"""Accepts valid boundary-delimited Morse."""
	result = runner.invoke(
		app,
		["validate", ".... . .-.. .-.. ---"],
	)

	assert result.exit_code == 0
	assert "Valid Morse." in result.stdout


def test_validate_unspaced_morse(runner: CliRunner) -> None:
	"""Accepts valid continuous Morse."""
	result = runner.invoke(
		app,
		["validate", "......-...-..---", "--unspaced"],
	)

	assert result.exit_code == 0
	assert "Valid Morse." in result.stdout


def test_validate_from_stdin(runner: CliRunner) -> None:
	"""Reads Morse from stdin."""
	result = runner.invoke(
		app,
		["validate"],
		input=".... . .-.. .-.. ---\n",
	)

	assert result.exit_code == 0
	assert "Valid Morse." in result.stdout


def test_validate_invalid_spaced_morse(runner: CliRunner) -> None:
	"""Rejects invalid boundary-delimited Morse."""
	result = runner.invoke(
		app,
		["validate", ".... ^ .-.."],
	)

	assert result.exit_code == 1
	assert "Invalid Morse:" in result.stdout


def test_validate_invalid_unspaced_morse(runner: CliRunner) -> None:
	"""Rejects invalid continuous Morse."""
	result = runner.invoke(
		app,
		["validate", "^", "--unspaced"],
	)

	assert result.exit_code == 1
	assert "Invalid Morse:" in result.stdout


def test_validate_without_input(runner: CliRunner, monkeypatch) -> None:
	"""Rejects missing input when stdin is not available."""
	monkeypatch.setattr("sys.stdin.isatty", lambda: True)

	result = runner.invoke(app, ["validate"])

	assert result.exit_code == 1
	assert "No input supplied" in result.stdout
