"""
Integration tests for the entire system
"""

import pytest
import os
import tempfile
from pyreldb.storage import Database
from pyreldb.executor import QueryExecutor


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    temp_dir = tempfile.mkdtemp()
    db = Database("test_db", data_dir=temp_dir)
    yield db
    # Cleanup
    db_file = db.db_file
    if db_file.exists():
        os.remove(db_file)
    os.rmdir(temp_dir)


def test_create_and_insert(temp_db):
    """Test creating a table and inserting data"""
    executor = QueryExecutor(temp_db)

    # Create table
    result = executor.execute("""
        CREATE TABLE customers (
            id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            balance FLOAT
        );
    """)
    assert "Created table" in result.message

    # Insert data
    result = executor.execute("""
        INSERT INTO customers (id, name, balance)
        VALUES (1, 'John Doe', 1000.00);
    """)
    assert "Inserted 1 row" in result.message

    # Select data
    result = executor.execute("SELECT * FROM customers;")
    assert len(result.rows) == 1
    assert result.rows[0]['name'] == 'John Doe'


def test_full_crud_cycle(temp_db):
    """Test complete CRUD operations"""
    executor = QueryExecutor(temp_db)

    # Create
    executor.execute("""
        CREATE TABLE products (
            id INT PRIMARY KEY,
            name VARCHAR(100),
            price FLOAT
        );
    """)

    # Insert
    executor.execute("INSERT INTO products (id, name, price) VALUES (1, 'Laptop', 50000);")
    executor.execute("INSERT INTO products (id, name, price) VALUES (2, 'Phone', 30000);")

    # Read
    result = executor.execute("SELECT * FROM products;")
    assert len(result.rows) == 2

    # Update
    executor.execute("UPDATE products SET price = 45000 WHERE id = 1;")
    result = executor.execute("SELECT * FROM products WHERE id = 1;")
    assert result.rows[0]['price'] == 45000

    # Delete
    executor.execute("DELETE FROM products WHERE id = 2;")
    result = executor.execute("SELECT * FROM products;")
    assert len(result.rows) == 1


def test_join_operation(temp_db):
    """Test JOIN operations"""
    executor = QueryExecutor(temp_db)

    # Create tables
    executor.execute("""
        CREATE TABLE customers (
            id INT PRIMARY KEY,
            name VARCHAR(100)
        );
    """)

    executor.execute("""
        CREATE TABLE orders (
            id INT PRIMARY KEY,
            customer_id INT,
            amount FLOAT
        );
    """)

    # Insert data
    executor.execute("INSERT INTO customers (id, name) VALUES (1, 'Alice');")
    executor.execute("INSERT INTO customers (id, name) VALUES (2, 'Bob');")
    executor.execute("INSERT INTO orders (id, customer_id, amount) VALUES (1, 1, 100.0);")
    executor.execute("INSERT INTO orders (id, customer_id, amount) VALUES (2, 1, 200.0);")

    # Join query
    result = executor.execute("""
        SELECT customers.name, orders.amount
        FROM customers
        INNER JOIN orders ON customers.id = orders.customer_id;
    """)

    assert len(result.rows) == 2
    assert all('name' in row for row in result.rows)
    assert all('amount' in row for row in result.rows)


def test_where_clause_filtering(temp_db):
    """Test WHERE clause with various conditions"""
    executor = QueryExecutor(temp_db)

    executor.execute("""
        CREATE TABLE users (
            id INT PRIMARY KEY,
            age INT,
            balance FLOAT
        );
    """)

    executor.execute("INSERT INTO users (id, age, balance) VALUES (1, 25, 5000);")
    executor.execute("INSERT INTO users (id, age, balance) VALUES (2, 30, 3000);")
    executor.execute("INSERT INTO users (id, age, balance) VALUES (3, 20, 7000);")

    # Test > operator
    result = executor.execute("SELECT * FROM users WHERE age > 22;")
    assert len(result.rows) == 2

    # Test < operator
    result = executor.execute("SELECT * FROM users WHERE balance < 6000;")
    assert len(result.rows) == 2

    # Test = operator
    result = executor.execute("SELECT * FROM users WHERE id = 2;")
    assert len(result.rows) == 1
    assert result.rows[0]['age'] == 30


def test_indexing_performance(temp_db):
    """Test that indexes improve query performance"""
    executor = QueryExecutor(temp_db)

    executor.execute("""
        CREATE TABLE indexed_table (
            id INT PRIMARY KEY,
            value VARCHAR(100)
        );
    """)

    # Insert multiple rows
    for i in range(100):
        executor.execute(f"INSERT INTO indexed_table (id, value) VALUES ({i}, 'value_{i}');")

    # Create index
    executor.execute("CREATE INDEX idx_value ON indexed_table (value);")

    # Query should use index
    result = executor.execute("SELECT * FROM indexed_table WHERE id = 50;")
    assert len(result.rows) == 1
    assert result.rows[0]['value'] == 'value_50'


def test_persistence(temp_db):
    """Test that data persists across database instances"""
    executor = QueryExecutor(temp_db)

    # Create and populate table
    executor.execute("""
        CREATE TABLE persistent (
            id INT PRIMARY KEY,
            data VARCHAR(100)
        );
    """)
    executor.execute("INSERT INTO persistent (id, data) VALUES (1, 'test_data');")

    # Get data directory
    data_dir = str(temp_db.data_dir)

    # Create new database instance
    db2 = Database("test_db", data_dir=data_dir)
    executor2 = QueryExecutor(db2)

    # Data should still be there
    result = executor2.execute("SELECT * FROM persistent;")
    assert len(result.rows) == 1
    assert result.rows[0]['data'] == 'test_data'


def test_order_by(temp_db):
    """Test ORDER BY clause"""
    executor = QueryExecutor(temp_db)

    executor.execute("""
        CREATE TABLE scores (
            id INT PRIMARY KEY,
            name VARCHAR(100),
            score INT
        );
    """)

    executor.execute("INSERT INTO scores (id, name, score) VALUES (1, 'Alice', 85);")
    executor.execute("INSERT INTO scores (id, name, score) VALUES (2, 'Bob', 92);")
    executor.execute("INSERT INTO scores (id, name, score) VALUES (3, 'Carol', 78);")

    # Test ASC
    result = executor.execute("SELECT * FROM scores ORDER BY score;")
    assert result.rows[0]['name'] == 'Carol'
    assert result.rows[2]['name'] == 'Bob'

    # Test DESC
    result = executor.execute("SELECT * FROM scores ORDER BY score DESC;")
    assert result.rows[0]['name'] == 'Bob'
    assert result.rows[2]['name'] == 'Carol'


def test_limit(temp_db):
    """Test LIMIT clause"""
    executor = QueryExecutor(temp_db)

    executor.execute("""
        CREATE TABLE items (
            id INT PRIMARY KEY,
            name VARCHAR(100)
        );
    """)

    for i in range(10):
        executor.execute(f"INSERT INTO items (id, name) VALUES ({i}, 'item_{i}');")

    result = executor.execute("SELECT * FROM items LIMIT 5;")
    assert len(result.rows) == 5

