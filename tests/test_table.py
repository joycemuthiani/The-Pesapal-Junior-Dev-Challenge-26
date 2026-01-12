"""
Tests for table operations
"""

import pytest
from pyreldb.table import Table
from pyreldb.types import Column, DataType


@pytest.fixture
def sample_table():
    """Create a sample table for testing"""
    columns = [
        Column("id", DataType.INT, primary_key=True),
        Column("name", DataType.VARCHAR, length=100, nullable=False),
        Column("email", DataType.VARCHAR, length=100, unique=True),
        Column("balance", DataType.FLOAT, default=0.0)
    ]
    return Table("users", columns)


def test_table_creation(sample_table):
    """Test table creation"""
    assert sample_table.name == "users"
    assert len(sample_table.columns) == 4
    assert "id" in sample_table.columns


def test_insert_row(sample_table):
    """Test inserting a row"""
    row = sample_table.insert({
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "balance": 100.0
    })

    assert row.row_id == 0
    assert row["name"] == "John Doe"
    assert len(sample_table.scan()) == 1


def test_insert_with_defaults(sample_table):
    """Test inserting with default values"""
    row = sample_table.insert({
        "id": 1,
        "name": "Jane Doe",
        "email": "jane@example.com"
    })

    assert row["balance"] == 0.0  # Default value


def test_primary_key_constraint(sample_table):
    """Test primary key uniqueness"""
    sample_table.insert({
        "id": 1,
        "name": "User 1",
        "email": "user1@example.com"
    })

    # Try to insert duplicate primary key
    with pytest.raises(ValueError):
        sample_table.insert({
            "id": 1,
            "name": "User 2",
            "email": "user2@example.com"
        })


def test_unique_constraint(sample_table):
    """Test unique constraint"""
    sample_table.insert({
        "id": 1,
        "name": "User 1",
        "email": "same@example.com"
    })

    # Try to insert duplicate email
    with pytest.raises(ValueError):
        sample_table.insert({
            "id": 2,
            "name": "User 2",
            "email": "same@example.com"
        })


def test_update_row(sample_table):
    """Test updating a row"""
    row = sample_table.insert({
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "balance": 100.0
    })

    sample_table.update(0, {"balance": 200.0})

    rows = sample_table.scan()
    assert rows[0]["balance"] == 200.0


def test_delete_row(sample_table):
    """Test deleting a row"""
    sample_table.insert({
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    })

    sample_table.delete(0)

    assert len(sample_table.scan()) == 0


def test_find_by_column(sample_table):
    """Test finding rows by column value"""
    sample_table.insert({
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    })
    sample_table.insert({
        "id": 2,
        "name": "Jane Doe",
        "email": "jane@example.com"
    })

    results = sample_table.find_by_column("name", "John Doe")
    assert len(results) == 1
    assert results[0]["email"] == "john@example.com"


def test_table_serialization(sample_table):
    """Test table serialization"""
    sample_table.insert({
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    })

    table_dict = sample_table.to_dict()
    assert table_dict['name'] == "users"
    assert len(table_dict['rows']) == 1

    # Deserialize
    table2 = Table.from_dict(table_dict)
    assert table2.name == sample_table.name
    assert len(table2.scan()) == 1

