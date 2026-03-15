from src.db.backend.memory import Database


def test_create_table():
    db = Database()
    db.create_table(table_name='users', table_header={'id': 'id', 'name': 'name', 'sex': 'sex'})
    assert list(iter(db.tables['users'].table.keys())) == ['id', 'name', 'sex']


def test_empty_select():
    db = Database()
    db.create_table(table_name='users', table_header={'id': 'id', 'name': 'name', 'sex': 'sex'})
    response = db.select('users')
    assert response == []


def test_insert():
    db = Database()
    db.create_table(table_name='users', table_header={'id': 'id', 'name': 'name', 'sex': 'sex'})
    db.insert('users', {'id': 1, 'name': 'ivan', 'sex': 'male'})
    response = db.select('users')
    assert response == [[1, 'ivan', 'male']]


def test_select_one():
    db = Database()
    db.create_table(table_name='users', table_header={'id': 'id', 'name': 'name', 'sex': 'sex'})
    db.insert('users', {'id': 1, 'name': 'ivan', 'sex': 'male'})
    db.insert('users', {'id': 2, 'name': 'kate', 'sex': 'fem'})
    response = db.select('users', filter_cols={'id': 1})
    assert response == [[1, 'ivan', 'male']]


def test_select_all():
    db = Database()
    db.create_table(table_name='users', table_header={'id': 'id', 'name': 'name', 'sex': 'sex'})
    db.insert('users', {'id': 1, 'name': 'ivan', 'sex': 'male'})
    db.insert('users', {'id': 2, 'name': 'kate', 'sex': 'fem'})
    response = db.select('users')
    assert response == [[1, 'ivan', 'male'], [2, 'kate', 'fem']]


def test_update():
    db = Database()
    db.create_table(table_name='users', table_header={'id': 'id', 'name': 'name', 'sex': 'sex'})
    db.insert('users', {'id': 1, 'name': 'ivan', 'sex': 'male'})
    db.insert('users', {'id': 2, 'name': 'kate', 'sex': 'fem'})
    db.update('users', filters={'id': 1}, cols={'name': 'alex'})
    response = db.select('users', filter_cols={'id': 1})
    assert response == [[1, 'alex', 'male']]


def test_delete():
    db = Database()
    db.create_table(table_name='users', table_header={'id': 'id', 'name': 'name', 'sex': 'sex'})
    db.insert('users', {'id': 1, 'name': 'ivan', 'sex': 'male'})
    db.insert('users', {'id': 2, 'name': 'kate', 'sex': 'fem'})
    db.delete('users', {'id': 1})
    response = db.select('users')
    assert response == [[2, 'kate', 'fem']]


def test_update_many():
    db = Database()
    db.create_table(table_name='users', table_header={'id': 'id', 'name': 'name', 'sex': 'sex'})
    db.insert('users', {'id': 1, 'name': 'ivan', 'sex': 'male'})
    db.insert('users', {'id': 2, 'name': 'kate', 'sex': 'fem'})
    db.update('users', filters={'id': 1, 'sex': 'fem'}, cols={'name': 'alex'})
    response = db.select('users')
    assert response == [[1, 'alex', 'male'], [2, 'alex', 'fem']]
