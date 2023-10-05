
"""Compute reliability metrics

Usage:
  reliability [options] <scoresheet> <datafile>
  reliability -h | --help

Options:
  -h --help              Show this screen
  --version              Show version
  --exclusions=<file>    A scoresheet with additional exclude commands
  --page-number=<num>    If using an Excel datafile as input, what sheet
                         should we use? Indexed from 0. [default: 0]
  --dialect=<dialect>    The dialect for CSV files; options are 'excel' or
                         'excel-tab' [default: excel]
  --imputation           Use mean substitution for missing values; the
                         default is to use list-wise deletion
  --output=<file>        An output file to write to [default: STDOUT]
  -q --quiet             Don't print errors
  -v, --verbose          Print extra debugging output
"""

import os
import io
import sys
import logging
import csv
import openpyxl
import math

import scorify
from docopt import docopt
from schema import Schema, Use, Or, And, SchemaError
from scorify import scoresheet, datafile
from scorify.excel_reader import ExcelReader


def open_for_read(fname):
    return io.open(os.path.expanduser(fname), 'r', encoding='utf-8-sig')


def validate_arguments(arguments):
    s = Schema({
        '<scoresheet>': Use(open_for_read, error="Can't open scoresheet"),
        '<datafile>': Use(open_for_read, error="Can't open datafile"),
        '--page-number': Use(int),
        '--output': str,
        '--exclusions': Or(
            None, Use(open_for_read, error="Can't open exclusions")),
        '--dialect': And(
            Use(str.lower),
            lambda s: s in ['excel', 'excel-tab'],
            error="Dialect must be excel or excel-tab"),
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
    compute_reliability(parse_arguments())


def main_test(test_args):
    compute_reliability(parse_arguments(test_args))


def read_data(input_filename, dialect, page_number=0):
    if input_filename.name.endswith("xls") or input_filename.name.endswith("xlsx"):
        workbook = openpyxl.load_workbook(input_filename)
        workbook_page = workbook[workbook.sheetnames[page_number]]
        return ExcelReader(workbook_page)
    else:
        return csv.reader(input_filename, dialect=dialect)

def load_scoresheet(filename, dialect):
    raw_data = read_data(filename, dialect)
    sheet = scoresheet.Reader(raw_data).read_into_scoresheet()
    if sheet.has_errors():
        logging.error("Errors in {0}:".format(filename))
        for err in sheet.errors:
            logging.error(err)
        sys.exit(1)
    return sheet

def load_datafile(filename, dialect, page_number, exclusions, sheet):
    raw_data = read_data(filename, dialect, page_number)
    data = datafile.Datafile(raw_data, sheet.layout_section, sheet.rename_section)
    data.read()
    if exclusions is not None:
        exclusions_data = read_data(exclusions, dialect=dialect)
        exclusions_scoresheet = scoresheet.Reader(exclusions_data).read_into_scoresheet()
        try:
            data.apply_exclusions(exclusions_scoresheet.exclude_section)
        except datafile.ExclusionError as err:
            logging.critical("Error in exclusions of {0}:".format(exclusions))
            logging.critical(err)
            sys.exit(1)
    return data


def mean(row):
    if (len(row) == 0):
        return 0
    return sum(row) / len(row)

def variance(row):
    if (len(row) <=1):
        return 0
    return (sum([(i - mean(row))**2 for i in row]) / (len(row)-1))

def stdev(row):
    return math.sqrt(variance(row))


# definition from https://www.youtube.com/watch?v=G0RblT5qkFQ
def alpha(data):
    n = len(data)
    if (n <= 1):
        return 1.0

    # the 'Sigma_i(v_t)' in the numerator
    sum_variance = sum([variance(row) for row in data])

    # the 'v_t' in the denominator
    total_variance = variance([sum(x) for x in zip(*data)])

    if (total_variance == 0):
        logging.warning("Chronbach's alpha failed: can't divide by zero total variance")
        return -1  # I don't know what to do here

    result = (n/(n-1)) * (1 - (sum_variance / total_variance))
    return result


# see https://www.sciencedirect.com/science/article/pii/S259029112200122X
# def omega(data):
#     return -1.0


def compute_reliability(arguments):

    # process inputs
    validated = validate_arguments(arguments)
    logging.debug(validated)
    sheet = load_scoresheet(validated['<scoresheet>'], validated['--dialect'])
    data = load_datafile(validated['<datafile>'],
                         validated['--dialect'],
                         validated['--page-number'],
                         validated['--exclusions'],
                         sheet).data

    # output header
    print(f"{'':>15}{'mean':>10}{'stdev':>10}{'alpha':>10}")

    for measure in sheet.score_section.get_measures():
        questions = sheet.score_section.questions_by_measure[measure]

        if (validated['--imputation']):
            # substitute means for missing values
            means = {q: mean([float(ppt[q]) for ppt in data if ppt[q].isnumeric()]) for q in questions}
            data_for_measure = [[float(ppt[q] if ppt[q].isnumeric() else means[q]) for ppt in data] for q in questions]
        else:
            # delete ppts with missing values
            clean = [ppt for ppt in data if all([ppt[q].isnumeric() for q in questions])]
            data_for_measure = [[float(ppt[q]) for ppt in clean] for q in questions]

        # data_for_measure is "sideways": each row has all participants' answers to one question

        flat = sum(data_for_measure, [])

        print(f"{measure:<15}{mean(flat):10.5f}{stdev(flat):10.5f}{alpha(data_for_measure):10.5f}")



if __name__ == '__main__':
    main()
