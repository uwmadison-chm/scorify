# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

from collections import namedtuple

import directives

class Scoresheet(object):
    def __init__(self):
        self.errors = []
        self.layout_section = LayoutSection()
        self.exclude_section = ExcludeSection()
        self.transform_section = TransformSection()
        self.score_section = ScoreSection()
        self.measure_section = MeasureSection()

    def add_error(self, line_number, message):
        self.errors.append(ScoresheetMessage(line_number, message))


ScoresheetMessage = namedtuple('ScoresheetMessage', ['line', 'message'])


class Reader(object):
    def __init__(self, data=None):
        """
        data should be a csv.Reader-like object. Notably, it should be
        iterable, return a list per iteration, and support line_number.
        """
        self.data = data

    def read_into_scoresheet(self, sheet=None):
        if sheet == None:
            sheet = Scoresheet()
        section_map = {
            'layout': sheet.layout_section,
            'exclude' : sheet.exclude_section,
            'transform': sheet.transform_section,
            'score': sheet.score_section,
            'measure': sheet.measure_section
        }
        layout_lines = []
        exclusion_lines = []

        for line in self.data:
            ignore_line = (len(line) < 2) or (line[0] == "#")
            if ignore_line:
                continue
            stripped_parts = [str(p).strip() for p in line]
            line_type = stripped_parts[0]
            line_params = stripped_parts[1:]
            try:
                sect = section_map[line_type]
                sect.append_from_strings(line_params)
            except KeyError:
                sheet.add_error(
                    self.data.line_num,
                    "I don't understand {0}".format(line_type))
            except (
                SectionError,
                directives.DirectiveError,
                mappings.MappingError) as exc:
                sheet.add_error(self.data.line_num, exc.message)
        return sheet


class SectionError(ValueError):
    pass


class Section(object):
    def __init__(self, directives=None):
        if directives is None:
            directives = []
        super(Section, self).__init__()
        self.directives = directives
        self.errors = []

    def append_from_strings(self, string_list):
        raise NotImplementedError()

    def append_directive(self, directive):
        self.directives.append(directive)

    def __len__(self):
        return len(self.directives)


class LayoutSection(Section):
    def __init__(self, directives=None):
        super(LayoutSection, self).__init__(directives)

    def is_valid(self):
        self.errors = []
        headers = [d for d in self.directives if d.info == 'header']
        if len(headers) > 1:
            self.errors.append('you can only have one header in your layout')
        if len(headers) < 1:
            self.errors.append('you must have one header in your layout')

        datas = [d for d in self.directives if d.info == 'data']
        if len(datas) > 1:
            self.errors.append('you can only have one data in your layout')
        if len(datas) < 1:
            self.errors.append('you must have one data in your layout')

        last_entry = self.directives[-1]
        if not last_entry.info == 'data':
            self.errors.append("data needs to come last in your layout")

        return len(self.errors) == 0

    def append_from_strings(self, string_list):
        """
        string_list will have the "layout" stripped off already; it should
        be one of ["header", "data", "skip"] but we'll let directives.Layout
        figure that out.
        """
        if len(string_list) < 1:
            raise directives.DirectiveError(
                "layout must be 'header', 'data', or 'skip'")
        self.append_directive(directives.Layout(string_list[0]))


class ExcludeSection(Section):
    def __init__(self, directives=None):
        super(ExcludeSection, self).__init__(directives)

    def append_from_strings(self, string_list):
        if len(string_list) < 1:
            raise directives.DirectiveError(
                "exclude must have a column name")
        exclude_col = string_list[0]
        exclude_val = ''
        if len(string_list) > 1:
            exclude_val = string_list[1]
        self.append_directive(directives.Exclude(exclude_col, exclude_val))


class TransformSection(Section):
    def __init__(self, directives=None):
        super(TransformSection, self).__init__(directives)

    def append_from_strings(self, string_list):
        if len(string_list) < 2:
            raise directives.DirectiveError(
                "transform must have a name and transformation")
        name, xform = string_list[0], string_list[1]
        self.directives.append(directives.Transform(name, xform))

    def append_directive(self, directive):
        name = directive.name
        dupes = [d for d in self.directives if d.name == name]
        if len(dupes) > 0:
            raise SectionError(
                "there's already a transform called {0}".format(name))
        super(TransformSection, self).append_directive(directive)

class ScoreSection(Section):
    def __init__(self, directives=None):
        super(ScoreSection, self).__init__(directives)

    def append_from_strings(self, string_list):
        if len(string_list) < 1:
            raise directives.DirectiveError(
                "score must have a column name")
        col_name = string_list[0]
        measure_name = ''
        transform = ''
        if len(string_list) > 1:
            measure_name = string_list[1]
        if len(string_list) > 2:
            transform = string_list[2]

        self.append_directive(
            directives.Score(col_name, measure_name, transform))

    def append_directive(self, directive):
        column = directive.column
        measure_name = directive.measure_name
        dupes = [d for d in self.directives if
            d.column == column and d.measure_name == measure_name]
        if len(dupes) > 0:
            raise SectionError("{0} is already part of {1}".format(
                column, measure_name))
        super(ScoreSection, self).append_directive(directive)


class MeasureSection(Section):
    def __init__(self, directives=None):
        super(MeasureSection, self).__init__(directives)

    def append_from_strings(self, string_list):
        if len(string_list) < 2:
            raise directives.DirectiveError(
                "measures must have a name and aggregator function")
        name = string_list[0]
        agg_fx = string_list[1]
        d = directives.Measure(name, agg_fx)
        super(MeasureSection, self).append_directive(d)

    def append_directive(self, directive):
        name = directive.name
        dupes = [d for d in self.directives if d.name == name]
        if len(dupes) > 0:
            raise SectionError("{0} is already a measure name".format(name))
        super(MeasureSection, self).append_directive(directive)