scorify
=======

A simple tool for scoring psychological self-report questionnaires.


## Background

Many psychology studies use one or more self-report questionnaires to understand their participants. Generally, these are recorded by software programs that let you download a CSV file of the results, one participant per row, one question per column.

Scoring these files is a bunch of work. Oftentimes, many questionnaires (or sub-scales) are included in one CSV file. Often, half of the questions are "reverse-scored" to combat the tendancy people have to agree with questions. Scoring these files usually means spending a whole bunch of time in Excel, and no one likes doing that.

Scorify aims to fix this.

## Example

What you'll do is create a tab- or comma-separated "scoring file" that looks like:

<table>
<tr><td>layout</td><td>header</td><td></td></tr>
<tr><td>layout</td><td>data...</td><td></td></tr>
<tr><td>exclude</td>td><td>PPT_COL</td>td><td>bad_ppt1</td></tr>
<tr><td>exclude</td>td><td>PPT_COL</td>td><td>bad_ppt2</td></tr>
<tr><td>transform</td><td>normal</td><td>map(1:5, 1:5)</td></tr>
<tr><td>transform</td><td>reverse</td><td>map(1:5, 5:1)</td></tr>
<tr><td>score</td>td><td>PPT_COL</td><td></td></tr>
<tr><td>score</td>td><td>HAPPY_Q1</td>td><td>HAPPY</td><td>normal</td></tr>
<tr><td>score</td>td><td>SAD_Q1</td>td><td>SAD</td><td>normal</td></tr>
<tr><td>score</td>td><td>HAPPY_Q2</td>td><td>HAPPY</td><td>reverse</td></tr>
<tr><td>measure</td>td><td>HAPPY_SCORE</td><td>mean(HAPPY)</td></tr>
<tr><td>measure</td>td><td>SAD_SCORE</td><td>mean(SAD)</td></tr>
</table>

When run on data that contains PPT_COL, HAPPY_Q1, SAD_Q1, and HAPPY_Q2 columns, the output will be:

PPT_COL | HAPPY_Q1 (HAPPY) | SAD_Q1 (SAD) | HAPPY_Q2 (HAPPY) | HAPPY_SCORE | SAD_SCORE
--------|------------------|--------------|------------------|-------------|----------
ppt1 | 4 | 2 | 3 | 3.5 | 2
ppt2 | 2 | 5 | 1 | 1.5 | 5