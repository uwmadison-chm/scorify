#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright (c) 2024 Board of Regents of the University of Wisconsin System

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
  --output=<file>      An output file to write to (if blank, writes to STDOUT)
  -q --quiet           Only print errors
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

logging.basicConfig(format="%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def open_for_read(fname):
    return io.open(os.path.expanduser(fname), "r", encoding="utf-8-sig")


def validate_arguments(arguments):
    s = Schema(
        {
            "<scoresheet>": Use(open_for_read, error="Can't open scoresheet"),
            "<datafile>": Use(open_for_read, error="Can't open datafile"),
            "--sheet": Use(int),
            "--output": Or(str, None),
            "--exclusions": Or(None, Use(open_for_read, error="Can't open exclusions")),
            "--dialect": And(
                Use(str.lower),
                lambda s: s in ["excel", "excel-tab"],
                error="Dialect must be excel or excel-tab",
            ),
            "--nans-as": str,
            str: object,  # Ignore extras
        }
    )
    try:
        validated = s.validate(arguments)
    except SchemaError as e:
        logger.error("Error: " + str(e))
        sys.exit(1)
    return validated


def read_data(thing, dialect, sheet_number=0):
    if thing.name.endswith("xls") or thing.name.endswith("xlsx"):
        wb = openpyxl.load_workbook(thing.name)
        s = wb[wb.sheetnames[sheet_number]]
        return ExcelReader(s)

    else:
        return csv.reader(thing, dialect=dialect)


def score_data(scoresheet_file, data_file, exclusions, dialect, sheet):
    # This method is way too long, I know.
    scoresheet_data = read_data(scoresheet_file, dialect=dialect)

    # First, read the scoresheet
    ss = scoresheet.Reader(scoresheet_data).read_into_scoresheet()
    if ss.has_errors():
        logger.error("Errors in {0}:".format(scoresheet_file))
        for err in ss.errors:
            logger.error(err)
        sys.exit(1)

    # Load the data
    datafile_data = read_data(data_file, dialect=dialect, sheet_number=sheet)
    df = datafile.Datafile(datafile_data, ss.layout_section, ss.rename_section)
    df.read()

    # Load and apply exclusions file
    if exclusions is not None:
        exclusions_data = read_data(exclusions, dialect=dialect)
        exc_ss = scoresheet.Reader(exclusions_data).read_into_scoresheet()
        exc = exc_ss.exclude_section
        df.apply_exclusions(exc)

    # Apply exclusions from scoresheet
    df.apply_exclusions(ss.exclude_section)
    # Actual scoring!
    scored = scorer.Scorer.score(df, ss.transform_section, ss.score_section)
    scorer.Scorer.add_measures(scored, ss.aggregator_section)
    return scored


def print_data(scored_data, output, nans_as, dialect, header_map=None):
    if output is None:
        out = csv.writer(sys.stdout, dialect=dialect)
    else:
        outfile = open(output, "w")
        out = csv.writer(outfile, dialect=dialect)

    if header_map is None:
        headers_mapped = scored_data.header
        logger.debug("No header map provided, using original headers")
    else:
        headers_mapped = [h.format_map(header_map) for h in scored_data.header]
        logger.debug(f"Mapped headers to {headers_mapped}")

    logger.info(f"Writing to {output}")
    out.writerow(headers_mapped)
    for row in scored_data.keep:
        rk = [row.get(h, "") for h in scored_data.header]
        out.writerow(rk)
    for row in scored_data:
        rl = [pp(row[h], none_val=nans_as) for h in scored_data.header]
        out.writerow(rl)


def main(argv):
    args = docopt(__doc__, argv, version=f"Scorify {scorify.__version__}")
    val = validate_arguments(args)
    if val["--verbose"]:
        logger.setLevel(logging.DEBUG)
    elif val["--quiet"]:
        logger.setLevel(logging.WARNING)
    logger.debug(val)

    try:
        scored = score_data(
            val["<scoresheet>"],
            val["<datafile>"],
            val["--exclusions"],
            val["--dialect"],
            val["--sheet"],
        )
    except datafile.ExclusionError as err:
        logger.critical("Error in exclusions")
        logger.critical(err)
        sys.exit(1)
    except (scorer.ScoringError, scorer.TransformError) as err:
        logger.critical("Error in score of {0}:".format(val["<scoresheet>"]))
        logger.critical(err)
        sys.exit(1)
    except scorer.AggregationError as err:
        logger.critical("Error in measures of {0}:".format(val["<scoresheet>"]))
        logger.critical(err)
        sys.exit(1)

    print_data(scored, val["--output"], val["--nans-as"], val["--dialect"])


def entry_point():
    main(sys.argv[1:])


if __name__ == "__main__":
    entry_point()
