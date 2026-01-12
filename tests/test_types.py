"""
Tests for data types and column definitions
"""

import pytest
from datetime import datetime
from pyreldb.types import Column, DataType


def test_column_creation():
    """Test creating a column"""
    col = Column("id", DataType.INT, primary_key=True)
    assert col.name == "id"
    assert col.data_type == DataType.INT
    assert col.primary_key is True


def test_int_validation():
    """Test INT type validation"""
    col = Column("age", DataType.INT, nullable=False)

    # Valid values
    is_valid, error = col.validate(25)
    assert is_valid is True
    assert error is None

    # NULL value
    is_valid, error = col.validate(None)
    assert is_valid is False


def test_varchar_validation():
    """Test VARCHAR type validation with length constraint"""
    col = Column("name", DataType.VARCHAR, length=10)

    # Valid value
    is_valid, error = col.validate("John")
    assert is_valid is True

    # Too long
    is_valid, error = col.validate("Very Long Name")
    assert is_valid is False


def test_float_validation():
    """Test FLOAT type validation"""
    col = Column("price", DataType.FLOAT)

    is_valid, error = col.validate(19.99)
    assert is_valid is True

    is_valid, error = col.validate("19.99")
    assert is_valid is True  # Should convert string to float


def test_boolean_validation():
    """Test BOOLEAN type validation"""
    col = Column("active", DataType.BOOLEAN)

    is_valid, error = col.validate(True)
    assert is_valid is True

    is_valid, error = col.validate("true")
    assert is_valid is True


def test_datetime_validation():
    """Test DATETIME type validation"""
    col = Column("created_at", DataType.DATETIME)

    is_valid, error = col.validate(datetime.now())
    assert is_valid is True

    is_valid, error = col.validate("2024-01-01 12:00:00")
    assert is_valid is True


def test_column_serialization():
    """Test column serialization/deserialization"""
    col = Column("email", DataType.VARCHAR, length=100, unique=True)

    col_dict = col.to_dict()
    assert col_dict['name'] == "email"
    assert col_dict['data_type'] == "VARCHAR"
    assert col_dict['length'] == 100
    assert col_dict['unique'] is True

    # Deserialize
    col2 = Column.from_dict(col_dict)
    assert col2.name == col.name
    assert col2.data_type == col.data_type
    assert col2.length == col.length
    assert col2.unique == col.unique

