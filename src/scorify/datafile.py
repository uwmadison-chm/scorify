# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

"""
Reads data files (or CSV objects) into datafile objects.

Datafiles are iterable and indexable by column name. When reading, you pass
in a scoresheet.LayoutSection, which tells you where data and header sections
are.
"""
from __future__ import absolute_import

from scorify.errors import HaystackError


class Datafile(object):
    def __init__(self, lines, layout_section, rename_section):
        self.lines = lines
        self.layout_section = layout_section
        self.rename_section = rename_section
        self.header = []
        self.data = []
        super(Datafile, self).__init__()

    def read(self):
        self.header = []
        self.data = []
        for line_num, line in enumerate(self.lines):
            # Since we assume layout_section is valid, we only care about
            # header and skip lines -- everything else must be data.
            line_type = ''
            if line_num < len(self.layout_section.directives):
                line_type = self.layout_section.directives[line_num].info
            if line_type == 'skip':
                continue
            if line_type == 'header':
                self.header = [
                    self.rename_section.map_name(h.strip()) for h in line]
            else:
                self.append_data(line)

    def append_data(self, data):
        # Force lines of funny length to be the header's length
        len_diff = len(self.header) - len(data)
        padding = [''] * len_diff
        full_line = data + padding
        self.data.append(dict(zip(self.header, full_line)))

    def apply_exclusions(self, exclusion_section):
        new_data = []
        for row in self.data:
            try:
                exclude = any([e.excludes(row) for e in exclusion_section])
            except KeyError as exc:
                raise ExclusionError(
                    "data columns", str(exc), self.data.header)
            if not exclude:
                new_data.append(row)
        self.data = new_data

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, item):
        return self.data[item]


class ExclusionError(HaystackError):
    pass
