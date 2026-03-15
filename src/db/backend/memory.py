class Database:
    def __init__(self):
        self.tables = {}

    def create_table(self, table_header, table_name):
        self.tables[table_name] = Table(table_header)

    def select(self, name_table, filter_cols=None):
        return self.tables[name_table].select(filter_cols)

    def insert(self, name_table, cols):
        self.tables[name_table].insert(cols)

    def delete(self, name_table, filter_cols):
        self.tables[name_table].delete(filter_cols)

    def update(self, name_table, filters, cols):
        self.tables[name_table].update(filters, cols)



class Table:
    def __init__(self, table_header):
        self.table = {}

        for i in table_header:
            self.table[table_header[i]] = []

    def select(self, filter_cols=None):
        result = []
        if filter_cols is None:
            for i in range(len(self.table[next(iter(self.table.keys()))])):
                result.append(self._get_row(i))
            return result

        for col, value in filter_cols.items():
            now_col = self.table[col]
            for i in range(len(now_col)):
                if now_col[i] == value:
                    result.append(self._get_row(i))

        return result

    def insert(self, cols):
        if set(cols.keys()) == set(self.table.keys()):
            for col, value in cols.items():
                self.table[col].append(value)

    def delete(self, filter_cols):
        indexes = set()

        for col, value in filter_cols.items():
            now_col = self.table[col]
            for i in range(len(now_col)):
                if now_col[i] == value:
                    indexes.add(i)

        for index in indexes:
            for col in self.table.keys():
                self.table[col].pop(index)

    def update(self, filters, cols_data):
        indexes = set()

        for col, value in filters.items():
            now_col = self.table[col]
            for i in range(len(now_col)):
                if now_col[i] == value:
                    indexes.add(i)

        for index in indexes:
            for col, value in cols_data.items():
                self.table[col][index] = value

    def _get_row(self, index):
        res = []
        for i in self.table.keys():
            res.append(self.table[i][index])

        return res