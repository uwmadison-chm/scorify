class ExcelReader():
    """
    We need to mimic csv.Reader's line_num property on row_values

    NOTE: This is not working correctly yet
    """
    def __init__(self, sheet):
        self.sheet = sheet
        self.line_num = -1
        self.iterator = sheet.iter_rows(values_only=True)


    def __iter__(self):
        return self

    def __next__(self):
        self.line_num += 1
        if self.line_num >= self.sheet.max_row:
            raise StopIteration()

        def xstr(s):
            if s is None:
                return ''
            return str(s)

        # list, because openpyxl seems to build a tuple
        return list(map(xstr, next(self.iterator)))

