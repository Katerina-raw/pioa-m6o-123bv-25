import json
import os
import csv


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


class JSONDataBase(Database):
    def __init__(self, path):
        self.path = path
        super().__init__()

    def save_db(self):
        self._save_db_json()

    def open_db(self):
        self._open_db_json()

    def _save_db_json(self):
        data = {'tables': []}
        for table_name, table in self._tables.items():
            data['tables'].append({'table_name': table_name, 'table': table.serialize()})

        with open(self.path, 'w', encoding="utf-8") as f:
            json.dump(data, f)

    def _open_db_json(self):
        with open(self.path, 'r', encoding="utf-8") as f:
            try:
                data = json.load(f)
                for table_data in data['tables']:
                    table = Table([])
                    table.table = table_data['table']
                    self._tables[table_data['table_name']] = table
            except Exception:
                raise EOFError('File damaged or not exist')

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


class CSVDataBase(Database):
    def __init__(self, path):
        self.path = path

        super().__init__()

    def save_db(self):
        self._save_db_csv()

    def open_db(self):
        self._open_db_csv()

    def _save_db_csv(self):
        for table_name, table in self._tables.items():
            save_data = []
            table_data = table.serialize()
            save_data.append(list(table_data.keys()))
            save_data.extend(table.select())
            with open(os.path.join(self.path, f'{table_name}.csv'), 'w') as f:
                csv.writer(f).writerows(save_data)

    def _open_db_csv(self):
        try:
            files = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f)) and f.endswith('.csv')]
            for path in files:
                with open(os.path.join(self.path, path), 'r') as f:
                    data = csv.reader(f)
                    header = next(data)
                    table = Table(header)
                    for i in data:
                        if i:
                            table.insert({col: value for col, value in zip(header, i)})

                    self._tables[next(iter(path.split('.csv')))] = table
        except Exception:
            raise EOFError('Error while opening files')

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

    def select_sorted(self, filter_cols=None, sort_field=None, ascending=True):
        rows = self.select(filter_cols)

        if sort_field is None or not rows:
            return rows

        if sort_field not in self.table:
            raise KeyError("Field '{}' does not exist".format(sort_field))

        col_index = list(self.table.keys()).index(sort_field)
        if all(map(lambda m: m[col_index].isdigit(), rows)):
            rows.sort(key=lambda row: int(row[col_index]), reverse=not ascending)
        else:
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