# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

import pytest

from scorify import scoresheet
from scorify import directives


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
