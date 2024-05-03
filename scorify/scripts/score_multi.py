#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright (c) 2024 Board of Regents of the University of Wisconsin System

"""Score multiple data files at once.

score_multi takes a spreadsheet that lists data files and scoresheets and 
scores all of them at once. The input is a CSV file with one row per scoring
command, and literally whatever columns you want -- as long as the column
headers don't contain spaces.

When each row is processed, the options for scoresheet, data, output, and sheet
will all be formatted with python's str.format_map() method, with the row
as a dict passed in. This is so you can use the columns in the file to define
what data to score, where to find the scoresheet, and where to write the output.

In addition, unless --no-format-headers is passed, the header of the output data
will also be similarly formatted, so you can, for example, use the same
scoresheet to score data for multiple events.

Unlike score_data, score_multi does not support writing to STDOUT.

Usage:
    score_multi [options] <multi_csv> <scoresheet> <data> <output>
    score_multi -h | --help

Options:
    -h --help             Show this screen
    --version             Show version
    --dry-run             Don't actually write any output
    --sheet=<num>         If using an Excel datafile as input, what sheet
                          should we use? Indexed from 0. [default: 0]
    --no-format-headers   Don't do string replacement in output headers
    --nans-as=<string>    Print NaNs as this [default: NaN]
    --ignore-missing      Assume blank data if a column named in the
                          scoresheet is missing from the data
    -q --quiet            Don't print errors
    -v, --verbose         Print extra debugging output
"""

# Yes we're just going to use score_data for this. It's a little gross, but it
# also means the semantics of scoring are consistent between the two scripts.
import scorify
from scorify.scripts import score_data

from docopt import docopt
from schema import Schema, Use, Or, And, SchemaError

from csv import DictReader
from pathlib import Path
import sys

import logging

logging.basicConfig(format="%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def open_for_read(fname):
    fpath = Path(fname)
    return open(fpath.expanduser(), "r", encoding="utf-8-sig")


def validate_arguments(args):
    s = Schema(
        {
            "<multi_csv>": Use(open_for_read, error="Can't open multi_csv file"),
            "<scoresheet>": str,
            "<data>": str,
            "<output>": str,
            "--sheet": Use(int),
            "--nans-as": str,
            "--ignore-missing": bool,
            "--dry-run": bool,
            "--no-format-headers": bool,
            "--quiet": bool,
            "--verbose": bool,
            str: object,  # Ignore extras
        }
    )
    try:
        validated = s.validate(args)
    except SchemaError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    if validated["--quiet"]:
        logger.setLevel(logging.CRITICAL)
    if validated["--verbose"]:
        logger.setLevel(logging.DEBUG)
    validated["--format-headers"] = not validated["--no-format-headers"]
    return validated


def score_multi(
    multi_csv,
    scoresheet,
    data,
    output,
    sheet,
    dry_run,
    format_hedaers,
    nans_as,
    ignore_missing,
):
    csv_reader = DictReader(multi_csv)
    for row in csv_reader:
        logger.debug(f"Processing row: {row}")
        # score_data.main(
        #     {
        #         "<scoresheet>": scoresheet.format_map(row),
        #         "<datafile>": data.format_map(row),
        #         "--output": output.format_map(row),
        #         "--sheet": sheet,
        #         "--nans-as": nans_as,
        #         "--ignore-missing": ignore_missing,
        #         "--quiet": True,
        #         "--verbose": False,
        #     }
        # )


def main():
    args = docopt(__doc__, version=scorify.__version__)
    validated = validate_arguments(args)
    logger.debug(f"Validated arguments: {validated}")
    sys.exit(
        score_multi(
            validated["<multi_csv>"],
            validated["<scoresheet>"],
            validated["<data>"],
            validated["<output>"],
            validated["--sheet"],
            validated["--dry-run"],
            validated["--format-headers"],
            validated["--nans-as"],
            validated["--ignore-missing"],
        )
    )


if __name__ == "__main__":
    main()
