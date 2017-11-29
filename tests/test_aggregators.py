# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

import pytest

import math

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
    n, fx, measures = aggregators.parse_expr('ratio(foo, bar)')
    assert n == 'ratio'
    assert fx == aggregators.ag_ratio
    assert measures == ['foo', 'bar']
    n, fx, measures = aggregators.parse_expr('max(foo, bar)')
    assert fx == aggregators.ag_max
    assert measures == ['foo', 'bar']
    n, fx, measures = aggregators.parse_expr('min(foo, bar)')
    assert fx == aggregators.ag_min
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


def test_ratio():
    ar = [1, 2]
    assert aggregators.ag_ratio(ar) == 0.5


def test_ratio_with_zero():
    ar = [1, 0]
    assert math.isnan(aggregators.ag_ratio(ar))


def test_max():
    ar = [1, 5, 2]
    assert aggregators.ag_max(ar) == 5


def test_min():
    ar = [1, 5, 2]
    assert aggregators.ag_min(ar) == 1
