# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

import pytest

from scorify import aggregators


def test_sum_with_nums():
    ar = [1,2,3]
    assert aggregators.ag_sum(ar) == 6


def test_sum_with_strings():
    ar = ['1','2','3']
    assert aggregators.ag_sum(ar) == 6


def test_mean():
    ar = [1,2,3]
    assert aggregators.ag_mean(ar) == 2