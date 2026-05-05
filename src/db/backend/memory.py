import json, os, csv


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

    def get_len_header(self, name_table):
        return self.tables[name_table].get_len_header()

class FileDataBase(Database):
    def __init__(self, path, json=False, csv=False):
        self.json = json
        self.csv = csv
        self.path = path
        if json == csv:
            raise TypeError('FileDataBase must be json or csv')

        super().__init__()

    def save_db(self):
        if self.json:
            self._save_db_json()
        else:
            self._save_db_csv()

    def open_db(self):
        if self.json:
            self._open_db_json()
        else:
            self._open_db_csv()

    def _save_db_json(self):
        data = {'tables': []}
        for table_name, table in self.tables.items():
            data['tables'].append({'table_name': table_name, 'table': table.serialize()})

        with open(self.path, 'w') as f:
            json.dump(data, f)

    def _open_db_json(self):
        with open(self.path, 'r') as f:
            data = json.load(f)
            for table_data in data['tables']:
                table = Table([])
                table.table = table_data['table']
                self.tables[table_data['table_name']] = table

    def _save_db_csv(self):
        for table_name, table in self.tables.items():
            save_data = []
            table_data = table.serialize()
            save_data.append(list(table_data.keys()))
            save_data.extend(table.select())
            with open(os.path.join(self.path, f'{table_name}.csv'), 'w') as f:
                csv.writer(f).writerows(save_data)

    def _open_db_csv(self):
        files = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f)) and f.endswith('.csv')]
        for path in files:
            with open(os.path.join(self.path, path), 'r') as f:
                data = csv.reader(f)
                header = next(data)
                table = Table(header)
                for i in data:
                    table.insert({col: value for col, value in zip(header, i)})

                self.tables[next(iter(path.split('.csv')))] = table

    def create_table(self, *arg, **kwargs):
        super().create_table(*arg, **kwargs)
        self.save_db()

    def insert(self, *arg, **kwargs):
        super().insert(*arg, **kwargs)
        self.save_db()

    def delete(self, *arg, **kwargs):
        super().delete(*arg, **kwargs)
        self.save_db()

    def update(self, *arg, **kwargs):
        super().update(*arg, **kwargs)
        self.save_db()


class Table:
    def __init__(self, table_header):
        self.table = {}

        for i in table_header:
            self.table[i] = []

    def select(self, filter_cols=None):
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

    def insert(self, cols):
        if set(cols.keys()) == set(self.table.keys()):
            for col, value in cols.items():
                self.table[col].append(value)

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
