# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright (c) 2024 Board of Regents of the University of Wisconsin System

import pytest

from scorify import scoresheet, directives


@pytest.fixture
def good_sample_csv():
    import io
    import csv

    return csv.reader(
        io.StringIO(
            """
layout,header
layout,skip
 layout,data

rename,happy_1,happy

# This is a comment
exclude,ppt,0000
exclude,ppt,9999

transform,normal,"map(1:5,1:5)"
transform,reverse,"map(1:5,5:1)"
transform,gender,discrete_map("1": "f", "2": "m")

score,happy1, happy,normal
score,sad1,sad,reverse
score,happy2,happy,reverse
score,sad2,sad,normal
score,gender,gender,gender

measure,mean_happy,mean(happy)
measure,mean_sad,mean(sad)
measure,emo_vals,"join(happy, sad)"
measure,happy_ratio,"ratio(mean_happy,mean_sad)"
measure,min_emo,"min(happy, sad)"
measure,max_happy,max(happy)
"""
        )
    )


def test_successful_read(good_sample_csv):
    reader = scoresheet.Reader(good_sample_csv)
    ss = reader.read_into_scoresheet()
    assert type(ss) == scoresheet.Scoresheet
    assert ss.errors == []
    assert len(ss.layout_section) == 3
    assert len(ss.rename_section) == 1
    assert len(ss.transform_section) == 3
    assert len(ss.score_section) == 5
    assert len(ss.aggregator_section) == 6


def test_section_iterates():
    skip = directives.Layout("skip")
    header = directives.Layout("header")
    data = directives.Layout("data")

    ls = scoresheet.LayoutSection([header, skip, data])
    for directive in ls:
        assert directive


def test_layout_section():
    skip = directives.Layout("skip")
    header = directives.Layout("header")
    data = directives.Layout("data")

    ls = scoresheet.LayoutSection([header, data])
    assert ls.is_valid()

    ls = scoresheet.LayoutSection([header, skip, data])
    assert ls.is_valid()

    ls = scoresheet.LayoutSection([header, header, data])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([header])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([data])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([header, data, data])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([header, data, skip])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([data, header])
    assert not ls.is_valid()


def test_layout_section_with_string_ary():
    ls = scoresheet.LayoutSection()
    ls.append_from_strings(["header"])
    assert len(ls) == 1
    with pytest.raises(directives.DirectiveError):
        ls.append_from_strings([])
    with pytest.raises(directives.DirectiveError):
        ls.append_from_strings(["foo"])


def test_rename_section_with_string_list():
    s = scoresheet.RenameSection()
    s.append_from_strings(["foo", "bar"])
    assert len(s) == 1
    assert s.map_name("foo") == "bar"
    assert s.map_name("baz") == "baz"


def test_rename_section_dupes():
    s = scoresheet.RenameSection()
    s.append_from_strings(["foo", "bar"])
    # "foo" and "bar" are off-limits for any other renames
    with pytest.raises(scoresheet.SectionError):
        s.append_from_strings(["foo", "x"])
    with pytest.raises(scoresheet.SectionError):
        s.append_from_strings(["x", "foo"])
    with pytest.raises(scoresheet.SectionError):
        s.append_from_strings(["bar", "x"])
    with pytest.raises(scoresheet.SectionError):
        s.append_from_strings(["x", "bar"])


def test_transform_section_dupes():
    s = scoresheet.TransformSection()
    d = directives.Transform("foo", "map(1:5, 1:5)")
    s.append_directive(d)
    with pytest.raises(scoresheet.SectionError):
        s.append_directive(d)
    assert len(s.directives) == 1


def test_transform_section_getitem():
    s = scoresheet.TransformSection()
    d = directives.Transform("foo", "map(1:5, 1:5)")
    s.append_directive(d)
    assert s["foo"] == d


def test_transform_section_getitem_with_blank():
    s = scoresheet.TransformSection()
    assert type(s[""]) == directives.Transform


def test_score_section_dupes():
    s = scoresheet.ScoreSection()
    d = directives.Score("col", "measure")
    s.append_directive(d)
    with pytest.raises(scoresheet.SectionError):
        s.append_directive(d)
    s.append_directive(directives.Score("col", "measure2"))
    s.append_directive(directives.Score("col2", "measure"))
    assert len(s.directives) == 3


def test_aggregator_section_dupes():
    s = scoresheet.AggregatorSection()
    d = directives.Aggregator("foo", "mean(bar)")
    s.append_directive(d)
    with pytest.raises(scoresheet.SectionError):
        s.append_directive(d)
    assert len(s.directives) == 1
