class ExcelReader():
    """
    We need to mimic csv.Reader's line_num property on row_values

    NOTE: This is not working correctly yet
    """
    def __init__(self, sheet):
        self.sheet = sheet
        self.line_num = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.line_num += 1
        if self.line_num >= self.sheet.nrows:
            raise StopIteration()
        return self.sheet.row_values(self.line_num)

