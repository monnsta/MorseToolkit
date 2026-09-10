from typer.testing import CliRunner

from morse.cli.app import app


def test_encode_text(runner: CliRunner) -> None:
	result = runner.invoke(app, ["encode", "hello"])

	assert result.exit_code == 0
	assert result.stdout.strip() == ".... . .-.. .-.. ---"


def test_encode_unspaced(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["encode", "hello", "--unspaced"],
	)

	assert result.exit_code == 0
	assert result.stdout.strip() == "......-...-..---"


def test_encode_from_stdin(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["encode"],
		input="hello\n",
	)

	assert result.exit_code == 0
	assert result.stdout.strip() == ".... . .-.. .-.. ---"


def test_encode_empty_argument(runner: CliRunner) -> None:
	result = runner.invoke(app, ["encode", ""])

	assert result.exit_code != 0


def test_encode_without_input(runner: CliRunner, monkeypatch) -> None:
	monkeypatch.setattr("sys.stdin.isatty", lambda: True)

	result = runner.invoke(app, ["encode"])

	assert result.exit_code != 0
	assert "No input supplied" in result.output
