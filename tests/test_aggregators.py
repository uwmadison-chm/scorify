# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

import pytest

from scorify import aggregators


def test_good_parsing():
    n, fx, measures = aggregators.parse_expr("sum(foo)")
    assert n == 'sum'
    assert fx == aggregators.ag_sum
    assert measures == ['foo']
    n, fx, measures = aggregators.parse_expr("MEAN(foo, bar)")
    assert n == 'mean'
    assert fx == aggregators.ag_mean
    assert measures == ['foo', 'bar']
    n, fx, measures = aggregators.parse_expr('join(foo, bar)')
    assert n == 'join'
    assert fx == aggregators.ag_join
    assert measures == ['foo', 'bar']


def test_bad_parses():
    with pytest.raises(aggregators.AggregatorError):
        aggregators.parse_expr("dkjaskdj")
    with pytest.raises(aggregators.AggregatorError):
        aggregators.parse_expr("bogus(foo)")


def test_sum_with_nums():
    ar = [1, 2, 3]
    assert aggregators.ag_sum(ar) == 6


def test_sum_with_strings():
    ar = ['1', '2', '3']
    assert aggregators.ag_sum(ar) == 6


def test_mean():
    ar = [1, 2, 3]
    assert aggregators.ag_mean(ar) == 2


def test_join():
    ar = ['foo', 'bar', 'baz']
    assert aggregators.ag_join(ar) == 'foo|bar|baz'
    ar = [1, 2, 3]
    assert aggregators.ag_join(ar) == '1|2|3'
    ar = ['foo', '', ' ', 'bar']
    assert aggregators.ag_join(ar) == 'foo|bar'
