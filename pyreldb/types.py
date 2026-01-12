"""
Data type definitions and validation
"""

from datetime import datetime
from typing import Any, Optional
from enum import Enum


class DataType(Enum):
    """Supported data types in the database"""

    INT = "INT"
    VARCHAR = "VARCHAR"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    DATETIME = "DATETIME"


class Column:
    """Represents a table column with its properties"""

    def __init__(
        self,
        name: str,
        data_type: DataType,
        length: Optional[int] = None,
        nullable: bool = True,
        primary_key: bool = False,
        unique: bool = False,
        default: Any = None,
    ):
        self.name = name
        self.data_type = data_type
        self.length = length
        self.nullable = nullable
        self.primary_key = primary_key
        self.unique = unique
        self.default = default

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against this column's type and constraints

        Returns:
            (is_valid, error_message)
        """
        # Check NULL constraint
        if value is None:
            if not self.nullable and not self.primary_key:
                return False, f"Column '{self.name}' cannot be NULL"
            return True, None

        # Type validation
        try:
            converted = self.convert(value)
            if converted is None and value is not None:
                return False, f"Invalid value for {self.data_type.value}"
        except (ValueError, TypeError) as e:
            return False, f"Type error for column '{self.name}': {str(e)}"

        # Length validation for VARCHAR
        if self.data_type == DataType.VARCHAR and self.length:
            if len(str(value)) > self.length:
                return (
                    False,
                    f"Value exceeds maximum length {self.length} for column '{self.name}'",
                )

        return True, None

    def convert(self, value: Any) -> Any:
        """Convert a value to the appropriate Python type"""
        if value is None:
            return None

        if self.data_type == DataType.INT:
            return int(value)
        elif self.data_type == DataType.FLOAT:
            return float(value)
        elif self.data_type == DataType.VARCHAR:
            return str(value)
        elif self.data_type == DataType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "t")
            return bool(value)
        elif self.data_type == DataType.DATETIME:
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                # Try common datetime formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Cannot parse datetime: {value}")
            raise ValueError(f"Invalid datetime value: {value}")

        return value

    def to_dict(self) -> dict:
        """Serialize column definition to dictionary"""
        return {
            "name": self.name,
            "data_type": self.data_type.value,
            "length": self.length,
            "nullable": self.nullable,
            "primary_key": self.primary_key,
            "unique": self.unique,
            "default": self.default,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Column":
        """Deserialize column definition from dictionary"""
        return cls(
            name=data["name"],
            data_type=DataType(data["data_type"]),
            length=data.get("length"),
            nullable=data.get("nullable", True),
            primary_key=data.get("primary_key", False),
            unique=data.get("unique", False),
            default=data.get("default"),
        )

    def __repr__(self) -> str:
        constraints = []
        if self.primary_key:
            constraints.append("PRIMARY KEY")
        if self.unique:
            constraints.append("UNIQUE")
        if not self.nullable:
            constraints.append("NOT NULL")

        type_str = self.data_type.value
        if self.data_type == DataType.VARCHAR and self.length:
            type_str += f"({self.length})"

        constraint_str = " " + " ".join(constraints) if constraints else ""
        return f"{self.name} {type_str}{constraint_str}"
