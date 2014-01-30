scorify
=======

A simple tool for scoring psychological self-report questionnaires.


## Background

Many psychology studies use one or more self-report questionnaires to understand their participants. Generally, these are recorded by software programs that let you download a CSV file of the results, one participant per row, one question per column.

Scoring these files is a bunch of work. Oftentimes, many questionnaires (or sub-scales) are included in one CSV file. Often, half of the questions are "reverse-scored" to combat the tendancy people have to agree with questions. Scoring these files usually means spending a whole bunch of time in Excel, and no one likes doing that.

Scorify aims to fix this.

## Example

What you'll do is create a tab- or comma-separated "scoring file" that looks like:

 | 
-|-
layout | header |
layout | data... |
exclude | PPT_COL | bad_ppt1
exclude | PPT_COL | bad_ppt2
transform | normal | map(1:5, 1:5)
transform | reverse | map(1:5, 5:1)
score | PPT_COL
score | HAPPY_Q1 | HAPPY | normal
score | SAD_Q1 | SAD | normal
score | HAPPY_Q2 | HAPPY | reverse
measure | HAPPY_SCORE | mean(HAPPY)
measure | SAD_SCORE | mean(SAD)

When run on data that contains PPT_COL, HAPPY_Q1, SAD_Q1, and HAPPY_Q2 columns, the output will be:

PPT_COL | HAPPY_Q1 (HAPPY) | SAD_Q1 (SAD) | HAPPY_Q2 (HAPPY) | HAPPY_SCORE | SAD_SCORE
--------|------------------|--------------|------------------|-------------|----------
ppt1 | 4 | 2 | 3 | 3.5 | 2
ppt2 | 2 | 5 | 1 | 1.5 | 5