# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright (c) 2024 Board of Regents of the University of Wisconsin System

from __future__ import with_statement

import pytest

from scorify.mappings import (
    Mapping,
    Identity,
    LinearMapping,
    DiscreteMapping,
    MappingError,
    PassthroughMapping,
)


def test_identity():
    i = Identity()
    test_vals = (0, "foo")
    for v in test_vals:
        assert v == i.transform(v)


def test_good_mappings():
    sets = [((1, 5), (1, 5)), ((1, 5), (5, 1)), ((1, 5), (2, 6)), ((1, 5), (0, 10))]
    for inrange, outrange in sets:
        m = LinearMapping(inrange, outrange)
        assert m.transform(inrange[0]) == outrange[0]
        assert m.transform(inrange[1]) == outrange[1]


def test_linear_mapping_strings():
    m = LinearMapping((1, 5), (2, 6))
    assert m.transform("1") == 2


def test_mapping_fails_with_small_inrange():
    with pytest.raises(MappingError):
        LinearMapping((1, 1), (2, 3))


def test_mapping_fails_with_letter_ranges():
    with pytest.raises(MappingError):
        LinearMapping(("a", 1), (1, 5))

    with pytest.raises(MappingError):
        LinearMapping((1, 5), ("a", 1))


def test_linear_mapping_from_string():
    m = LinearMapping.from_string("map( -1:3,2.5: 4)")
    assert m.input_domain == (-1.0, 3.0)
    assert m.output_domain == (2.5, 4.0)
    with pytest.raises(MappingError):
        LinearMapping.from_string("braboz")
    with pytest.raises(MappingError):
        LinearMapping.from_string("map(a:b,3:4)")


def test_discrete_mapping_from_string():
    m = DiscreteMapping.from_string('discrete_map("1":"f","2":"m")')
    assert m.map_dict == {"1": "f", "2": "m"}
    # And let's get trickier
    m = DiscreteMapping.from_string(r'discrete_map("1\"": "f" , "2" :"m")')
    assert m.map_dict == {r'1"': "f", "2": "m"}


def test_discrete_mapping_transform():
    m = DiscreteMapping({"1": "f", "2": "m"})
    assert m.transform("1") == "f"
    assert m.transform("2") == "m"
    assert m.transform("3") == ""


def test_passthrough_mapping_from_string():
    m = PassthroughMapping.from_string('passthrough_map("1":"f","2":"m")')
    assert m.map_dict == {"1": "f", "2": "m"}


def test_passthrough_mapping_transform():
    m = PassthroughMapping({"1": "f", "2": "m"})
    assert m.transform("1") == "f"
    assert m.transform("3") == "3"


def test_mapping_types():
    assert type(Mapping.from_string("")) == Identity
    assert type(Mapping.from_string("i")) == Identity
    assert type(Mapping.from_string("map(1:3,2:4)")) == LinearMapping
    assert type(Mapping.from_string('discrete_map("a":"b")')) == DiscreteMapping

    assert type(Mapping.from_string('passthrough_map("a":"b")')) == PassthroughMapping
