class SpreadSheetUtils:
    def __init__(self, sheet):
        self.sheet = sheet


    def get_col_index(self, column_name):
        header = self.sheet.row_values(1)
        return header.index(column_name) + 1

    def find_row_by_col_value(self, column_name, value_to_find):
        all_rows = self.sheet.get_all_records()
        for idx, row in enumerate(all_rows):
            if row.get(column_name) == value_to_find:
                return idx + 2  # +2 accounts for header row (1) + 0-based index
        return None
