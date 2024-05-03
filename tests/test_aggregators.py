# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright (c) 2024 Board of Regents of the University of Wisconsin System

from __future__ import absolute_import, division

import pytest

import math

from scorify import aggregators


def test_good_parsing():
    n, fx, measures = aggregators.parse_expr("sum(foo)")
    assert n == "sum"
    assert fx == aggregators.ag_sum
    assert measures == ["foo"]
    n, fx, measures = aggregators.parse_expr("MEAN(foo, bar)")
    assert n == "mean"
    assert fx == aggregators.ag_mean
    assert measures == ["foo", "bar"]
    n, fx, measures = aggregators.parse_expr("join(foo, bar)")
    assert n == "join"
    assert fx == aggregators.ag_join
    assert measures == ["foo", "bar"]
    n, fx, measures = aggregators.parse_expr("ratio(foo, bar)")
    assert n == "ratio"
    assert fx == aggregators.ag_ratio
    assert measures == ["foo", "bar"]
    n, fx, measures = aggregators.parse_expr("max(foo, bar)")
    assert fx == aggregators.ag_max
    assert measures == ["foo", "bar"]
    n, fx, measures = aggregators.parse_expr("min(foo, bar)")
    assert fx == aggregators.ag_min
    assert measures == ["foo", "bar"]
    n, fx, measures = aggregators.parse_expr("sum_imputed(foo)")
    assert n == "sum_imputed"
    assert fx == aggregators.ag_sum_imputed
    assert measures == ["foo"]
    n, fx, measures = aggregators.parse_expr("mean_imputed(foo)")
    assert n == "mean_imputed"
    assert fx == aggregators.ag_mean_imputed
    assert measures == ["foo"]
    n, fx, measures = aggregators.parse_expr("imputed_fraction(foo)")
    assert n == "imputed_fraction"
    assert fx == aggregators.ag_imputed_fraction
    assert measures == ["foo"]


def test_bad_parses():
    with pytest.raises(aggregators.AggregatorError):
        aggregators.parse_expr("dkjaskdj")
    with pytest.raises(aggregators.AggregatorError):
        aggregators.parse_expr("bogus(foo)")


def test_sum_with_nums():
    ar = [1, 2, 3]
    assert aggregators.ag_sum(ar) == 6


def test_sum_with_strings():
    ar = ["1", "2", "3"]
    assert aggregators.ag_sum(ar) == 6


def test_mean():
    ar = [1, 2, 3]
    assert aggregators.ag_mean(ar) == 2


def test_join():
    ar = ["foo", "bar", "baz"]
    assert aggregators.ag_join(ar) == "foo|bar|baz"
    ar = [1, 2, 3]
    assert aggregators.ag_join(ar) == "1|2|3"
    ar = ["foo", "", " ", "bar"]
    assert aggregators.ag_join(ar) == "foo|bar"


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


def test_mean_imputed():
    ar = [1, None, 3, 5]
    imputed_mean = aggregators.ag_mean([1, 3, 3, 5])
    assert aggregators.ag_mean_imputed(ar) == imputed_mean
    ar_nan = [1, float("nan"), 3, 5]
    assert aggregators.ag_mean_imputed(ar_nan) == imputed_mean
    assert math.isnan(aggregators.ag_mean_imputed([None, None]))


def test_sum_imputed():
    ar = [1, None, 3, 5]
    assert aggregators.ag_sum_imputed(ar) == (1 + 3 + 3 + 5)
    assert math.isnan(aggregators.ag_sum_imputed([None, None]))


def test_imputed_fraction():
    ar = [1, None, 3, 5]
    assert aggregators.ag_imputed_fraction(ar) == (1 / 4)
