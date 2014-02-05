# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

import pytest

from scorify import scoresheet
from scorify import directives


@pytest.fixture
def good_sample_csv():
    import StringIO
    import csv
    return csv.reader(StringIO.StringIO("""
layout,header
layout,skip
 layout,data

# This is a comment
exclude,ppt,0000
exclude,ppt,9999

transform,normal,"map(1:5,1:5)"
transform,reverse,"map(1:5,5:1)"

score,happy1, happy,normal
score,sad1,sad,reverse
score,happy2,happy,reverse
score,sad2,sad,normal

measure,mean_happy,mean(happy)
measure,mean_sad,mean(sad)
"""))


def test_successful_read(good_sample_csv):
    reader = scoresheet.Reader(good_sample_csv)
    ss = reader.read_into_scoresheet()
    assert type(ss) == scoresheet.Scoresheet
    assert ss.errors == []
    assert len(ss.layout_section) == 3
    assert len(ss.transform_section) == 2
    assert len(ss.score_section) == 4
    assert len(ss.measure_section) == 2


def test_layout_section():
    skip = directives.Layout('skip')
    header = directives.Layout('header')
    data = directives.Layout('data')

    ls = scoresheet.LayoutSection([header,data])
    assert ls.is_valid()

    ls = scoresheet.LayoutSection([header,skip,data])
    assert ls.is_valid()

    ls = scoresheet.LayoutSection([header,header,data])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([header])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([data])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([header,data,data])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([header,data,skip])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([data,header])
    assert not ls.is_valid()


def test_layout_section_with_string_ary():
    ls = scoresheet.LayoutSection()
    ls.append_from_strings(['header'])
    assert len(ls) == 1
    with pytest.raises(directives.DirectiveError):
        ls.append_from_strings([])
    with pytest.raises(directives.DirectiveError):
        ls.append_from_strings(['foo'])

def test_transform_section_dupes():
    s = scoresheet.TransformSection()
    d = directives.Transform("foo", "map(1:5, 1:5)")
    s.append_directive(d)
    with pytest.raises(scoresheet.SectionError):
        s.append_directive(d)
    assert len(s.directives) == 1


def test_score_section_dupes():
    s = scoresheet.ScoreSection()
    d = directives.Score("col", "measure")
    s.append_directive(d)
    with pytest.raises(scoresheet.SectionError):
        s.append_directive(d)
    s.append_directive(directives.Score("col", "measure2"))
    s.append_directive(directives.Score("col2", "measure"))
    assert len(s.directives) == 3


def test_measure_section_dupes():
    s = scoresheet.MeasureSection()
    d = directives.Measure('foo', 'mean(bar)')
    s.append_directive(d)
    with pytest.raises(scoresheet.SectionError):
        s.append_directive(d)
    assert len(s.directives) == 1