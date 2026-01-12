"""
Storage engine and database management
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from pyreldb.table import Table
from pyreldb.types import Column


class Database:
    """Main database class managing tables and persistence"""

    def __init__(self, name: str = "default", data_dir: str = "data"):
        self.name = name
        self.data_dir = Path(data_dir)
        self.tables: Dict[str, Table] = {}
        self.db_file = self.data_dir / f"{name}.json"

        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load database if it exists
        if self.db_file.exists():
            self.load()

    def create_table(self, name: str, columns: list[Column]) -> Table:
        """
        Create a new table

        Args:
            name: Table name
            columns: List of Column definitions

        Returns:
            The created Table object
        """
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")

        if not columns:
            raise ValueError("Table must have at least one column")

        table = Table(name, columns)
        self.tables[name] = table
        self.save()
        return table

    def drop_table(self, name: str):
        """Drop a table"""
        if name not in self.tables:
            raise ValueError(f"Table '{name}' does not exist")

        del self.tables[name]
        self.save()

    def get_table(self, name: str) -> Optional[Table]:
        """Get a table by name"""
        return self.tables.get(name)

    def list_tables(self) -> list[str]:
        """List all table names"""
        return list(self.tables.keys())

    def table_exists(self, name: str) -> bool:
        """Check if a table exists"""
        return name in self.tables

    def save(self):
        """Persist database to disk"""
        data = {
            "name": self.name,
            "created_at": datetime.now().isoformat(),
            "tables": {name: table.to_dict() for name, table in self.tables.items()},
        }

        # Write to temporary file first, then rename (atomic operation)
        temp_file = self.db_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

        temp_file.replace(self.db_file)

    def load(self):
        """Load database from disk"""
        if not self.db_file.exists():
            return

        with open(self.db_file, "r") as f:
            data = json.load(f)

        self.name = data.get("name", self.name)
        self.tables = {}

        for table_name, table_data in data.get("tables", {}).items():
            self.tables[table_name] = Table.from_dict(table_data)

    def export_table_csv(self, table_name: str, output_file: str):
        """Export a table to CSV format"""
        table = self.get_table(table_name)
        if not table:
            raise ValueError(f"Table '{table_name}' does not exist")

        import csv

        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=table.column_order)
            writer.writeheader()

            for row in table.scan():
                writer.writerow(row.data)

    def get_stats(self) -> dict:
        """Get database statistics"""
        stats = {"name": self.name, "num_tables": len(self.tables), "tables": {}}

        for name, table in self.tables.items():
            stats["tables"][name] = {
                "columns": len(table.columns),
                "rows": len(table.scan()),
                "indexes": len(table.indexes),
                "size_kb": len(json.dumps(table.to_dict())) / 1024,
            }

        return stats

    def __repr__(self) -> str:
        return f"Database(name={self.name}, tables={len(self.tables)})"
