scorify
=======

A simple tool for scoring psychological self-report questionnaires.

## Background

Many psychology studies use one or more self-report questionnaires to understand their participants. Generally, these are recorded by software programs that let you download a CSV file of the results, one participant per row, one question per column.

Scoring these files is a bunch of work. Oftentimes, many questionnaires (or sub-scales) are included in one CSV file. Often, half of the questions are "reverse-scored" to combat the tendancy people have to agree with questions. Scoring these files usually means spending a whole bunch of time in Excel, and no one likes doing that.

Scorify aims to fix this.

## Installation

scorify has no dependencies (execpt Python 2.? probably 5) or greater. So:

`pip install scorify`

should have you set up.

## Installed commands:

#### `score_data`

    Score questionnaire responses.

    Usage:
      scorify [options] <scoresheet> <datafile>
      scorify -h | --help

    Options:
      -h --help            Show this screen
      --version            Show version
      --exclusions=<file>  A scoresheet with additional exclude commands
      --nans-as=<string>   Print NaNs as this [default: NaN]
      -q --quiet           Don't print errors

## Example scoresheet

What you'll do is create a tab- or comma-separated "scoresheet" that looks like:

<table>
<tr><td>layout</td><td>header</td><td> </td><td> </td></tr>
<tr><td>layout</td><td>data</td><td> </td><td> </td></tr>
<tr><td>exclude</td><td>PPT_COL</td><td>bad_ppt1</td><td> </td></tr>
<tr><td>exclude</td><td>PPT_COL</td><td>bad_ppt2</td><td> </td></tr>
<tr><td>transform</td><td>normal</td><td>map(1:5, 1:5)</td><td> </td></tr>
<tr><td>transform</td><td>reverse</td><td>map(1:5, 5:1)</td><td> </td></tr>
<tr><td>score</td><td>PPT_COL</td><td> </td><td> </td></tr>
<tr><td>score</td><td>HAPPY_Q1</td><td>happy</td><td>normal</td></tr>
<tr><td>score</td><td>SAD_Q1</td><td>sad</td><td>normal</td></tr>
<tr><td>score</td><td>HAPPY_Q2</td><td>happy</td><td>reverse</td></tr>
<tr><td>measure</td><td>happy_score</td><td>mean(happy)</td><td> </td></tr>
<tr><td>measure</td><td>sad_score</td><td>mean(sad)</td><td> </td></tr>
</table>

When run on data that contains PPT_COL, HAPPY_Q1, SAD_Q1, and HAPPY_Q2 columns, the output will be:

PPT_COL | HAPPY_Q1 (happy) | SAD_Q1 (sad) | HAPPY_Q2 (happy) | happy_score | sad_score
--------|------------------|--------------|------------------|-------------|----------
ppt1 | 4 | 2 | 3 | 3.5 | 2
ppt2 | 2 | 5 | 1 | 1.5 | 5


## Credits

Scorify packages two excellent libraries: [docopt](https://github.com/docopt/docopt) and [schema](https://github.com/halst/schema).

docopt is copyright (c) 2013 Vladimir Keleshev, vladimir@keleshev.com
schema is copyright (c) 2012 Vladimir Keleshev, vladimir@keleshev.com

Hey, look at that! Same guy.