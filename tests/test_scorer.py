# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright (c) 2024 Board of Regents of the University of Wisconsin System

import pytest

import math
from scorify import datafile, scoresheet, scorer


@pytest.fixture
def transforms():
    ts = scoresheet.TransformSection()
    ts.append_from_strings(["reverse", "map(1:5,5:1)"])
    ts.append_from_strings(["gmap", 'discrete_map("1": "f", "2": "m")'])
    return ts


@pytest.fixture
def scores_1():
    ss = scoresheet.ScoreSection()
    ss.append_from_strings(["happy1", "happy"])
    ss.append_from_strings(["happy2", "happy", "reverse"])
    return ss


@pytest.fixture
def scores_2():
    ss = scoresheet.ScoreSection()
    ss.append_from_strings(["happy1", "happy"])
    ss.append_from_strings(["happy2", "happy", "reverse"])
    ss.append_from_strings(["sad1", "sad"])
    ss.append_from_strings(["sad2", "sad", "reverse"])
    return ss


@pytest.fixture
def scores_3():
    ss = scoresheet.ScoreSection()
    ss.append_from_strings(["happy1", "happy", "", "KINDA HAPPY"])
    ss.append_from_strings(["happy2", "happy", "reverse", "VERY HAPPY"])
    return ss


@pytest.fixture
def gender_score():
    ss = scoresheet.ScoreSection()
    ss.append_from_strings(["gender1", "gender", "gmap"])
    return ss


@pytest.fixture
def data_1():
    df = datafile.Datafile(None, None, None)
    df.header = ["ppt", "happy1", "sad1", "happy2", "sad2", "gender1"]
    df.append_data(["a", "5", "2", "2", "4", "1"])
    df.append_data(["b", "2", "3", "4", "1", "3"])
    return df


@pytest.fixture
def data_with_bad():
    df = datafile.Datafile(None, None, None)
    df.header = ["ppt", "happy1", "sad1", "happy2", "sad2"]
    df.append_data(["a", "bad", "2", "bad", "4"])
    return df


@pytest.fixture
def bad_scored(data_with_bad, transforms, scores_1):
    return scorer.Scorer.score(data_with_bad, transforms, scores_1)


@pytest.fixture
def measures_1():
    ms = scoresheet.AggregatorSection()
    ms.append_from_strings(["happy", "mean(happy)"])
    return ms


@pytest.fixture
def measures_2():
    ms = scoresheet.AggregatorSection()
    ms.append_from_strings(["affect", "sum(happy, sad)"])
    return ms


@pytest.fixture
def measures_with_ratio():
    ms = scoresheet.AggregatorSection()
    ms.append_from_strings(["sum_happy", "sum(happy)"])
    ms.append_from_strings(["sum_sad", "sum(sad)"])
    ms.append_from_strings(["ratio_happy", "ratio(sum_happy, sum_sad)"])
    return ms


@pytest.fixture
def measures_with_minmax():
    ms = scoresheet.AggregatorSection()
    ms.append_from_strings(["min_emo", "min(happy, sad)"])
    ms.append_from_strings(["max_happy", "max(happy)"])
    return ms


@pytest.fixture
def measures_bad():
    ms = scoresheet.AggregatorSection()
    ms.append_from_strings(["happy", "sum(badness)"])
    return ms


@pytest.fixture
def scored_data_1(data_1, transforms, scores_1):
    return scorer.Scorer.score(data_1, transforms, scores_1)


@pytest.fixture
def scored_data_2(data_1, transforms, scores_2):
    return scorer.Scorer.score(data_1, transforms, scores_2)


def test_scorer_scores(data_1, transforms, scores_1):
    res = scorer.Scorer.score(data_1, transforms, scores_1)
    assert res.header == ["happy1: happy", "happy2: happy: reverse"]
    d = res.data[0]
    assert d["happy1: happy"] == "5"
    assert d["happy2: happy: reverse"] == 4


def test_scorer_renames(data_1, transforms, scores_3):
    res = scorer.Scorer.score(data_1, transforms, scores_3)
    assert res.header == ["KINDA HAPPY", "VERY HAPPY"]
    d = res.data[0]
    assert d["KINDA HAPPY"] == "5"
    assert d["VERY HAPPY"] == 4


def test_scorer_assigns_nan_on_bad_score(data_with_bad, transforms, scores_1):
    res = scorer.Scorer.score(data_with_bad, transforms, scores_1)
    d = res.data[0]
    assert math.isnan(d["happy2: happy: reverse"])


def test_scorer_measures(scored_data_1, measures_1):
    assert scored_data_1.header == ["happy1: happy", "happy2: happy: reverse"]
    scorer.Scorer.add_measures(scored_data_1, measures_1)
    assert scored_data_1.header == ["happy1: happy", "happy2: happy: reverse", "happy"]
    assert scored_data_1.data[0]["happy"] == 4.5


def test_scorer_does_ratio(scored_data_2, measures_with_ratio):
    scorer.Scorer.add_measures(scored_data_2, measures_with_ratio)
    assert scored_data_2.data[0]["ratio_happy"] == 9.0 / 4.0


def test_scorer_minmax(scored_data_2, measures_with_minmax):
    scorer.Scorer.add_measures(scored_data_2, measures_with_minmax)
    assert scored_data_2.data[0]["min_emo"] == 2
    assert scored_data_2.data[0]["max_happy"] == 5
    assert scored_data_2.data[1]["min_emo"] == 2
    assert scored_data_2.data[1]["max_happy"] == 2


def test_measures_fail_with_bad_name(scored_data_1, measures_bad):
    with pytest.raises(scorer.AggregationError):
        scorer.Scorer.add_measures(scored_data_1, measures_bad)


def test_scorer_assigns_nan_on_bad_measure(bad_scored, measures_1):
    scorer.Scorer.add_measures(bad_scored, measures_1)
    assert math.isnan(bad_scored.data[0]["happy"])


def test_scorer_does_discrete_mappings(data_1, transforms, gender_score):
    res = scorer.Scorer.score(data_1, transforms, gender_score)

    assert res.data[0]["gender1: gender: gmap"] == "f"
    assert res.data[1]["gender1: gender: gmap"] == ""


def test_measures_multi_names(scored_data_2, measures_2):
    scorer.Scorer.add_measures(scored_data_2, measures_2)
    d = scored_data_2.data[0]
    assert d["affect"] == 5 + 4 + 2 + 2
