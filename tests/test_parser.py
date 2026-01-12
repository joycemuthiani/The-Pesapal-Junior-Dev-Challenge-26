"""
Tests for SQL parser
"""

import pytest
from pyreldb.parser import SQLParser, Tokenizer


def test_tokenizer():
    """Test SQL tokenization"""
    query = "SELECT * FROM users WHERE id = 1;"
    tokenizer = Tokenizer(query)
    tokens = tokenizer.tokenize()

    assert tokens[0].value == "SELECT"
    assert tokens[0].type == "KEYWORD"
    assert tokens[2].value == "FROM"


def test_parse_select():
    """Test parsing SELECT query"""
    parser = SQLParser()
    result = parser.parse("SELECT * FROM users;")

    assert result['type'] == 'SELECT'
    assert result['table'] == 'users'
    assert result['columns'] == ['*']


def test_parse_select_with_columns():
    """Test parsing SELECT with specific columns"""
    parser = SQLParser()
    result = parser.parse("SELECT name, email FROM users;")

    assert result['columns'] == ['name', 'email']


def test_parse_select_with_where():
    """Test parsing SELECT with WHERE clause"""
    parser = SQLParser()
    result = parser.parse("SELECT * FROM users WHERE id = 1;")

    assert result['where'] is not None
    assert result['where']['column'] == 'id'
    assert result['where']['operator'] == '='
    assert result['where']['value'] == 1


def test_parse_insert():
    """Test parsing INSERT query"""
    parser = SQLParser()
    result = parser.parse("INSERT INTO users (name, email) VALUES ('John', 'john@example.com');")

    assert result['type'] == 'INSERT'
    assert result['table'] == 'users'
    assert result['columns'] == ['name', 'email']
    assert result['values'] == ['John', 'john@example.com']


def test_parse_update():
    """Test parsing UPDATE query"""
    parser = SQLParser()
    result = parser.parse("UPDATE users SET balance = 100.0 WHERE id = 1;")

    assert result['type'] == 'UPDATE'
    assert result['table'] == 'users'
    assert result['updates']['balance'] == 100.0
    assert result['where'] is not None


def test_parse_delete():
    """Test parsing DELETE query"""
    parser = SQLParser()
    result = parser.parse("DELETE FROM users WHERE id = 1;")

    assert result['type'] == 'DELETE'
    assert result['table'] == 'users'
    assert result['where'] is not None


def test_parse_create_table():
    """Test parsing CREATE TABLE query"""
    parser = SQLParser()
    result = parser.parse("""
        CREATE TABLE users (
            id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE
        );
    """)

    assert result['type'] == 'CREATE_TABLE'
    assert result['table'] == 'users'
    assert len(result['columns']) == 3
    assert result['columns'][0]['name'] == 'id'
    assert result['columns'][0]['primary_key'] is True


def test_parse_join():
    """Test parsing JOIN query"""
    parser = SQLParser()
    result = parser.parse("""
        SELECT users.name, orders.amount
        FROM users
        INNER JOIN orders ON users.id = orders.user_id;
    """)

    assert result['type'] == 'SELECT'
    assert len(result['joins']) == 1
    assert result['joins'][0]['type'] == 'INNER'
    assert result['joins'][0]['table'] == 'orders'


def test_parse_order_by():
    """Test parsing ORDER BY clause"""
    parser = SQLParser()
    result = parser.parse("SELECT * FROM users ORDER BY name DESC;")

    assert result['order_by'] is not None
    assert result['order_by']['column'] == 'name'
    assert result['order_by']['direction'] == 'DESC'


def test_parse_limit():
    """Test parsing LIMIT clause"""
    parser = SQLParser()
    result = parser.parse("SELECT * FROM users LIMIT 10;")

    assert result['limit'] == 10


def test_parse_complex_where():
    """Test parsing complex WHERE with AND/OR"""
    parser = SQLParser()
    result = parser.parse("SELECT * FROM users WHERE age > 18 AND balance < 1000;")

    assert result['where']['type'] == 'LOGICAL'
    assert result['where']['operator'] == 'AND'

