# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright (c) 2024 Board of Regents of the University of Wisconsin System

from scorify import utils


def test_float_pp():
    assert utils.float_pp(1.0) == "1"
    assert utils.float_pp(float("nan"), none_val="NaN") == "NaN"
    assert utils.float_pp(1.2345, float_places=2) == "1.23"


def test_pp():
    assert utils.pp(1.0) == "1"
    assert utils.pp(None, none_val="NaN") == "NaN"
    assert utils.pp(True) == "True"
