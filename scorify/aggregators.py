# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

"""
Aggregators are functions that consense sets of numbers into single ones.
They're used by measure directives.
"""

import math

# sum is a reserved word in python because goddammt
def ag_sum(values):
    return math.fsum([float(v) for v in values])


def ag_mean(values):
    return ag_sum(values)/float(len(values))