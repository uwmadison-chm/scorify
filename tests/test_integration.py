from __future__ import absolute_import, division

import pytest
import os
import xlrd
import warnings

from .base import *
from scorify.scripts.score_data import main_test
from scorify.scoresheet import SectionError
from scorify.aggregators import AggregatorError

def run_score_data(scoresheet, data, output):
    main_test([
        "--output=" + from_subdir("output", output),
        from_subdir("input", scoresheet),
        from_subdir("input", data)
        ])

def run_test(scoresheet, data, expected):
    run_score_data(scoresheet, data, expected)

    expected_content = open(from_subdir("input", expected)).read()
    actual_content = open(from_subdir("output", expected)).read()
    assert actual_content == expected_content

def run_excel_test(scoresheet, data, expected):
    with warnings.catch_warnings():
        # Skip some xlrd deprecation warnings
        warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        run_score_data(scoresheet, data, expected)

        # This is erroring out
        e = xlrd.open_workbook(from_subdir("input", expected)).sheet_by_index(0)
        a = xlrd.open_workbook(from_subdir("output", expected)).sheet_by_index(0)

        assert e.nrows == a.nrows
        # TODO


def test_basic_integration():
    run_test("001_scoresheet.csv", "001_data.csv", "001_expected.csv")

def test_scoresheet_error():
    with pytest.raises(SystemExit) as e:
        run_test("002_broken_scoresheet.csv", "001_data.csv", "001_expected.csv")
        assert e.value.code == 1

def test_excel_integration():
    run_excel_test("003_scoresheet.xlsx", "003_data.xlsx", "003_expected.xlsx")

def test_excel_integration_error():
    pytest.skip
    # Need to confirm that input with errors gets correctly handled in excel land
    with pytest.raises(SystemExit) as e:
        run_excel_test("004_broken_scoresheet.xlsx", "003_data.xlsx", "003_expected.xlsx")
        assert e.value.code == 1
