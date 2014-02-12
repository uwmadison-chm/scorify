# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

import pytest

from scorify import datafile, scoresheet, scorer


@pytest.fixture
def transforms():
    ts = scoresheet.TransformSection()
    ts.append_from_strings(['-', 'map(1:5,5:1)'])
    return ts


@pytest.fixture
def scores_1():
    ss = scoresheet.ScoreSection()
    ss.append_from_strings(['happy1', 'happy'])
    ss.append_from_strings(['happy2', 'happy', '-'])
    return ss

@pytest.fixture
def data_1():
    df = datafile.Datafile(None, None)
    df.header = ['ppt', 'happy1', 'sad1', 'happy2', 'sad2']
    df.append_data(['a', '5', '2', '2', '4'])
    df.append_data(['b', '2', '3', '4', '1'])
    return df


def test_scorer_scores(data_1, transforms, scores_1):
    res = scorer.Scorer.score(data_1, transforms, scores_1)
    assert res.header == ['happy1: happy', 'happy2: happy']
    d = res.data[0]
    assert d['happy1: happy'] == '5'
    assert d['happy2: happy'] == 4