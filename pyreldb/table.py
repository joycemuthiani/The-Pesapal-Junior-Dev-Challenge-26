"""
Table and schema management
"""

from typing import Any, Dict, List, Optional
from pyreldb.types import Column, DataType
from pyreldb.index import BTreeIndex, SimpleIndex


class Row:
    """Represents a row in a table"""

    def __init__(self, data: Dict[str, Any], row_id: int):
        self.data = data
        self.row_id = row_id

    def __getitem__(self, key: str) -> Any:
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any):
        self.data[key] = value

    def get(self, key: str, default=None) -> Any:
        return self.data.get(key, default)

    def to_dict(self) -> dict:
        return {
            'row_id': self.row_id,
            'data': self.data
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Row':
        return cls(data['data'], data['row_id'])


class Table:
    """Represents a database table"""

    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.column_order = [col.name for col in columns]
        self.rows: List[Row] = []
        self.indexes: Dict[str, BTreeIndex] = {}
        self.next_row_id = 0

        # Create indexes for primary key and unique columns
        for col in columns:
            if col.primary_key or col.unique:
                self.create_index(col.name)

    def create_index(self, column_name: str, index_type: str = 'btree'):
        """Create an index on a column"""
        if column_name not in self.columns:
            raise ValueError(f"Column '{column_name}' does not exist")

        if column_name in self.indexes:
            return  # Index already exists

        if index_type == 'btree':
            index = BTreeIndex(column_name)
        else:
            index = SimpleIndex(column_name)

        # Build index from existing rows
        for i, row in enumerate(self.rows):
            value = row[column_name]
            if value is not None:
                index.insert(value, i)

        self.indexes[column_name] = index

    def get_primary_key_column(self) -> Optional[Column]:
        """Get the primary key column if it exists"""
        for col in self.columns.values():
            if col.primary_key:
                return col
        return None

    def validate_row(self, data: Dict[str, Any], is_update: bool = False, exclude_row_index: Optional[int] = None) -> tuple[bool, Optional[str]]:
        """
        Validate a row against table schema and constraints

        Args:
            data: Row data to validate
            is_update: Whether this is an update (less strict validation)
            exclude_row_index: Row index to exclude from duplicate checks (for updates)

        Returns:
            (is_valid, error_message)
        """
        # Check for unknown columns
        for col_name in data.keys():
            if col_name not in self.columns:
                return False, f"Unknown column: '{col_name}'"

        # Validate each column
        for col_name, column in self.columns.items():
            value = data.get(col_name)

            # For updates, only validate provided columns
            if is_update and col_name not in data:
                continue

            # Validate type and constraints
            is_valid, error = column.validate(value)
            if not is_valid:
                return False, error

            # Check unique constraint (skip if this is the row being updated)
            if column.unique or column.primary_key:
                if value is not None:
                    existing_rows = self.find_by_column(col_name, value)
                    # Filter out the row being updated
                    if exclude_row_index is not None:
                        existing_rows = [r for r in existing_rows if self.rows.index(r) != exclude_row_index]
                    if existing_rows:
                        return False, f"Duplicate value for {('PRIMARY KEY' if column.primary_key else 'UNIQUE')} column '{col_name}'"

        return True, None

    def insert(self, data: Dict[str, Any]) -> Row:
        """
        Insert a new row into the table

        Args:
            data: Dictionary of column_name -> value

        Returns:
            The inserted Row object
        """
        # Fill in defaults for missing columns
        full_data = {}
        for col_name, column in self.columns.items():
            if col_name in data:
                full_data[col_name] = column.convert(data[col_name])
            elif column.default is not None:
                full_data[col_name] = column.default
            else:
                full_data[col_name] = None

        # Validate
        is_valid, error = self.validate_row(full_data)
        if not is_valid:
            raise ValueError(f"Validation error: {error}")

        # Create row
        row = Row(full_data, self.next_row_id)
        self.next_row_id += 1

        # Insert into table
        row_index = len(self.rows)
        self.rows.append(row)

        # Update indexes
        for col_name, index in self.indexes.items():
            value = row[col_name]
            if value is not None:
                index.insert(value, row_index)

        return row

    def find_by_column(self, column_name: str, value: Any) -> List[Row]:
        """Find rows where column equals value"""
        if column_name in self.indexes:
            # Use index for fast lookup
            row_indices = self.indexes[column_name].search(value)
            return [self.rows[i] for i in row_indices if i < len(self.rows)]
        else:
            # Full table scan
            return [row for row in self.rows if row[column_name] == value]

    def find_by_range(self, column_name: str, start: Any, end: Any) -> List[Row]:
        """Find rows where column value is in range [start, end]"""
        if column_name in self.indexes and isinstance(self.indexes[column_name], BTreeIndex):
            # Use B-tree index for range query
            row_indices = self.indexes[column_name].range_search(start, end)
            return [self.rows[i] for i in row_indices if i < len(self.rows)]
        else:
            # Full table scan
            return [row for row in self.rows
                    if row[column_name] is not None and start <= row[column_name] <= end]

    def update(self, row_index: int, updates: Dict[str, Any]) -> Row:
        """
        Update a row

        Args:
            row_index: Index of row to update
            updates: Dictionary of column_name -> new_value

        Returns:
            The updated Row object
        """
        if row_index >= len(self.rows):
            raise ValueError(f"Invalid row index: {row_index}")

        row = self.rows[row_index]
        old_data = row.data.copy()

        # Apply updates
        new_data = row.data.copy()
        for col_name, value in updates.items():
            if col_name not in self.columns:
                raise ValueError(f"Unknown column: '{col_name}'")
            new_data[col_name] = self.columns[col_name].convert(value)

        # Validate (excluding current row from unique checks)
        is_valid, error = self.validate_row(new_data, is_update=True, exclude_row_index=row_index)

        if not is_valid:
            raise ValueError(f"Validation error: {error}")

        # Update indexes
        for col_name in updates.keys():
            if col_name in self.indexes:
                # Remove old value from index
                old_value = old_data[col_name]
                if old_value is not None:
                    self.indexes[col_name].delete(old_value, row_index)

                # Add new value to index
                new_value = new_data[col_name]
                if new_value is not None:
                    self.indexes[col_name].insert(new_value, row_index)

        # Apply updates
        row.data = new_data
        return row

    def delete(self, row_index: int):
        """Delete a row"""
        if row_index >= len(self.rows):
            raise ValueError(f"Invalid row index: {row_index}")

        row = self.rows[row_index]

        # Remove from indexes
        for col_name, index in self.indexes.items():
            value = row[col_name]
            if value is not None:
                index.delete(value, row_index)

        # Mark as deleted (we keep the slot to maintain row indices)
        self.rows[row_index] = None

    def scan(self) -> List[Row]:
        """Get all non-deleted rows"""
        return [row for row in self.rows if row is not None]

    def to_dict(self) -> dict:
        """Serialize table to dictionary"""
        return {
            'name': self.name,
            'columns': [col.to_dict() for col in self.columns.values()],
            'column_order': self.column_order,
            'rows': [row.to_dict() if row else None for row in self.rows],
            'indexes': {name: idx.to_dict() for name, idx in self.indexes.items()},
            'next_row_id': self.next_row_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Table':
        """Deserialize table from dictionary"""
        columns = [Column.from_dict(col) for col in data['columns']]
        table = cls(data['name'], columns)
        table.column_order = data['column_order']
        table.next_row_id = data['next_row_id']

        # Restore rows
        table.rows = [Row.from_dict(row) if row else None for row in data['rows']]

        # Restore indexes
        for name, idx_data in data.get('indexes', {}).items():
            if 'order' in idx_data:
                table.indexes[name] = BTreeIndex.from_dict(idx_data)
            else:
                table.indexes[name] = SimpleIndex.from_dict(idx_data)

        return table

    def __repr__(self) -> str:
        return f"Table({self.name}, columns={len(self.columns)}, rows={len(self.scan())})"

