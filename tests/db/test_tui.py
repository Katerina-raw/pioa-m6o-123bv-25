from unittest.mock import patch
from src.db.tui import TUI
from src.db.backend.memory import Database

def test_init():
    tui = TUI()
    assert type(tui.db) == Database
    assert 'students' in tui.db.tables

def test_print_menu(capsys):
    tui = TUI()
    tui._print_menu()
    captured = capsys.readouterr()
    assert '=== База данных ===' in captured.out

def test_print_table_menu(capsys):
    tui = TUI()
    tui._print_table_menu('test')
    captured = capsys.readouterr()
    assert '--- Таблица test ---' in captured.out

def test_read_str(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda x: 'hello')
    tui = TUI()
    result = tui._read_str('')
    assert result == 'hello'

def test_show_tables_empty(capsys):
    tui = TUI()
    tui.db.tables = {}
    result = tui._show_tables()
    captured = capsys.readouterr()
    assert result == False
    assert 'Нет таблиц' in captured.out

def test_show_tables_with_data(capsys):
    tui = TUI()
    tui.db.tables = {'users': None}
    result = tui._show_tables()
    captured = capsys.readouterr()
    assert result == True
    assert '- users' in captured.out

def test_get_columns():
    tui = TUI()
    tui.db.create_table({'id': 'id', 'name': 'name'}, 'test')
    cols = tui._get_columns('test')
    assert 'id' in cols
    assert 'name' in cols

def test_show_records_empty(capsys):
    tui = TUI()
    tui._show_records([])
    captured = capsys.readouterr()
    assert 'Нет записей' in captured.out

def test_show_records_with_data(capsys):
    tui = TUI()
    tui._show_records([['1', 'Ivan']])
    captured = capsys.readouterr()
    assert "1. ['1', 'Ivan']" in captured.out

def test_input_record(monkeypatch):
    inputs = ['Ivan', '25']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    tui = TUI()
    result = tui._input_record(['name', 'age'])
    assert result == {'name': 'Ivan', 'age': '25'}

def test_input_filter(monkeypatch):
    inputs = ['Ivan', '']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    tui = TUI()
    result = tui._input_filter(['name', 'age'])
    assert result == {'name': 'Ivan'}

def test_create_table_success(monkeypatch, capsys):
    inputs = ['mytable', 'col1', 'col2', '']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    tui = TUI()
    tui._create_table()
    captured = capsys.readouterr()
    assert 'mytable' in tui.db.tables
    assert 'создана' in captured.out

def test_create_table_exists(monkeypatch, capsys):
    tui = TUI()
    tui.db.create_table({'id': 'id'}, 'old')
    inputs = ['old', 'col1', '']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    tui._create_table()
    captured = capsys.readouterr()
    assert 'уже есть' in captured.out

def test_work_with_table_not_found(monkeypatch, capsys):
    tui = TUI()
    tui.db.create_table({'id': 'id'}, 'real')
    inputs = ['wrong']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    with patch.object(tui, '_show_tables') as mock:
        mock.return_value = True
        tui._work_with_table()
        captured = capsys.readouterr()
        assert 'не найдена' in captured.out

def test_work_with_table_show_all(monkeypatch):
    tui = TUI()
    tui.db.create_table({'id': 'id'}, 'test')
    inputs = ['test', '1', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    with patch.object(tui, '_show_records') as mock:
        tui._work_with_table()
        mock.assert_called()

def test_work_with_table_insert(monkeypatch):
    tui = TUI()
    tui.db.create_table({'id': 'id'}, 'test')
    inputs = ['test', '2', '1', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    with patch.object(tui.db, 'insert') as mock:
        tui._work_with_table()
        mock.assert_called()

def test_work_with_table_find(monkeypatch):
    tui = TUI()
    tui.db.create_table({'id': 'id'}, 'test')
    inputs = ['test', '3', '1', '', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    with patch.object(tui.db, 'select') as mock:
        tui._work_with_table()
        mock.assert_called()

def test_work_with_table_delete(monkeypatch):
    tui = TUI()
    tui.db.create_table({'id': 'id'}, 'test')
    inputs = ['test', '5', '1', '', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    with patch.object(tui.db, 'delete') as mock:
        tui._work_with_table()
        mock.assert_called()

def test_loop_create(monkeypatch):
    inputs = ['1', '', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    tui = TUI()
    with patch.object(tui, '_create_table') as mock:
        tui.loop()
        mock.assert_called()

def test_loop_show(monkeypatch):
    inputs = ['2', '', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    tui = TUI()
    with patch.object(tui, '_show_tables') as mock:
        tui.loop()
        mock.assert_called()

def test_loop_work(monkeypatch):
    inputs = ['3', '', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    tui = TUI()
    with patch.object(tui, '_work_with_table') as mock:
        tui.loop()
        mock.assert_called()

def test_loop_bad_command(monkeypatch, capsys):
    inputs = ['99', '', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    tui = TUI()
    tui.loop()
    captured = capsys.readouterr()
    assert 'Неверная команда' in captured.out

def test_work_with_table_no_tables(monkeypatch, capsys):
    tui = TUI()
    tui.db.tables = {}
    tui._work_with_table()
    captured = capsys.readouterr()
    assert "Нет таблиц" in captured.out

def test_work_with_table_find_no_filter(monkeypatch):
    tui = TUI()
    tui.db.create_table({'id': 'id'}, 'test')
    inputs = ['test', '3', '', '', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    with patch.object(tui.db, 'select') as mock:
        tui._work_with_table()
        mock.assert_called()
        args = mock.call_args[0]
        assert len(args) == 1

def test_work_with_table_update_no_data(monkeypatch, capsys):
    tui = TUI()
    tui.db.create_table({'id': 'id'}, 'test')
    inputs = ['test', '4', '1', '', '', '', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    tui._work_with_table()
    captured = capsys.readouterr()
    assert 'Обновлено' not in captured.out

def test_work_with_table_delete_no_confirm(monkeypatch, capsys):
    tui = TUI()
    tui.db.create_table({'id': 'id'}, 'test')
    tui.db.insert('test', {'id': '1'})
    inputs = ['test', '5', '', '', 'n', '0']
    monkeypatch.setattr('builtins.input', lambda x: inputs.pop(0))
    tui._work_with_table()
    captured = capsys.readouterr()
    assert 'Удалено' not in captured.out
    records = tui.db.select('test')
    assert len(records) == 1
