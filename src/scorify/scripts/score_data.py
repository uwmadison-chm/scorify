#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

"""Score questionnaire responses.

Usage:
  score_data [options] <scoresheet> <datafile>
  score_data -h | --help

Options:
  -h --help            Show this screen
  --version            Show version
  --exclusions=<file>  A scoresheet with additional exclude commands
  --nans-as=<string>   Print NaNs as this [default: NaN]
  --dialect=<dialect>  The dialect for CSV files; options are 'excel' or
                       'excel-tab' [default: excel]
  -q --quiet           Don't print errors
  -v, --verbose        Print extra debugging output
"""

import os
import io
import sys
import csv
import logging

import scorify
from scorify.vendor.docopt import docopt
from scorify.vendor.schema import Schema, Use, Or, And, SchemaError
from scorify import scoresheet, datafile, scorer
from scorify.utils import pp


def open_for_read(fname):
    return io.open(os.path.expanduser(fname), 'rU', encoding='utf-8-sig')


def validate_arguments(arguments):
    s = Schema({
        '<scoresheet>': Use(open_for_read, error="Can't open scoresheet"),
        '<datafile>': Use(open_for_read, error="Can't open datafile"),
        '--exclusions': Or(
            None, Use(open_for_read, error="Can't open exclusions")),
        '--dialect': And(
            Use(str.lower),
            lambda s: s in ['excel', 'excel-tab'],
            error="Dialect must be excel or excel-tab"),
        '--nans-as': str,
        str: object  # Ignore extras
    })
    return s.validate(arguments)


def main():
    logging.basicConfig(
        format="%(message)s", stream=sys.stderr, level=logging.INFO)
    arguments = docopt(
        __doc__,
        version="Scorify {0}".format(scorify.__version__))
    score_data(arguments)


def score_data(arguments):
    # This method is way too long, I know.
    try:
        validated = validate_arguments(arguments)
    except SchemaError as e:
        logging.error("Error: " + str(e))
        sys.exit(1)
    if validated['--quiet']:
        logging.root.setLevel(logging.CRITICAL)
    if validated['--verbose']:
        logging.root.setLevel(logging.DEBUG)
    logging.debug(validated)
    dialect = validated['--dialect']
    scoresheet_csv = csv.reader(validated['<scoresheet>'], dialect=dialect)
    # First, read the scoresheet and exclusions (if any)
    ss = scoresheet.Reader(scoresheet_csv).read_into_scoresheet()
    if ss.has_errors():
        logging.error("Errors in {0}:".format(arguments['<scoresheet>']))
        for err in ss.errors:
            logging.error(err)
        sys.exit(1)

    exc = None
    if validated['--exclusions'] is not None:
        exclusions_csv = csv.reader(
            validated['--exclusions'],
            dialect=dialect)
        exc_ss = scoresheet.Reader(exclusions_csv).read_into_scoresheet()
        exc = exc_ss.exclude_section
    datafile_csv = csv.reader(validated['<datafile>'], dialect=dialect)
    df = datafile.Datafile(
        datafile_csv, ss.layout_section, ss.rename_section)
    df.read()
    if exc is not None:
        try:
            df.apply_exclusions(exc)
        except datafile.ExclusionError as err:
            logging.critical("Error in exclusions of {0}:".format(
                arguments['--exclusions']))
            logging.critical(err)
            sys.exit(1)
    try:
        df.apply_exclusions(ss.exclude_section)
        scored = scorer.Scorer.score(
            df, ss.transform_section, ss.score_section)
        scorer.Scorer.add_measures(scored, ss.measure_section)
        print_data(scored, validated['--nans-as'], dialect)

    except datafile.ExclusionError as err:
        logging.critical("Error in exclusions of {0}:".format(
            arguments['<scoresheet>']))
        logging.critical(err)
        sys.exit(1)
    except (scorer.ScoringError, scorer.TransformError) as err:
        logging.critical("Error in score of {0}:".format(
            arguments['<scoresheet>']))
        logging.critical(err)
        sys.exit(1)
    except scorer.AggregationError as err:
        logging.critical("Error in measures of {0}:".format(
            arguments['<scoresheet>']))
        logging.critical(err)


def print_data(sd, nans_as, dialect):
    out = csv.writer(sys.stdout, dialect=dialect)
    out.writerow(sd.header)
    for row in sd:
        rl = [pp(row[h], none_val=nans_as) for h in sd.header]
        out.writerow(rl)

if __name__ == '__main__':
    main()
