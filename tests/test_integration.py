from __future__ import absolute_import, division

import pytest
import csv

from .base import from_subdir
from scorify.scripts import score_data


def run_score_data(scoresheet, data, output, sheet=None):
    args = [
        "--output=" + from_subdir("output", output),
        from_subdir("input", scoresheet),
        from_subdir("input", data),
    ]
    if sheet:
        args.append("--sheet={0}".format(sheet))
    score_data.main(args)


def run_test(scoresheet, data, expected):
    run_score_data(scoresheet, data, expected)

    expected_content = open(from_subdir("input", expected)).read()
    actual_content = open(from_subdir("output", expected)).read()
    assert actual_content == expected_content


def run_excel_test(scoresheet, data, expected, sheet=None):
    run_score_data(scoresheet, data, expected, sheet=sheet)

    with open(from_subdir("input", expected)) as ecsv:
        e = csv.reader(ecsv)
        elist = list(e)

    with open(from_subdir("output", expected)) as acsv:
        a = csv.reader(acsv)
        alist = list(a)

    # Compare length
    assert len(elist) == len(alist)
    # Compare content
    assert elist == alist


def test_basic_integration():
    run_test("001_scoresheet.csv", "001_data.csv", "001_expected.csv")


def test_scoresheet_error():
    with pytest.raises(SystemExit) as e:
        run_test("002_broken_scoresheet.csv", "001_data.csv", "001_expected.csv")
        assert e.value.code == 1


def test_excel_integration():
    run_excel_test("003_scoresheet.xlsx", "003_data.xlsx", "003_expected.csv")


def test_excel_specific_sheet():
    run_excel_test("003_scoresheet.xlsx", "003_data.xlsx", "004_expected.csv", 1)


def test_excel_integration_error():
    pytest.skip
    # Need to confirm that input with errors gets correctly handled in excel
    # land
    with pytest.raises(SystemExit) as e:
        run_excel_test(
            "004_broken_scoresheet.xlsx", "003_data.xlsx", "003_expected.csv"
        )
        assert e.value.code == 1


def test_score_column_names():
    run_test("005_scoresheet.csv", "005_data.csv", "005_expected.csv")
