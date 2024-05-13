import pytest
import csv

from .base import from_subdir
from scorify.scripts import score_data


def test_help(capsys):
    with pytest.raises(SystemExit):
        score_data.main(["--help"])
    out, err = capsys.readouterr()
    assert "Usage:" in out


def test_version(capsys):
    with pytest.raises(SystemExit):
        score_data.main(["--version"])
    out, err = capsys.readouterr()
    assert "Scorify" in out


# Cases we want to test:
# 1. Everything works, we get as many files as there are lines in the input
# 2. We get an error in the scoring for a line, and get one less line than requested
# 3. We have an
