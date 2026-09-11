from pathlib import Path

from typer.testing import CliRunner

from morse.cli.app import app


def test_solve_unspaced_morse(runner: CliRunner, dictionary_file: Path) -> None:
	result = runner.invoke(
		app,
		["solve", "......-...-..---", "-d", str(dictionary_file)],
	)

	assert result.exit_code == 0
	assert "1. hello" in result.stdout


def test_solve_from_stdin(runner: CliRunner, dictionary_file: Path) -> None:
	result = runner.invoke(
		app,
		["solve", "-d", str(dictionary_file)],
		input="......-...-..---\n",
	)

	assert result.exit_code == 0
	assert "1. hello" in result.stdout


def test_solve_limit(runner: CliRunner, dictionary_file: Path) -> None:
	result = runner.invoke(
		app,
		["solve", "......-...-..---", "-d", str(dictionary_file), "-n", "1"],
	)

	assert result.exit_code == 0
	lines = [line for line in result.stdout.splitlines() if line.strip()]
	assert len(lines) == 1


def test_solve_no_solution(runner: CliRunner, dictionary_file: Path) -> None:
	result = runner.invoke(
		app,
		["solve", "--------------------", "-d", str(dictionary_file)],
	)

	assert result.exit_code == 1
	assert "No solution found." in result.output


def test_solve_missing_dictionary(runner: CliRunner) -> None:
	result = runner.invoke(
		app,
		["solve", "......-...-..---", "-d", "nonexistent.txt"],
	)

	assert result.exit_code != 0


def test_solve_without_input(
	runner: CliRunner, dictionary_file: Path, monkeypatch
) -> None:
	monkeypatch.setattr("sys.stdin.isatty", lambda: True)

	result = runner.invoke(
		app,
		["solve", "-d", str(dictionary_file)],
	)

	assert result.exit_code != 0
	assert "No input supplied" in result.output
