# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright (c) 2024 Board of Regents of the University of Wisconsin System

from __future__ import with_statement

import pytest

from scorify import directives


def test_layout_accepts_header_skip_data():
    with pytest.raises(directives.DirectiveError):
        directives.Layout("foo")
    assert directives.Layout("header")
    assert directives.Layout("data")
    assert directives.Layout("skip")
    assert directives.Layout(" skip ")
    assert directives.Layout("SKIP")


def test_layout_accepts_header_keep():
    assert directives.Layout("keep")


def test_transforming_works():
    tx = directives.Transform("", "")
    assert tx.transform(1) == 1
    tx = directives.Transform("", "map(1:5,2:6)")
    assert tx.transform(1) == 2


def test_creating_rename():
    # Just verify it exists; this directive doesn't do anything.
    directives.Rename("foo", "bar")
    # You need a new name
    with pytest.raises(directives.DirectiveError):
        directives.Rename("", "foo")
    with pytest.raises(directives.DirectiveError):
        directives.Rename("foo", "")
    # And you can't rename something to itself
    with pytest.raises(directives.DirectiveError):
        directives.Rename("foo", "foo")


def test_conflicts_with():
    d = directives.Rename("foo", "bar")
    assert d.conflicts_with(directives.Rename("foo", "baz"))
    assert d.conflicts_with(directives.Rename("bar", "baz"))
    assert d.conflicts_with(directives.Rename("baz", "foo"))
    assert d.conflicts_with(directives.Rename("baz", "bar"))
    assert not d.conflicts_with(directives.Rename("baz", "corge"))


def test_measure():
    m = directives.Aggregator("foo", "mean(c_foo)")
    assert m.agg_fx
    assert m.to_use == ["c_foo"]
    with pytest.raises(directives.DirectiveError):
        directives.Aggregator("foo", "bar")
