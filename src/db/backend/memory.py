class Database:
    def __init__(self):
        self._tables = {}

    def create_table(self, table_header, table_name):
        if table_name in self._tables:
            raise KeyError("Table {} already exists".format(table_name))
        self._tables[table_name] = Table(table_header)

    def select(self, name_table, filter_cols=None):
        if name_table in self._tables:
            return self._tables[name_table].select(filter_cols)
        else:
            raise KeyError("Table {} does not exist".format(name_table))

    def select_sorted(self, name_table, filter_cols=None, sort_field=None, ascending=True):
        if name_table in self._tables:
            return self._tables[name_table].select_sorted(filter_cols, sort_field, ascending)
        else:
            raise KeyError("Table {} does not exist".format(name_table))

    def insert(self, name_table, cols):
        if name_table in self._tables:
            self._tables[name_table].insert(cols)

        else:
            raise KeyError("Table {} does not exist".format(name_table))

    def delete(self, name_table, filter_cols):
        if name_table in self._tables:
            self._tables[name_table].delete(filter_cols)
        else:
            raise KeyError("Table {} does not exist".format(name_table))

    def update(self, name_table, filters, cols):
        if name_table in self._tables:
            self._tables[name_table].update(filters, cols)
        else:
            raise KeyError("Table {} does not exist".format(name_table))

    def get_len_header(self, name_table):
        if name_table in self._tables:
            return self._tables[name_table].get_len_header()
        else:
            raise KeyError("Table {} does not exist".format(name_table))

    def get_tables_name(self):
        return [i for i in self._tables.keys()]

    def get_cols_name(self, table_name):
        if table_name in self._tables:
            return self._tables[table_name].get_cols_name()
        else:
            raise KeyError("Table {} does not exist".format(table_name))


class Table:
    def __init__(self, table_header):
        self.table = {}

        for i in table_header:
            self.table[i] = []

    def select(self, filter_cols=None):
        if self.table == {}:
            return []

        result = []
        if filter_cols is None:
            for i in range(len(self.table[next(iter(self.table.keys()))])):
                result.append(self._get_row(i))
            return result

        num_rows = len(self.table[next(iter(self.table.keys()))])
        for i in range(num_rows):
            match = True
            for col, value in filter_cols.items():
                if col not in self.table or self.table[col][i] != value:
                    match = False
                    break
            if match:
                result.append(self._get_row(i))

        return result

    def select_sorted(self, filter_cols=None, sort_field=None, ascending=True):
        rows = self.select(filter_cols)

        if sort_field is None or not rows:
            return rows

        if sort_field not in self.table:
            raise KeyError("Field '{}' does not exist".format(sort_field))

        col_index = list(self.table.keys()).index(sort_field)
        try:
            rows.sort(key=lambda row: float(row[col_index]), reverse=not ascending)
        except ValueError:
            rows.sort(key=lambda row: row[col_index], reverse=not ascending)
        return rows

    def insert(self, cols):
        if set(cols.keys()) == set(self.table.keys()):
            for col, value in cols.items():
                self.table[col].append(value)
        else:
            raise KeyError("Not found columns {}".format(set(cols.keys()) ^ set(self.table.keys())))

    def delete(self, filter_cols):
        if not self.table:
            return

        num_rows = len(self.table[next(iter(self.table.keys()))])
        indexes_to_delete = set()

        for i in range(num_rows):
            match = True
            for col, value in filter_cols.items():
                if col not in self.table or self.table[col][i] != value:
                    match = False
                    break
            if match:
                indexes_to_delete.add(i)

        for index in sorted(indexes_to_delete, reverse=True):
            for col in self.table.keys():
                self.table[col].pop(index)

    def update(self, filters, cols_data):
        for col in cols_data.keys():
            if col not in self.table:
                raise KeyError("Field '{}' does not exist".format(col))

        if not self.table:
            return

        num_rows = len(self.table[next(iter(self.table.keys()))])
        indexes_to_update = set()

        for i in range(num_rows):
            match = True
            for col, value in filters.items():
                if col not in self.table or self.table[col][i] != value:
                    match = False
                    break
            if match:
                indexes_to_update.add(i)

        for index in indexes_to_update:
            for col, value in cols_data.items():
                if col in self.table:
                    self.table[col][index] = value

    def _get_row(self, index):
        res = []
        for i in self.table.keys():
            res.append(self.table[i][index])

        return res

    def serialize(self) -> dict:
        return self.table

    def get_len_header(self):
        return len(self.table)

    def get_cols_name(self):
        return [i for i in self.table.keys()]