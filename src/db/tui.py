from src.db.backend.memory import Database


class TUI:
    def __init__(self):
        self.db = Database()
        self.db.create_table({"id": "id", "name": "name", "age": "age"}, "students")

    def _print_menu(self):
        print("\n=== База данных ===")
        print("1. Создать таблицу")
        print("2. Все таблицы")
        print("3. Работа с таблицей")
        print("0. Выход")

    def _print_table_menu(self, table_name):
        print(f"\n--- Таблица {table_name} ---")
        print("1. Все записи")
        print("2. Добавить")
        print("3. Найти")
        print("4. Обновить")
        print("5. Удалить")
        print("0. Назад")

    def _read_str(self, prompt, required=False):
        val = input(prompt).strip()
        return val if val or not required else None

    def _show_tables(self):
        if not self.db.get_tables_name():
            print("Нет таблиц")
            return False
        for name in self.db.get_tables_name():
            print(f"- {name}")
        return True

    def _show_records(self, records):
        if not records:
            print("Нет записей")
            return
        for i, r in enumerate(records, 1):
            print(f"{i}. {r}")

    def _input_record(self, columns):
        data = {}
        for col in columns:
            val = self._read_str(f"{col}: ")
            if val:
                data[col] = val
        return data

    def _input_filter(self, columns):
        filt = {}
        for col in columns:
            val = self._read_str(f"{col} (Enter=пропустить): ")
            if val:
                filt[col] = val
        return filt

    def _create_table(self):
        name = self._read_str("Имя таблицы: ", True)

        if name is None:
            print('Ничего не введено')
            return

        if name in self.db.get_tables_name():
            print("Таблица уже есть")
            return

        cols = []
        print("Колонки (пустая строка - конец):")
        while True:
            col = input(f"{len(cols) + 1}: ").strip()
            if not col:
                if len(cols) > 0:
                    break
                print("Нужна хотя бы одна колонка")
                continue
            if col not in cols:
                cols.append(col)

        header = {col: col for col in cols}
        self.db.create_table(header, name)
        print(f"Таблица {name} создана")

    def _work_with_table(self):
        if not self._show_tables():
            return

        name = self._read_str("Имя таблицы: ", True)
        if name not in self.db.get_tables_name():
            print("Таблица не найдена")
            return

        columns = self.db.get_cols_name(name)

        while True:
            self._print_table_menu(name)
            cmd = input("Выберите: ").strip()

            if cmd == "1":
                records = self.db.select(name)
                self._show_records(records)


            elif cmd == "2":
                data = self._input_record(columns)
                self.db.insert(name, data)
                print("Добавлено")

            elif cmd == "3":
                filt = self._input_filter(columns)
                if filt:
                    records = self.db.select(name, filt)
                else:
                    records = self.db.select(name)
                self._show_records(records)

            elif cmd == "4":
                print("Фильтр для обновления:")
                filt = self._input_filter(columns)
                print("Новые данные:")
                data = self._input_record(columns)
                if data:
                    self.db.update(name, filt, data)
                    print("Обновлено")
            elif cmd == "5":
                print("Фильтр для удаления:")
                filt = self._input_filter(columns)
                if filt or input("Удалить все? (y/n): ").lower() == 'y':
                    self.db.delete(name, filt)
                    print("Удалено")

            elif cmd == "0":  # Назад
                break

    def loop(self):
        try:
            while True:
                self._print_menu()
                cmd = input("Выберите: ").strip()

                if cmd == "1":
                    self._create_table()
                elif cmd == "2":
                    self._show_tables()
                elif cmd == "3":
                    self._work_with_table()
                elif cmd == "0":
                    break
                else:
                    print("Неверная команда")

                if cmd != "0":
                    input("Enter...")
        except Exception as e:
            print(e)


def run():
    TUI().loop()


if __name__ == "__main__":
    run()