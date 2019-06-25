# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

"""
A set of exceptions for scorify.
"""


class HaystackError(KeyError):
    def __init__(self, haystack_name, needle, haystack):
        msg = "Can't find {0} in {1}.\nPossible values: {2}".format(
            needle, haystack_name, ", ".join(haystack))
        super(LookupError, self).__init__(msg)
