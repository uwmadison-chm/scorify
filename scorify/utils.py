# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System
from __future__ import absolute_import

import re
import math

float_stripper = re.compile(r"\.0*$")


def pp(val, float_places=2, none_val='NaN'):
    mapping = {
        float: float_pp
    }
    mapper = mapping.get(type(val))
    if mapper:
        return mapper(val, float_places, none_val)
    else:
        if val is None:
            return none_val
    return str(val)


def float_pp(num, float_places=2, none_val='NaN'):
    if math.isnan(num) or math.isinf(num):
        return none_val
    rounded = str(round(num, float_places))
    return float_stripper.sub("", rounded)
