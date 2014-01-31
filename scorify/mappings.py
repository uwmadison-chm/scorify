# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

from __future__ import division

"""
A set (right now, just two) of functions that can transform cells in input
files.

The two functions are:

Identity: (doesn't change anything)
LinearMapping: Change a variable from one domain to another (eg, from 1:5 to 5:1)
"""


class Mapping(object):

    def __init__(self):
        super(Mapping, self).__init__()

    def transform(self, value):
        return None


class Identity(Mapping):

    def __init__(self):
        super(Identity, self).__init__()

    def transform(self, value):
        return value


class LinearMapping(Mapping):

    def __init__(self, input_domain, output_domain):
        super(LinearMapping, self).__init__()
        self.input_domain = input_domain
        self.output_domain = output_domain
        try:
            irange = input_domain[1] - input_domain[0]
        except TypeError:
            raise MappingError("{0} and {1} must both be numbers".format(
                input_domain[1], input_domain[0]))
        if irange == 0:
            raise MappingError("Input domain numbers can't be the same")
        try:
            orange = output_domain[1] - output_domain[0]
        except TypeError:
            raise MappingError("{0} and {1} must both be numbers".format(
                input_domain[1], input_domain[0]))

    def transform(self, value):
        in_range = self.input_domain[1] - self.input_domain[0]
        out_range = self.output_domain[1] - self.output_domain[0]
        in_first = self.input_domain[0]
        out_first = self.output_domain[0]
        return (value - in_first) * (out_range/in_range) + out_first

    def __repr__(self):
        return "Map({0}, {1})".format(self.input_domain, self.output_domain)


class MappingError(ValueError):
    pass