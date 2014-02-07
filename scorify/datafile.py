# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

"""
Reads data files (or CSV objects) into datafile objects.

Datafiles are iterable and indexable by column name. When reading, you pass
in a scoresheet.LayoutSection, which tells you where data and header sections
are.
"""


class Datafile(object):
    def __init__(self, lines, layout_section):
        self.lines = lines
        self.layout_section = layout_section
        self.header = None
        self.data = None
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
                self.header = [h.strip() for h in line]
            else:
                # Force lines of funny length to be the header's length
                len_diff = len(self.header) - len(line)
                padding = [''] * len_diff
                full_line = line + padding
                self.data.append(dict(zip(self.header, full_line)))

