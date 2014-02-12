# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System


class ScoredValue(object):
    def __init__(self):
        pass


class ScoredData(object):
    def __init__(self, header=None, data=None):
        self.header = header or []
        self.data = data or []


def score_name(directive):
    name = directive.column
    if len(directive.measure_name) > 0:
        name += ': ' + directive.measure_name
    return name


class Scorer(object):
    @classmethod

    def score(kls, datafile, transform_section, score_section):
        out = ScoredData()
        out.header = [score_name(d) for d in score_section.directives]
        for r in datafile.data:
            scored = {}
            for s in score_section.directives:
                tx = transform_section[s.transform]
                name = score_name(s)
                sval = tx.transform(r[s.column])
                scored[name] = sval
            out.data.append(scored)

        return out