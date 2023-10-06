
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
import pandas as pd
import numpy as np
#import pingouin

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


# if we want to use pingouin, we cna delete this
def get_alpha(df):
    n = df.shape[1]
    if (n <= 1):
        return 1.0

    # the 'Sigma_i(v_t)' in the numerator
    sum_variance = df.var().sum()

    # the 'v_t' in the denominator
    total_variance = df.sum(axis=1).var()

    if (total_variance == 0):
        logging.warning("Chronbach's alpha failed: can't divide by zero total variance")
        return -1  # I don't know what to do here

    result = (n/(n-1)) * (1 - (sum_variance / total_variance))
    return result




def isnumber(x):
    try:
        float(x)
        return True
    except:
        return False


def print_row(a,b,c,d):
    print(f"{a:>15}{b:>12}{c:>12}{d:>12}")

def make_row(label, df):

    numpy = df.to_numpy()
    mean = np.mean(numpy)
    stdev = np.std(numpy)
    alpha = get_alpha(df)

    # if this is all we're using pingouin for, we could just us get_alpha
    #(alpha, confidence) = pingouin.cronbach_alpha(df)

    print_row(label,
              f"{mean:11.4f}",
              f"{stdev:6.4f}",
              f"{alpha:6.4f}")


def compute_reliability(arguments):

    # process inputs
    validated = validate_arguments(arguments)
    logging.debug(validated)
    sheet = load_scoresheet(validated['<scoresheet>'], validated['--dialect'])
    raw_data = load_datafile(validated['<datafile>'],
                             validated['--dialect'],
                             validated['--page-number'],
                             validated['--exclusions'],
                             sheet).data

    # load the data indo a pandas dataframe
    df = pd.DataFrame(data=raw_data)

    #remove metadata columns
    df = df[sheet.score_section.all_questions]

    # turn any empty cells, string, etc. into NaNs
    df = df[df.applymap(isnumber)]

    # turn everything into floats
    df = df.applymap(float)

    # get rid of NaNs
    if (validated['--imputation']):
        df.fillna(df.mean(), inplace=True)
    else:
        df.dropna(inplace=True)

    # print header for measures section
    print_row('', 'mean', 'stdev', 'alpha')

    for measure in sheet.score_section.get_measures():
        questions = sheet.score_section.questions_by_measure[measure]
        print()
        make_row(measure, df[questions])
        for q in questions:
            make_row("omit " + q, df[questions].drop(q, axis=1, inplace=False))





if __name__ == '__main__':
    main()
