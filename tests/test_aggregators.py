# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

import pytest

from scorify import aggregators


def test_good_parsing():
    n, fx, cols = aggregators.parse_expr("sum(foo)")
    assert n == 'sum'
    assert fx == aggregators.ag_sum
    assert cols == ['foo']
    n, fx, cols = aggregators.parse_expr("MEAN(foo, bar)")
    assert n == 'mean'
    assert fx == aggregators.ag_mean
    assert cols == ['foo', 'bar']


def test_bad_parses():
    with pytest.raises(aggregators.AggregatorError):
        aggregators.parse_expr("dkjaskdj")
    with pytest.raises(aggregators.AggregatorError):
        aggregators.parse_expr("bogus(foo)")


def test_sum_with_nums():
    ar = [1,2,3]
    assert aggregators.ag_sum(ar) == 6


def test_sum_with_strings():
    ar = ['1','2','3']
    assert aggregators.ag_sum(ar) == 6


def test_mean():
    ar = [1,2,3]
    assert aggregators.ag_mean(ar) == 2