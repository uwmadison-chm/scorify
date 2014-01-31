# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

from __future__ import with_statement

import pytest

from scorify import mappings

def test_identity():
    i = mappings.Identity()
    test_vals = (0, 'foo')
    for v in test_vals:
        assert v == i.transform(v)


def test_good_mappings():
    sets = [
        ((1,5), (1,5)),
        ((1,5), (5,1)),
        ((1,5), (2,6)),
        ((1,5), (0, 10))
    ]
    for inrange, outrange in sets:
        m = mappings.LinearMapping(inrange, outrange)
        assert m.transform(inrange[0]) == outrange[0]
        assert m.transform(inrange[1]) == outrange[1]

def test_mapping_fails_with_small_inrange():
    with pytest.raises(mappings.MappingError):
        m = mappings.LinearMapping((1,1), (2,3))

def test_mapping_fails_with_letter_ranges():
    with pytest.raises(mappings.MappingError):
        m = mappings.LinearMapping(('a', 1), (1,5))

    with pytest.raises(mappings.MappingError):
        m = mappings.LinearMapping((1,5), ('a', 1))