# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright (c) 2024 Board of Regents of the University of Wisconsin System

import pytest

from scorify import datafile, scoresheet


@pytest.fixture
def good_data():
    return [
        ["ppt", "happy1", "happy2", "sad1", "sad2", "extra"],
        ["skip", "skip", "skip", "skip", "skip", "skip"],
        ["a", "5", "2", "1", "4", "3"],
        ["b", "5", "2", "1", "4", "3"],
        ["c", "5", "2", "1", "4", "3"],
    ]


@pytest.fixture
def good_data_keep():
    return [
        ["ppt", "happy1", "happy2", "sad1", "sad2", "extra"],
        [
            "",
            "How happy are you?",
            "How happy were you before you started filling out paperwork?",
            "How sad are you?",
            "How sad is this data?",
            "",
        ],
        ["skip", "skip", "skip", "skip", "skip", "skip"],
        ["a", "5", "2", "1", "4", "3"],
        ["b", "5", "2", "1", "4", "3"],
        ["c", "5", "2", "1", "4", "3"],
    ]


@pytest.fixture
def unicode_data():
    return [
        ["ppt", "happy1", "happy2", "sad1", "sad2", "🐢"],
        ["skip", "skip", "skip", "skip", "skip", "skip"],
        ["🐙", "5", "2", "1", "4", "3"],
        ["🌽", "2", "2", "1", "4", "3"],
        ["🐢", "5", "2", "1", "4", "3"],
    ]


@pytest.fixture
def data_with_funny_lengths():
    return [["a", "b"], [1, 2, 3], [4]]


@pytest.fixture
def data_with_duplicate_header():
    return [["a", "b", "a"], [1, 2, 3], [4, 5, 6]]


@pytest.fixture
def empty_rename_section():
    return scoresheet.RenameSection()


@pytest.fixture
def active_rename_section():
    s = scoresheet.RenameSection()
    s.append_from_strings(["happy1", "happy_1"])
    return s


@pytest.fixture
def layout_section_with_skip():
    ls = scoresheet.LayoutSection()
    ls.append_from_strings(["header"])
    ls.append_from_strings(["skip"])
    ls.append_from_strings(["data"])
    return ls


@pytest.fixture
def layout_section_with_skip_and_keep():
    ls = scoresheet.LayoutSection()
    ls.append_from_strings(["header"])
    ls.append_from_strings(["keep"])
    ls.append_from_strings(["skip"])
    ls.append_from_strings(["data"])
    return ls


@pytest.fixture
def layout_section_no_skip():
    ls = scoresheet.LayoutSection()
    ls.append_from_strings(["header"])
    ls.append_from_strings(["data"])
    return ls


@pytest.fixture
def exclude_section():
    es = scoresheet.ExcludeSection()
    es.append_from_strings(["ppt", "a"])
    return es


def test_read_populates_header_data(
    good_data, layout_section_with_skip, empty_rename_section
):
    df = datafile.Datafile(good_data, layout_section_with_skip, empty_rename_section)
    df.read()
    assert df.header == good_data[0]
    assert df.data[0] == dict(zip(df.header, good_data[2]))


def test_read_populates_kept_data(
    good_data_keep, layout_section_with_skip_and_keep, empty_rename_section
):
    df = datafile.Datafile(
        good_data_keep, layout_section_with_skip_and_keep, empty_rename_section
    )
    df.read()
    assert df.header == good_data_keep[0]
    assert df.keep[0]["ppt"] == ""
    assert df.keep[0]["happy1"] == "How happy are you?"
    assert df.data[0]["ppt"] == "a"
    assert df.data[0]["happy1"] == "5"


def test_read_deals_with_unicode(
    unicode_data, layout_section_with_skip, empty_rename_section
):
    df = datafile.Datafile(unicode_data, layout_section_with_skip, empty_rename_section)
    df.read()
    assert df.header == unicode_data[0]
    assert df.data[0] == dict(zip(df.header, unicode_data[2]))
    assert df.data[2]["ppt"] == "🐢"


def test_read_handles_odd_lengths(
    data_with_funny_lengths, layout_section_no_skip, empty_rename_section
):
    df = datafile.Datafile(
        data_with_funny_lengths, layout_section_no_skip, empty_rename_section
    )
    df.read()
    assert len(df.data[0].values()) == len(df.header)
    assert len(df.data[1].values()) == len(df.header)


def test_read_warns_on_ambiguous_columns_and_picks_last(
    data_with_duplicate_header, layout_section_no_skip, empty_rename_section
):
    with pytest.warns(UserWarning):
        df = datafile.Datafile(
            data_with_duplicate_header, layout_section_no_skip, empty_rename_section
        )
        df.read()
        assert len(df.data[0].values()) == len(df.header) - 1
        assert df.data[0]["a"] == 3


def test_rename_changes_headers(
    good_data, layout_section_with_skip, active_rename_section
):
    df = datafile.Datafile(good_data, layout_section_with_skip, active_rename_section)
    df.read()
    assert "happy_1" in df.header
    assert "happy1" not in df.header


def test_apply_exclusions(
    good_data, layout_section_with_skip, exclude_section, empty_rename_section
):
    df = datafile.Datafile(good_data, layout_section_with_skip, empty_rename_section)
    df.read()
    assert len(df) == 3
    df.apply_exclusions(exclude_section)
    assert len(df) == 2
    assert df[0]["ppt"] == "b"
