# Scorify: A simple tool for scoring psychological self-report questionnaires.

[![DOI](https://zenodo.org/badge/16382827.svg)](https://zenodo.org/badge/latestdoi/16382827)

## Background

Many psychology studies use one or more self-report questionnaires to understand their participants. These responses go into CSV files with one question per column, one participant per row.

Scoring these files is a bunch of work. Oftentimes, many questionnaires (or sub-scales) are included in one CSV file. Often, half of the questions are "reverse-scored" to combat the tendancy people have to agree with questions. Scoring these files usually means spending a whole bunch of time in Excel, and no one likes doing that.

Scorify aims to fix this.

## Try scorify on the web!

If you want to build an automatic pipeline to score your data, you'll want the python version of the tool. But if you just want to give it a try in your browser, [try our web-based tool!](http://scorify-web.glitch.me)

## Installation

scorify requires Python 3.5.

    pip install scorify

should have you set up.

## Examples

See [examples/](examples/) for some test files. To run the neurohack data and
scoresheet, do something like:

    score_data neurohack_scoresheet.csv neurohack_April+2,+2019_11.05.csv

## Getting started

Given an example CSV file, let's say you want to score 5 columns, the answers
can be 1 to 5, where the third and fifth are reversed.

| ppt  | happy1 | happy2 | happy3 | happy4 | happy5 |
| ---  | ---    | ---    | ---    | ---    | ---    |
| 3001 | 1      | 2      | 1      | 3      | 4      |
| 3002 | 4      | 1      | 5      | 1      | 2      |
| 3003 | 1      | 3      | 2      | 3      | 1      |
| ...  | ...    | ...    | ...    | ...    | ...    |

Create a scoresheet that looks like:

| A         | B       | C            | D       |
| ---       | ---     | ---          | ---     |
| layout    | header  |              |         |
| layout    | data    |              |         |
|           |         |              |         |
| transform | normal  | map(1:5,1:5) |         |
| transform | reverse | map(1:5,5:1) |         |
|           |         |              |         |
| score     | ppt     |              |         |
| score     | happy1  | happy        | normal  |
| score     | happy2  | happy        | normal  |
| score     | happy3  | happy        | reverse |
| score     | happy4  | happy        | normal  |
| score     | happy5  | happy        | reverse |
|           |         |              |         |
| measure   | happy   | mean(happy)  |         |

Then you call `score_data` with that scoresheet and datafile, like:

    score_data scoresheet.csv datafile.csv

Your output just goes to STDOUT, and you should see it renaming columns.
To save the output if it looks good, just pipe it to a file:

    score_data scoresheet.csv datafile.csv > output.csv

### Other common operations

#### Excluding participants

If some participant data is particularly messy, you can exclude it using your
scoresheet like this:

| A       | B                  | C    |
| ---     | ---                | ---  |
| exclude | ppt_id_column_name | 3001 |

#### Keeping second row headers

If your question headers have a second row with verbose question text in them,
you can keep that in the scored data by adding a `layout keep` instruction:

    layout header
    layout keep
    layout data

Repeat the layout keep instruction if you want to keep more than one row.

## Scoresheet reference

The main input to scorify is a comma or tab-delimited "scoresheet" that has many rows and four columns. The first column tells what kind of command the row will be, and will be one of: `layout`, `exclude`, `transform`, `score`, or `measure`.

### layout

The layout section tells scorify what your input data looks like. It must contain a `header` and `data`, but `skip` and `keep` are also valid. `data` tells scorify that the rest of your input file is data. So:

    layout header
    layout skip
    layout data

would tell scorify to expect a header row, skip a line, and then read the rest of the file as data.

    layout header
    layout keep
    layout data

would result in scorify expecting a header row, keeping the next line as-is,
and reading the rest of the file as data.

### rename

The rename section renames a header column, and looks like:

    rename original_name new_name

Columns can only be renamed once, and must use a new, unique name. You must use the column's new name everywhere in the scoresheet.

### exclude

The format of an exclude line is:

    exclude column value

which will, as you might expect, exclude rows where `column` == `value`.

### transform

Sometimes, you'll want to reverse-score a column or otherwise change its value for scoring. And you'll want to give that some kind of sane name. Transforms let you do this. They look like:

    transform name mapper

Right now, you can apply two transformations.

#### `map()`

A linear mapping. Example:

    transform reverse map(1:5,5:1)

which will map the values 1,2,3,4,5 to 5,4,3,2,1. This will happily map values outside its input domain.

#### `discrete_map()`

A mapping for discrete values. Useful to map a numbers to human-meaningful values.

    transform score_gender discrete_map("1":"f", "2":"m")

Unmapped values will return a blank.

This transform can be useful when combined with `join()` (below) to combine an array of checkboxes into one column.

#### `passthrough_map()`

Like `discrete_map()`, though unmapped values will be unchanged. So, if you have:

    transform score_gender passthrough_map("1":"f", "2":"m")

a value of "999" will still be "999".

### score

The score section is where you tell scorify which columns you want in your output, what measure (if any) they belong to, and what transform (again, if any) you want to apply. These look like

    score column measure_name transform

`measure_name` and `transform` are both optional. So, to reverse score (using the `reverse` we defined up above) a column called `happy_1` and add it to the `happy` measure, use:

    score happy_1 happy reverse

You can optionally pass a 5th value, which will define the output column name:

    score happy_1 happy reverse ReverseHappy1

### measure

The measure section computes aggregate measures of your scored data. These lines look like:

    measure final_name aggregator(measure_1, measure_2, ..., measure_n)

We support the following aggregators:

#### `mean()`

As you might expect, this calculates the mean of the measure or measures listed. Example:

    measure happy mean(happy)

If any values in the measures are non-numeric, returns NaN.

#### `mean_imputed()`

Computes the mean of the measure. However, if any of the values in the measures are non-numeric, this fills in the mean of the numeric values. For example, `mean_imputed(1, '', 3, 5)` is `3`.

#### `sum()`

Computes the sum fo the listed measures. Example:

    measure sad sum(sad)

If any values in the measures are non-numeric, returns NaN.

#### `sum_imputed()`

Computes the sum of the measure. However, if any of the values in the measures are non-numeric, this fills in the mean of the numeric values. For example, `sum_imputed(1, '', 3, 5)` is `12`.

#### `imputed_fraction()`

The fraction of the data that is non-zero and would have a value imputed for it. `imputed_fraction(1, '', 3, 5)` is 0.25.

#### `join()`

`join()` is a little trickier. It collects all the non-blank values in the listed measures, and joins them with the `|` character. Useful if you have a set of values selected by checkbox. For example, if you had three measures that would either be blank or not for things participants might endorse, you could collate them into one column with:

    measure liked_pets join(likes_cats, likes_dogs, likes_horses)

If a participant had `cats` for `likes_cats` and `horses` for `likes_horses`, you'd get:

    cats|horses

#### `ratio()`

`ratio(a, b)` will compute the ratio of two columns; in other words: `a / b`. Notably, this works on other measures, so you can take the ratio of sums or means. In those cases, the ratio line needs to come after the other measures' lines do.

#### `min()`

`min(measure_1, measure_2)` will output the minimum numeric value in the given measures. Non-numeric values will cause NaN.

#### `max()`

`max(measure_1, measure_2)` will output the maximum numeric value in the given measures. Non-numeric values will cause NaN.

## Complete example

If you take a scoresheet that looks like:

| A         | B               | C                             | D       |
| ---       | ---             | ---                           | ---     |
| layout    | header          |                               |         |
| layout    | data            |                               |         |
|           |                 |                               |         |
| exclude   | PPT_COL         | bad_ppt1                      |         |
| exclude   | PPT_COL         | bad_ppt2                      |         |
|           |                 |                               |         |
| transform | normal          | map(1:5,1:5)                  |         |
| transform | reverse         | map(1:5,5:1)                  |         |
|           |                 |                               |         |
| score     | PPT_COL         |                               |         |
| score     | HAPPY_Q1        | happy                         | normal  |
| score     | SAD_Q1          | happy                         | normal  |
| score     | HAPPY_Q2        | happy                         | reverse |
|           |                 |                               |         |
| measure   | happy_score     | mean(happy)                   |         |
| measure   | sad_score       | mean(sad)                     |         |
| measure   | happiness_ratio | ratio(happy_score, sad_score) |         |

and run it on data that looks like:

| PPT_COL | EXTRA | HAPPY_Q1 | SAD_Q1 | HAPPY_Q2 |
| ---     | ---   | ---      | ---    | ---      |
| ppt1    | foo   | 4        | 2      | 2        |
| ppt2    | bar   | 2        | 5      | 5        |

... you'll get output like:

| PPT_COL | HAPPY_Q1: happy | SAD_Q1: sad | HAPPY_Q2: happy | happy_score | sad_score | happiness_ratio |
| ---     | ---             | ---         | ---             | ---         | ---       | ---             |
| ppt1    | 4               | 2           | 3               | 3.5         | 2         | 1.75            |
| ppt2    | 2               | 5           | 1               | 1.5         | 5         | 0.3             |


## Running multiple scoresheets

Scorify now ships with a tool called `score_multi` that takes a CSV file, and for each row in the file (except headers), runs `score_data`. The input, scoresheet, and output options are templates formatted with python's `format_map()` function with the current row of the CSV file as a map. In addition, the output headers may similarly be formatted with `format_map()`.

TODO: More documentation here! For now, run `score_multi -h`

## Reliability tool

The `reliability` command reads a scoresheet and a datafile and outputs
Cronbach's alpha for each measure, Cronbach's alpha for each measure omitting each
question for that measure, the Mahalanobis distance for each participant, and the
p value for each Mahalanobis distance.

    $ reliability examples/test_alpha_scoresheet.csv examples/test_alpha_data.csv

By default, any missing answers are handled by ignoring all of that participant's data
(list-wise deletion). Give the `--imputation` flag to instead fill in any missing response 
with the average (across participants) response to the question. If you get NaNs for the
Mahalanobis distance, it's probably because numpy failed to compute an inverse for the
covariance matrix.

## Credits

Scorify was written by Nate Vack <njvack@wisc.edu> and Dan Fitch <dfitch@wisce.du>. Scorify is copyright 2023 by the Boards of Regents of the University of Wisconsin System.

Scorify uses several excellent libraries:

* [docopt](https://github.com/docopt/docopt)
* [schema](https://github.com/halst/schema)
* [openpyxl](https://openpyxl.readthedocs.io/)

