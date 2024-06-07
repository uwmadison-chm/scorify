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
    -q --quiet            Only print errors
    -v, --verbose         Print extra debugging output
"""

# We're going to use score_data to do the actual scoring
import scorify
from scorify.scripts import score_data

from docopt import docopt
from schema import Schema, Use, SchemaError

from csv import DictReader
from pathlib import Path
import sys

import logging

logging.basicConfig(format="%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def open_for_read(fname):
    return Path(fname).expanduser().open("r", encoding="utf-8-sig")


def validate_arguments(args):
    s = Schema(
        {
            "<multi_csv>": Use(open_for_read),
            "<scoresheet>": str,
            "<data>": str,
            "<output>": str,
            "--sheet": str,
            "--nans-as": str,
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
    validated["--format-headers"] = not validated["--no-format-headers"]
    return validated


def format_str_or_none(value, row):
    """
    Format a string with a row from our CSV file, or return None if the value's
    not defined.
    """
    return value.format_map(row) if value else None


def format_int_or_none(value, row):
    """
    Format an int (and return it as int type) or return None if the value's not
    defined.
    """
    return int(value.format_map(row)) if value else None


def score_single(scoresheet_filename, data_filename, sheet_num):
    with open(scoresheet_filename, "r", encoding="utf-8-sig") as scoresheet_file:
        with open(data_filename, "r", encoding="utf-8-sig") as data_file:
            return score_data.score_data(
                scoresheet_file, data_file, None, "excel", sheet_num
            )


def format_and_print(scored_data, output_filename, format_headers, row, nans_as):
    header_formatter = row if format_headers else None
    score_data.print_data(
        scored_data, output_filename, nans_as, "excel", header_formatter
    )


def score_multi(
    multi_csv, scoresheet, data, output, sheet, dry_run, format_headers, nans_as
):
    csv_reader = DictReader(multi_csv)
    for row in csv_reader:
        logger.debug(f"Processing row: {row}")
        scoresheet_filename = Path(scoresheet.format_map(row)).expanduser()
        data_filename = Path(data.format_map(row)).expanduser()
        output_filename = Path(output.format_map(row)).expanduser()
        sheet_num = format_int_or_none(sheet, row)

        logger.info(f"Scoring {data_filename} with {scoresheet_filename}")
        try:
            scored = score_single(scoresheet_filename, data_filename, sheet_num)
        except Exception as e:
            logger.error(f"Error scoring {data_filename}: {e}")
            continue
        if dry_run:
            logger.info(f"--dry-run: would have written to {output_filename}")
        else:
            format_and_print(scored, output_filename, format_headers, row, nans_as)


def main(argv):
    args = docopt(__doc__, argv, version=f"Scorify {scorify.__version__}")
    val = validate_arguments(args)
    if val["--quiet"]:
        logger.setLevel(logging.WARNING)
    if val["--verbose"]:
        logger.setLevel(logging.DEBUG)
    score_data.logger = logger

    logger.debug(f"validated arguments: {val}")
    score_multi(
        val["<multi_csv>"],
        val["<scoresheet>"],
        val["<data>"],
        val["<output>"],
        val["--sheet"],
        val["--dry-run"],
        val["--format-headers"],
        val["--nans-as"],
    )


def entry_point():
    main(sys.argv[1:])


if __name__ == "__main__":
    entry_point()
