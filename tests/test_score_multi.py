import pytest
import csv

from .base import from_subdir
from scorify.scripts import score_multi


def test_help(capsys):
    with pytest.raises(SystemExit):
        score_multi.main(["--help"])
    out, _err = capsys.readouterr()
    assert "Usage:" in out


def test_version(capsys):
    with pytest.raises(SystemExit):
        score_multi.main(["--version"])
    out, _err = capsys.readouterr()
    assert "Scorify" in out


def test_missing_multifile(capsys):
    with pytest.raises(SystemExit):
        score_multi.main(["missing.csv", "missing.csv", "missing.csv", "missing.csv"])
        out, err = capsys.readouterr()
        assert "multi_csv" in err


def test_success(pytestconfig, tmp_path):
    data_dir = pytestconfig.rootpath / "tests" / "multi"
    multi_arg = data_dir / "success.csv"
    scoresheet_arg = data_dir / "score_{instrument}.csv"
    data_arg = data_dir / "data_{event}.csv"
    out_arg = tmp_path / "scored_{instrument}_{event}.csv"
    score_multi.main([f"{multi_arg}", f"{scoresheet_arg}", f"{data_arg}", f"{out_arg}"])
    multi_lines = multi_arg.read_text().splitlines()
    # Account for the header row
    score_commands_count = len(multi_lines) - 1
    assert score_commands_count == len(list(tmp_path.glob("*.csv")))


# More tests??
