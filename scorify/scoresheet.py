# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System


class Scoresheet(object):
    def __init__(self):
        self.errors = []
        self.layout_section = None
        self.exclusion_section = None
        self.transform_section = None
        self.score_section = None
        self.measure_section = None


class Reader(object):
    def __init__(self, data=None):
        self.data = data

    def read_into_scoresheet(self):
        return Scoresheet()


class LayoutSection(object):
    def __init__(self, layout_directives=[]):
        self.layout_directives = layout_directives
        self.errors = []

    def is_valid(self):
        self.errors = []
        headers = [d for d in self.layout_directives if d.info == 'header']
        if len(headers) > 1:
            self.errors.append('you can only have one header in your layout')
        if len(headers) < 1:
            self.errors.append('you must have one header in your layout')

        datas = [d for d in self.layout_directives if d.info == 'data']
        if len(datas) > 1:
            self.errors.append('you can only have one data in your layout')
        if len(datas) < 1:
            self.errors.append('you must have one data in your layout')

        last_entry = self.layout_directives[-1]
        if not last_entry.info == 'data':
            self.errors.append("data needs to come last in your layout")

        return len(self.errors) == 0