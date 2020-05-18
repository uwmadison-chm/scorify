#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright (c) 2020 Board of Regents of the University of Wisconsin System

"""Score questionnaire responses.

Usage:
  score_data [options] <scoresheet> <datafile>
  score_data -h | --help

Options:
  -h --help            Show this screen
  --version            Show version
  --exclusions=<file>  A scoresheet with additional exclude commands
  --sheet=<num>        If using an Excel datafile as input, what sheet
                       should we use? Indexed from 0. [default: 0]
  --nans-as=<string>   Print NaNs as this [default: NaN]
  --dialect=<dialect>  The dialect for CSV files; options are 'excel' or
                       'excel-tab' [default: excel]
  --output=<file>      An output file to write to [default: STDOUT]
  -q --quiet           Don't print errors
  -v, --verbose        Print extra debugging output
"""

import os
import io
import sys
import logging
import csv
import openpyxl

import scorify
from docopt import docopt
from schema import Schema, Use, Or, And, SchemaError
from scorify import scoresheet, datafile, scorer
from scorify.utils import pp
from scorify.excel_reader import ExcelReader


def open_for_read(fname):
    return io.open(os.path.expanduser(fname), 'r', encoding='utf-8-sig')


def validate_arguments(arguments):
    s = Schema({
        '<scoresheet>': Use(open_for_read, error="Can't open scoresheet"),
        '<datafile>': Use(open_for_read, error="Can't open datafile"),
        '--sheet': Use(int),
        '--output': str,
        '--exclusions': Or(
            None, Use(open_for_read, error="Can't open exclusions")),
        '--dialect': And(
            Use(str.lower),
            lambda s: s in ['excel', 'excel-tab'],
            error="Dialect must be excel or excel-tab"),
        '--nans-as': str,
        str: object  # Ignore extras
    })
    try:
        validated = s.validate(arguments)
    except SchemaError as e:
        logging.error("Error: " + str(e))
        sys.exit(1)
    if validated['--quiet']:
        logging.root.setLevel(logging.CRITICAL)
    if validated['--verbose']:
        logging.root.setLevel(logging.DEBUG)
    return validated

def parse_arguments(argv=None):
    return docopt(
        __doc__,
        argv,
        version="Scorify {0}".format(scorify.__version__))

def main():
    logging.basicConfig(
        format="%(message)s", stream=sys.stderr, level=logging.INFO)
    score_data(parse_arguments())

def main_test(test_args):
    score_data(parse_arguments(test_args))


def read_data(thing, dialect, sheet_number=0):
    if thing.name.endswith("xls") or thing.name.endswith("xlsx"):
        wb = openpyxl.load_workbook(thing.name)
        s = wb[wb.sheetnames[sheet_number]]
        return ExcelReader(s)

    else:
        return csv.reader(thing, dialect=dialect)

def score_data(arguments):
    # This method is way too long, I know.
    validated = validate_arguments(arguments)
    logging.debug(validated)
    dialect = validated['--dialect']
    scoresheet_data = read_data(validated['<scoresheet>'], dialect=dialect)

    # First, read the scoresheet
    ss = scoresheet.Reader(scoresheet_data).read_into_scoresheet()
    if ss.has_errors():
        logging.error("Errors in {0}:".format(arguments['<scoresheet>']))
        for err in ss.errors:
            logging.error(err)
        sys.exit(1)

    # Load the data
    datafile_data = read_data(validated['<datafile>'], dialect=dialect, sheet_number=validated['--sheet'])
    df = datafile.Datafile(
        datafile_data, ss.layout_section, ss.rename_section)
    df.read()

    # Load and apply exclusions file
    if validated['--exclusions'] is not None:
        exclusions_data = read_data(
            validated['--exclusions'],
            dialect=dialect)
        exc_ss = scoresheet.Reader(exclusions_data).read_into_scoresheet()
        exc = exc_ss.exclude_section
        try:
            df.apply_exclusions(exc)
        except datafile.ExclusionError as err:
            logging.critical("Error in exclusions of {0}:".format(
                arguments['--exclusions']))
            logging.critical(err)
            sys.exit(1)

    try:
        # Apply exclusions from scoresheet
        df.apply_exclusions(ss.exclude_section)
        # Actual scoring!
        scored = scorer.Scorer.score(
            df, ss.transform_section, ss.score_section)
        scorer.Scorer.add_measures(scored, ss.measure_section)
        print_data(arguments['--output'], scored, validated['--nans-as'], dialect)

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
        sys.exit(1)


def print_data(output, sd, nans_as, dialect):
    if output == "STDOUT":
        out = csv.writer(sys.stdout, dialect=dialect)
    else:
        outfile = open(output, 'w')
        out = csv.writer(outfile, dialect=dialect)

    out.writerow(sd.header)
    for row in sd.keep:
        rk = [row.get(h, '') for h in sd.header]
        out.writerow(rk)
    for row in sd:
        rl = [pp(row[h], none_val=nans_as) for h in sd.header]
        out.writerow(rl)


if __name__ == '__main__':
    main()
