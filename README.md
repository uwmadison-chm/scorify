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

## Scoresheets

The main input to scorify is a comma or tab-delimited "scoresheet" that has many rows and four columns. The first column tells what kind of command the row will be, and will be one of: `layout`, `exclude`, `transform`, `score`, or `measure`.

### layout

The layout section tells scorify what your input data looks like. It must contain a `header` and `data`, but `skip` is also valid. `data` tells scorify that the rest of your input file is data. So:

```
layout header
layout skip
layout data
```

would tell scorify to expect a header row, skip a line, and then read the rest of the file as data.

### exclude

The format of an exclude line is:

`exclude column value`

which will, as you might expect, exclude rows where `column` == `value`.

### transform

Sometimes, you'll want to reverse-score a column or otherwise change its value for scoring. And you'll want to give that some kind of sane name. Transforms let you do this. They look like:

`transform name mapper`

Right now, the only mapper you can use is a linear mapping function. To reverse-score a 1-5 scale, you can:

`transform reverse map(1:5,5:1)`

which will map the values 1,2,3,4,5 to 5,4,3,2,1.

### score

The score section is where you tell scorify which columns you want in your output, what measure (if any) they belong to, and what transform (again, if any) you want to apply. These look like

`score column measure_name transform`

`measure_name` and `transform` are both optional. So, to reverse score (using the `reverse` we defined up above) a column called `happy_1` and add it to the `happy` measure, use:

`score happy_1 happy reverse`

### measure

The measure section computes aggregate measures of your scored data. These lines look like:

`measure final_name aggregator(measure_name)`

The aggregators we currently support are `sum()` and `mean()` (and I hope you can guess what those do) adding more would be really easy. So, to compute the sum of the `happy` measure and write it to a `happy` column, you'd say:

`measure happy sum(happy)`

## Complete example

If you take a scoresheet that looks like:

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

and run it on data that looks like:

<table>
<tr><td>PPT_COL</td><td>EXTRA</td><td>HAPPY_Q1</td><td>SAD_Q1</td><td>HAPPY_Q2</td></tr>
<tr><td>ppt1</td><td>foo</td><td>4</td><td>2</td><td>2</td></tr>
<tr><td>ppt2</td><td>bar</td><td>2</td><td>5</td><td>5</td></tr>
</table>

and you'll get output like:

<table>
<tr><td>PPT_COL</td><td>HAPPY_Q1: happy</td><td>SAD_Q1: sad</td><td>HAPPY_Q2: happy</td><td>happy_score</td><td>sad_score</td></tr>
<tr><td>ppt1</td>4<td></td><td>2</td><td>3</td><td>3.5</td><td>2</td></tr>
<tr><td>ppt2</td>2<td></td><td>5</td><td>1</td><td>1.5</td><td>5</td></tr>
</table>

## Credits

Scorify packages two excellent libraries: [docopt](https://github.com/docopt/docopt) and [schema](https://github.com/halst/schema).

docopt is copyright (c) 2013 Vladimir Keleshev, vladimir@keleshev.com

schema is copyright (c) 2012 Vladimir Keleshev, vladimir@keleshev.com

Hey, look at that! Same guy.