import json
import csv
import os
from src.db.backend.memory import Database, Table


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
        try:
            with open(self.path, 'r', encoding="utf-8") as f:
                data = json.load(f)
                for table_data in data['tables']:
                    table = Table([])
                    table.table = table_data['table']
                    self._tables[table_data['table_name']] = table
        except FileNotFoundError:
            raise FileNotFoundError('File doesnt exist')
        except json.decoder.JSONDecodeError:
            raise EOFError('File damaged')
        except KeyError, ValueError, TypeError:
            raise EOFError("File structure isn't valuable")

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
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        for table_name, table in self._tables.items():
            save_data = []
            table_data = table.serialize()
            save_data.append(list(table_data.keys()))
            save_data.extend(table.select())
            with open(os.path.join(self.path, f'{table_name}.csv'), 'w', encoding="utf-8", newline="") as f:
                csv.writer(f).writerows(save_data)

    def _open_db_csv(self):
        try:
            files = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f)) and f.endswith('.csv')]
            for path in files:
                with open(os.path.join(self.path, path), 'r', encoding="utf-8", newline="") as f:
                    data = csv.reader(f)
                    header = next(data)
                    table = Table(header)
                    for i in data:
                        if i:
                            table.insert({col: value for col, value in zip(header, i)})

                    self._tables[next(iter(path.split('.csv')))] = table
        except FileNotFoundError:
            raise FileNotFoundError('File doesnt exist')
        except csv.Error:
            raise EOFError('Error while opening files')
        except KeyError, ValueError, TypeError:
            raise EOFError("File structure isn't valuable")

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