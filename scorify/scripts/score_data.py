#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

"""Score questionnaire responses.

Usage:
  scorify [options] <scoresheet> <datafile>

Options:
  -h --help            Show this screen
  --version            Show version
  --exclusions=<file>  A scoresheet with additional exclude commands
  --nans-as=<string>   Print NaNs as this [default: NaN]
"""

import os
import sys
import csv

import scorify
from scorify.vendor.docopt import docopt
from scorify.vendor.schema import Schema, Use, Or
from scorify import scoresheet, datafile, scorer
from scorify.utils import pp


def make_csv(fname):
    f = open(os.path.expanduser(fname), 'rU')
    try:
        dialect = csv.Sniffer().sniff(f.read())
    except:
        dialect = csv.excel
    f.seek(0)
    return csv.reader(f, dialect)


def validate_arguments(arguments):
    s = Schema({
        '<scoresheet>': Use(make_csv, error="Can't open scoresheet"),
        '<datafile>': Use(make_csv, error="Can't open datafile"),
        '--exclusions': Or(None, Use(make_csv, error="Can't open exclusions")),
        '--nans-as': str,
        str: object # Ignore extras
        })
    return s.validate(arguments)


def main():
    arguments = docopt(__doc__,
        version="Scorify {0}".format(scorify.__version__))
    valid_args = validate_arguments(arguments)
    score_data(valid_args)


def score_data(arguments):
    # First, read the scoresheet and exclusions (if any)
    ss = scoresheet.Reader(arguments['<scoresheet>']).read_into_scoresheet()

    exc = None
    if arguments['--exclusions'] is not None:
        exc_ss = scoresheet.Reader(
            arguments['--exclusions']).read_into_scoresheet()
        exc = exc_ss.exclude_section
    df = datafile.Datafile(arguments['<datafile>'], ss.layout_section)
    df.read()
    df.apply_exclusions(ss.exclude_section)
    if exc is not None:
        df.apply_exclusions(exc)

    scored = scorer.Scorer.score(df, ss.transform_section, ss.score_section)
    scorer.Scorer.add_measures(scored, ss.measure_section)
    print_data(scored, arguments['--nans-as'])


def print_data(sd, nans_as):
    out = csv.writer(sys.stdout, delimiter="\t")
    out.writerow(sd.header)
    for row in sd:
        rl = [pp(row[h], none_val=nans_as) for h in sd.header]
        out.writerow(rl)

if __name__ == '__main__':
    main()