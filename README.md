# Welcome to the scorify project

A simple tool for scoring psychological self-report questionnaires.

## Background

Many psychology studies use one or more self-report questionnaires to understand their participants. These responses go into CSV files with one question per column, one participant per row.

Scoring these files is a bunch of work. Oftentimes, many questionnaires (or sub-scales) are included in one CSV file. Often, half of the questions are "reverse-scored" to combat the tendancy people have to agree with questions. Scoring these files usually means spending a whole bunch of time in Excel, and no one likes doing that.

Scorify aims to fix this.

## Installation

scorify has no dependencies (execpt Python 2.? probably 5) or greater. So:

`pip install scorify`

should have you set up.

## Getting started

TODO write this section

## Scoresheet reference

The main input to scorify is a comma or tab-delimited "scoresheet" that has many rows and four columns. The first column tells what kind of command the row will be, and will be one of: `layout`, `exclude`, `transform`, `score`, or `measure`.

### layout

The layout section tells scorify what your input data looks like. It must contain a `header` and `data`, but `skip` is also valid. `data` tells scorify that the rest of your input file is data. So:

```
layout header
layout skip
layout data
```

would tell scorify to expect a header row, skip a line, and then read the rest of the file as data.

### rename

The rename section renames a header column, and looks like:

`rename original_name new_name`

Columns can only be renamed once, and must use a new, unique name. You must use the column's new name everywhere in the scoresheet.

### exclude

The format of an exclude line is:

`exclude column value`

which will, as you might expect, exclude rows where `column` == `value`.

### transform

Sometimes, you'll want to reverse-score a column or otherwise change its value for scoring. And you'll want to give that some kind of sane name. Transforms let you do this. They look like:

`transform name mapper`

Right now, you can apply two transformations.

#### `map()`

A linear mapping. Example:

`transform reverse map(1:5,5:1)`

which will map the values 1,2,3,4,5 to 5,4,3,2,1. This will happily map values outside its input domain.

#### `discrete_map()`

A mapping for discrete values. Useful to map a numbers to human-meaningful values.

`transform score_gender discrete_map("1":"f", "2":"m")`

Unmapped values will return a blank.

This transform can be useful when combined with `join()` (below) to combine an array of checkboxes into one column.

#### `passthrough_map()`

Like `discrete_map()`, though unmapped values will be unchanged. So, if you have:

`transform score_gender passthrough_map("1":"f", "2":"m")`

a value of "999" will still be "999".

### score

The score section is where you tell scorify which columns you want in your output, what measure (if any) they belong to, and what transform (again, if any) you want to apply. These look like

`score column measure_name transform`

`measure_name` and `transform` are both optional. So, to reverse score (using the `reverse` we defined up above) a column called `happy_1` and add it to the `happy` measure, use:

`score happy_1 happy reverse`

### measure

The measure section computes aggregate measures of your scored data. These lines look like:

`measure final_name aggregator(measure_1, measure_2, ..., measure_n)`

We support the following aggregators:

#### `mean()`

As you might expect, this calculates the mean of the measure or measures listed. Example:

`measure happy mean(happy)`

If any values in the measures are non-numeric, returns NaN.

#### `mean_imputed()`

Computes the mean of the measure. However, if any of the values in the measures are non-numeric, this fills in the mean of the numeric values. For example, `mean_imputed(1, '', 3, 5)` is `3`.

#### `sum()`

Computes the sum fo the listed measures. Example:

`measure sad sum(sad)`

If any values in the measures are non-numeric, returns NaN.

#### `sum_imputed()`

Computes the sum of the measure. However, if any of the values in the measures are non-numeric, this fills in the mean of the numeric values. For example, `sum_imputed(1, '', 3, 5)` is `12`.

#### `imputed_fraction()`

The fraction of the data that is non-zero and would have a value imputed for it. `imputed_fraction(1, '', 3, 5)` is 0.25.

#### `join()`

`join()` is a little trickier. It collects all the non-blank values in the listed measures, and joins them with the `|` character. Useful if you have a set of values selected by checkbox. For example, if you had three measures that would either be blank or not for things participants might endorse, you could collate them into one column with:

`measure liked_pets join(likes_cats, likes_dogs, likes_horses)`

If a participant had `cats` for `likes_cats` and `horses` for `likes_horses`, you'd get:

`cats|horses`

#### `ratio()`

`ratio(a, b)` will compute the ratio of two columns; in other words: `a / b`. Notably, this works on other measures, so you can take the ratio of sums or means. In those cases, the ratio line needs to come after the other measures' lines do.

#### `min()`

`min(measure_1, measure_2)` will output the minimum numeric value in the given measures. Non-numeric values will cause NaN.

#### `max()`

`max(measure_1, measure_2)` will output the maximum numeric value in the given measures. Non-numeric values will cause NaN.

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
<tr><td>measure</td><td>happiness_ratio</td><td>ratio(happy_score, sad_score)</td><td> </td></tr>
</table>

and run it on data that looks like:

<table>
<tr><td>PPT_COL</td><td>EXTRA</td><td>HAPPY_Q1</td><td>SAD_Q1</td><td>HAPPY_Q2</td></tr>
<tr><td>ppt1</td><td>foo</td><td>4</td><td>2</td><td>2</td></tr>
<tr><td>ppt2</td><td>bar</td><td>2</td><td>5</td><td>5</td></tr>
</table>

... you'll get output like:

<table>
<tr><td>PPT_COL</td><td>HAPPY_Q1: happy</td><td>SAD_Q1: sad</td><td>HAPPY_Q2: happy</td><td>happy_score</td><td>sad_score</td><td>happiness_ratio</td></tr>
<tr><td>ppt1</td>4<td></td><td>2</td><td>3</td><td>3.5</td><td>2</td><td>1.75</td></tr>
<tr><td>ppt2</td>2<td></td><td>5</td><td>1</td><td>1.5</td><td>5</td><td>0.3</td></tr>
</table>

## Credits

Scorify packages two excellent libraries: [docopt](https://github.com/docopt/docopt) and [schema](https://github.com/halst/schema).

docopt is copyright (c) 2013 Vladimir Keleshev, vladimir@keleshev.com

schema is copyright (c) 2012 Vladimir Keleshev, vladimir@keleshev.com

Hey, look at that! Same guy.