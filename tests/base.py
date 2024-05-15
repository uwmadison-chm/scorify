from pathlib import Path
from pytest import fixture


def from_this_dir(filename):
    return str(Path(__file__).parent / filename)


def from_subdir(subdir, filename):
    return str(Path(__file__).parent / subdir / filename)


@fixture
def test_path():
    return Path(__file__).parent
