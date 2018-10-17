# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System
from __future__ import absolute_import

from collections import defaultdict
from scorify.errors import HaystackError

NaN = float('nan')


class ScoredData(object):
    def __init__(self, header=None, data=None, measure_columns=None):
        self.header = header or []
        self.data = data or []
        self.measure_columns = measure_columns or defaultdict(list)

    def columns_for(self, measure_list):
        out = []
        for name in measure_list:
            if name in self.measure_columns:
                out.extend(self.measure_columns[name])
            elif name in self.header:
                out.append(name)
            else:
                raise KeyError(name)
        return out

    def known_measures(self):
        return [m for m in self.measure_columns.keys() if len(m.strip()) > 0]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)


class Scorer(object):
    @classmethod
    def score_name(kls, directive):
        name = directive.column
        if len(directive.measure_name) > 0:
            name += ': ' + directive.measure_name
        return name

    @classmethod
    def make_measure_columns(kls, score_section):
        mc = defaultdict(list)
        for d in score_section.directives:
            mc[d.measure_name].append(kls.score_name(d))
        return mc

    @classmethod
    def score(kls, datafile, transform_section, score_section):
        out = ScoredData()
        out.header = [kls.score_name(d) for d in score_section.directives]
        out.measure_columns = kls.make_measure_columns(score_section)

        for r in datafile.data:
            scored = {}
            for s in score_section.directives:
                try:
                    tx = transform_section[s.transform]
                except KeyError as exc:
                    raise TransformError(
                        "transforms", exc.message,
                        transform_section.known_transforms())

                name = kls.score_name(s)
                try:
                    sval = tx.transform(r[s.column])
                except KeyError as err:
                    raise ScoringError(
                        "data columns", str(err),
                        datafile.header)
                except ValueError:
                    sval = NaN
                scored[name] = sval
            out.data.append(scored)

        return out

    @classmethod
    def add_measures(kls, scored_data, measure_section):
        for m in measure_section.directives:
            scored_data.header.append(m.name)
        for row in scored_data.data:
            for m in measure_section.directives:
                try:
                    cols = scored_data.columns_for(m.to_use)
                except KeyError as exc:
                    raise AggregationError(
                        "measures", str(exc), scored_data.known_measures())
                vals = [row[col] for col in cols]
                try:
                    row[m.name] = m.agg_fx(vals)
                except ValueError:
                    row[m.name] = NaN


class TransformError(HaystackError):
    pass


class ScoringError(HaystackError):
    pass


class AggregationError(HaystackError):
    pass
