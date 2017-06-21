# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

from __future__ import division, absolute_import
import re

"""
A set (right now, just two) of functions that can transform cells in input
files.

The two functions are:

Identity: (doesn't change anything)
LinearMapping: Change a variable from one domain to
another (eg, from 1:5 to 5:1)
"""


class Mapping(object):

    def __init__(self):
        super(Mapping, self).__init__()

    def transform(self, value):
        return None

    @classmethod
    def from_string(kls, fx_string=''):
        if fx_string == '' or fx_string.find('i') == 0:
            return Identity()
        if fx_string.find("map(") == 0:
            return LinearMapping.from_string(fx_string)
        if fx_string.find("discrete_map(") == 0:
            return DiscreteMapping.from_string(fx_string)
        if fx_string.find("passthrough_map(") == 0:
            return PassthroughMapping.from_string(fx_string)


class Identity(Mapping):

    def __init__(self):
        super(Identity, self).__init__()

    def transform(self, value):
        return value


linear_mapping_re = re.compile(r""" # example: map(1:3,2:4)
map\(\s*
    (-?\d+\.?\d*)\s*:\s*(-?\d+\.?\d*) # 1:5 or -1:5 or 2.5 : -6.3
    \s*,\s*
    (-?\d+\.?\d*)\s*:\s*(-?\d+\.?\d*)
\s*\)
""", re.VERBOSE | re.IGNORECASE)


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
            output_domain[1] - output_domain[0]
        except TypeError:
            raise MappingError("{0} and {1} must both be numbers".format(
                input_domain[1], input_domain[0]))

    def transform(self, value):
        val_float = float(value)
        in_range = self.input_domain[1] - self.input_domain[0]
        out_range = self.output_domain[1] - self.output_domain[0]
        in_first = self.input_domain[0]
        out_first = self.output_domain[0]
        return (val_float - in_first) * (out_range/in_range) + out_first

    @classmethod
    def from_string(kls, fx_string):
        result = linear_mapping_re.match(fx_string)
        if result is None:
            raise MappingError("I don't understand {0!r}".format(
                fx_string))
        params = result.groups()
        pn = [float(param) for param in params]
        return LinearMapping((pn[0], pn[1]), (pn[2], pn[3]))

    def __repr__(self):
        return "LinearMapping({0}, {1})".format(
            self.input_domain, self.output_domain)

# Example: string_map("1":"f", "2":"m")
# We'll use this as an iterator to get all the "1":"f" maps
discrete_mapping_re = re.compile(r"""
    "((?:[^"\\]|\\.)*)"
    \s*:\s*
    "((?:[^"\\]|\\.)*)"
""", re.VERBOSE)


class DiscreteMapping(Mapping):

    def __init__(self, map_dict):
        super(DiscreteMapping, self).__init__()
        self.map_dict = map_dict

    def transform(self, value):
        # In the case where there's no match, it's probably best to return an
        # empty string. They'll always see the original value in the output
        # anyhow.
        return self.map_dict.get(value, '')

    @classmethod
    def from_string(kls, fx_string):
        def ues(s):
            # Unescapes strings -- will turn '\"' into '"'
            return bytes(s).decode('unicode-escape')
        # Python 2.7 has a sweet dict comprehension, but I'll keep 2.5 compat
        result = dict((
            (ues(match.group(1)), ues(match.group(2)))
            for match in re.finditer(discrete_mapping_re, fx_string)))
        return kls(result)


class PassthroughMapping(DiscreteMapping):
    def __init__(self, map_dict):
        super(PassthroughMapping, self).__init__(map_dict)

    def transform(self, value):
        return self.map_dict.get(value, value)


class MappingError(ValueError):
    pass
