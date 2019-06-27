from __future__ import absolute_import, division

import pytest
import os

from .base import *
from scorify.scripts.score_data import main_test

def run_test(scoresheet, data, expected):
    main_test([
        "--output=" + from_subdir("output", expected),
        from_subdir("input", scoresheet),
        from_subdir("input", data)
        ])

    expected_content = open(from_subdir("input", expected)).read()
    actual_content = open(from_subdir("output", expected)).read()
    assert actual_content == expected_content


def test_basic_integration():
    run_test("1_scoresheet.csv", "1_data.csv", "1_expected.csv")

