# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

import mappings

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
        if not info_lower in set(['header', 'data', 'skip']):
            raise DirectiveError("Didn't understand layout {0!r}".format(info))

        self.info = info_lower
        super(Layout, self).__init__()


class Exclude(object):
    """
    Skips a line in the data based on a column being equal to some value. So:

    exclude PARTICIPANT 001-1234

    would exclude a line in the input file where PARTICIPANT equales 001-1234.
    """

    def __init__(self, column, value):
        self.column = column
        self.value = value
        super(Exclude, self).__init__()


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

    def __init__(self, name, agg_fx):
        self.name = name
        self.agg_fx = agg_fx
        super(Measure, self).__init__()


class DirectiveError(ValueError):
    pass