# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

from __future__ import with_statement

import pytest

from scorify import directives


def test_layout_accepts_header_skip_data():
    with pytest.raises(directives.DirectiveError):
        l = directives.Layout('foo')
    assert directives.Layout('header')
    assert directives.Layout('data')
    assert directives.Layout('skip')
    assert directives.Layout('SKIP')