from pathlib import Path

from morse.cli.interactive.paths import (
	expand_path,
	path_completions,
)


def test_expand_path() -> None:
	path = expand_path("~/test_dir")
	assert isinstance(path, Path)
	assert not str(path).startswith("~")


def test_path_completions(tmp_path: Path) -> None:
	(tmp_path / "file1.txt").write_text("a")
	(tmp_path / "file2.txt").write_text("b")
	(tmp_path / "sub_dir").mkdir()

	prefix = str(tmp_path / "file")
	completions = path_completions(prefix)

	assert len(completions) == 2
	assert any("file1.txt" in c for c in completions)
	assert any("file2.txt" in c for c in completions)
