# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

"""
Aggregators are functions that consense sets of numbers into single ones.
They're used by measure directives.
"""
from __future__ import absolute_import, division

import math
import re
import logging

NaN = float('nan')

expr_re = re.compile(r"""
    (\w+)  # Function name
    \(
    ([^)]+) # Yup, you can put anything in the parens
    \)
""", re.VERBOSE | re.IGNORECASE)


def parse_expr(expr):
    fx_map = {
        'sum': ag_sum,
        'sum_imputed': ag_sum_imputed,
        'mean': ag_mean,
        'mean_imputed': ag_mean_imputed,
        'imputed_fraction': ag_imputed_fraction,
        'join': ag_join,
        'ratio': ag_ratio,
        'max': ag_max,
        'min': ag_min,
    }
    try:
        fx_name, measure_names = expr_re.match(expr).groups()
        fx_name = fx_name.lower()
        measure_names = [m.strip() for m in measure_names.split(",")]
    except AttributeError as err:
        raise AggregatorError(
            "I don't understand {0!r}: {1}".format(expr, err))
    try:
        fx = fx_map[fx_name]
    except KeyError:
        raise AggregatorError("I don't know {0}".format(fx_name))
    return (fx_name, fx, measure_names)


def isfinite(val):
    try:
        f_val = float(val)
    except (TypeError, ValueError):
        return False
    return not (math.isnan(f_val) or math.isinf(f_val))


def to_f(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def float_or_imputed(value, imputed_value):
    if isfinite(value):
        return to_f(value)
    return imputed_value


def numeric_only(values):
    floated_vals = [to_f(val) for val in values]
    return [val for val in floated_vals if isfinite(val)]


def impute_mean(values):
    numeric_values = numeric_only(values)
    mean_val = ag_mean(numeric_values)
    return [float_or_imputed(val, mean_val) for val in values]


# sum is a reserved word in python because goddammt
def ag_sum(values):
    return math.fsum([float(v) for v in values])


def ag_mean(values):
    return ag_sum(values)/(len(values))


def ag_mean_imputed(values):
    try:
        with_imputed = impute_mean(values)
        mean_val = ag_mean(with_imputed)
        logging.debug("mean({}): {}".format(with_imputed, mean_val))
        return mean_val
    except ZeroDivisionError:
        return NaN


def ag_sum_imputed(values):
    try:
        with_imputed = impute_mean(values)
        sum_val = ag_sum(with_imputed)
        logging.debug("sum({}): {}".format(with_imputed, sum_val))
        return sum_val
    except ZeroDivisionError:
        return NaN


def ag_imputed_fraction(values):
    """ The fraction of non-float-able items in values """
    imputed_count = len(values) - len(numeric_only(values))
    return imputed_count / len(values)


def ag_join(values):
    # Filters out empty values.
    values = [str(v) for v in values if len(str(v).strip()) > 0]
    return '|'.join([str(v) for v in values])


def ag_ratio(values):
    if len(values) != 2:
        raise AggregatorError("ratio() needs two values")
    try:
        return float(values[0] / float(values[1]))
    except ZeroDivisionError:
        return NaN


def ag_max(values):
    return max([float(v) for v in values])


def ag_min(values):
    return min([float(v) for v in values])


class AggregatorError(ValueError):
    pass
