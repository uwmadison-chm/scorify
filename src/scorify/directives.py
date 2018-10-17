# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System
from __future__ import absolute_import

from scorify import mappings
from scorify import aggregators

"""
Directives define operations we'll be performing on our input data files.
A scoresheet defines a set of directives; directive will be run on the input.

Examples include:
layout: Defines the header row and any rows we'll want to skip

exclude: Defines any rows we'll want to exclude from processing

transform: Shortcut names that define mappings

score: A column, a classification for the column, and the transform to run

measure: How to aggregate scored columns into directly-usable measurements
"""


class Layout(object):
    """
    Informs us about the layout of the data. They're processed in order; each
    layout directive corresponds to one line in your data file, except for a
    "data" layout which will read to the end fo the data file. Valid types are
    "header", "skip" and "data".

    If your input file looks like:
    COMMENT
    HEADER
    DESCRIPTION
    START OF DATA

    you'll use layout directives like:
    layout skip
    layout header
    layout skip
    layout data
    """

    def __init__(self, info):
        info_lower = info.strip().lower()
        if info_lower not in set(['header', 'data', 'skip']):
            raise DirectiveError(
                "Didn't understand layout {0!r}".format(info))

        self.info = info_lower
        super(Layout, self).__init__()


class Rename(object):
    """
    Renames a column. Renamed columns must be referred to by the new name.
    Does not allow giving a 0-length name. Empty names or names will be
    rejected, too. Sorry if your column names are blank.

    All logic for this is in the datafile, since that's the only place where
    we know column names.
    """
    def __init__(self, original_name, new_name):
        self.original_name = str(original_name)
        self.new_name = str(new_name)
        if len(self.original_name) == 0:
            raise DirectiveError("Can't rename a blank column.")
        if len(self.new_name) == 0:
            raise DirectiveError("Can't give a column a blank name.")
        if self.original_name == self.new_name:
            raise DirectiveError(
                "Can't rename a column to its original name.")

    def conflicts_with(self, other):
        return (
            self.original_name == other.original_name or
            self.original_name == other.new_name or
            self.new_name == other.new_name or
            self.new_name == other.original_name)

    def __str__(self):
        return "rename %s %s" % (self.original_name, self.new_name)


class Exclude(object):
    """
    Skips a line in the data based on a column being equal to some value. So:

    exclude PARTICIPANT 001-1234

    would exclude a line in the input file where PARTICIPANT equales 001-1234.
    """

    def __init__(self, column, value):
        self.column = column
        self.value = value.strip()
        super(Exclude, self).__init__()

    def excludes(self, row):
        return str(row[self.column]).strip() == self.value


class Transform(object):
    """
    Defines a named, shortcut transforation -- a simple function that operates
    on a single cell. Common examples would be:

    transform normal map(1:5, 1:5)
    transform reverse map(1:5, 5:1)

    If the third parameter is not specified, the identity mapping is assumed.
    """

    def __init__(self, name, fx_def):
        self.name = name
        self.fx_def = fx_def
        self.mapping = mappings.Mapping.from_string(fx_def)
        super(Transform, self).__init__()

    def transform(self, value):
        return self.mapping.transform(value)


class Score(object):
    """
    Tells us we want a given data column to appear in our output; allows us
    to specify what measure the column is used in and what transform should
    be applied to it. Examples:

    score PARTICIPANT
    score DATA_COL_1 MEASURE_1 normal
    score DATA_COL_2 MEASURE_1 reverse


    If the measure name is blank, the column doesn't get added to any measure.
    If the transform is blank, the data is copied without any changes.
    """

    def __init__(self, column, measure_name, transform=None):
        self.column = column
        self.measure_name = measure_name
        self.transform = transform
        super(Score, self).__init__()


class Measure(object):
    """
    Defines an aggregation (usually sum or mean or maybe count?) of scored
    columns. Examples:

    measure MEASURE_1_MEAN mean(MEASURE_1)
    """

    def __init__(self, name, aggregation_expr):
        self.name = name
        self.aggregation_expr = aggregation_expr
        try:
            fname, fx, to_use = aggregators.parse_expr(aggregation_expr)
            self.agg_fx = fx
            self.to_use = to_use

        except aggregators.AggregatorError as exc:
            raise DirectiveError(str(exc))

        super(Measure, self).__init__()


class DirectiveError(ValueError):
    pass
