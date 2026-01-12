"""
Query execution engine for PyRelDB
"""

from typing import Any, Dict, List, Optional
from pyreldb.storage import Database
from pyreldb.table import Table, Row
from pyreldb.types import Column, DataType
from pyreldb.parser import SQLParser


class QueryResult:
    """Represents the result of a query"""

    def __init__(
        self,
        columns: List[str],
        rows: List[Dict[str, Any]],
        message: Optional[str] = None,
    ):
        self.columns = columns
        self.rows = rows
        self.message = message
        self.row_count = len(rows)

    def __repr__(self) -> str:
        if self.message:
            return self.message
        return f"QueryResult(rows={self.row_count}, columns={len(self.columns)})"


class QueryExecutor:
    """Executes parsed SQL queries"""

    def __init__(self, database: Database):
        self.database = database
        self.parser = SQLParser()

    def execute(self, query: str) -> QueryResult:
        """
        Execute an SQL query

        Args:
            query: SQL query string

        Returns:
            QueryResult object
        """
        # Parse query
        parsed = self.parser.parse(query)

        # Execute based on type
        query_type = parsed["type"]

        if query_type == "SELECT":
            return self._execute_select(parsed)
        elif query_type == "INSERT":
            return self._execute_insert(parsed)
        elif query_type == "UPDATE":
            return self._execute_update(parsed)
        elif query_type == "DELETE":
            return self._execute_delete(parsed)
        elif query_type == "CREATE_TABLE":
            return self._execute_create_table(parsed)
        elif query_type == "CREATE_INDEX":
            return self._execute_create_index(parsed)
        elif query_type == "DROP_TABLE":
            return self._execute_drop_table(parsed)
        else:
            raise ValueError(f"Unsupported query type: {query_type}")

    def _execute_select(self, parsed: Dict[str, Any]) -> QueryResult:
        """Execute SELECT query"""
        table = self.database.get_table(parsed["table"])
        if not table:
            raise ValueError(f"Table '{parsed['table']}' does not exist")

        # Start with all rows
        rows = table.scan()

        # Apply JOINs
        if parsed["joins"]:
            rows = self._apply_joins(table, rows, parsed["joins"])

        # Apply WHERE clause
        if parsed["where"]:
            rows = [
                row
                for row in rows
                if self._evaluate_condition(row, parsed["where"], table)
            ]

        # Apply ORDER BY
        if parsed["order_by"]:
            column = parsed["order_by"]["column"]
            reverse = parsed["order_by"]["direction"] == "DESC"
            rows = sorted(
                rows,
                key=lambda r: r.get(column) if r.get(column) is not None else "",
                reverse=reverse,
            )

        # Apply LIMIT
        if parsed["limit"]:
            rows = rows[: parsed["limit"]]

        # Select columns
        columns = parsed["columns"]
        if columns == ["*"]:
            if parsed["joins"]:
                # For joins, get all columns from all tables
                columns = list(rows[0].data.keys()) if rows else []
            else:
                columns = table.column_order

        # Format result
        result_rows = []
        for row in rows:
            result_row = {}
            for col in columns:
                # Handle table.column syntax
                if "." in col:
                    # Extract column name without table prefix for result key
                    col_name = col.split(".", 1)[1]
                    # Try to get value using full table.column name first,
                    # then just column name
                    if col in row.data:
                        value = row.get(col)
                    else:
                        value = row.get(col_name)
                    result_row[col_name] = value
                else:
                    result_row[col] = row.get(col)
            result_rows.append(result_row)

        # Update columns list to use unprefixed names
        result_columns = [
            col.split(".", 1)[1] if "." in col else col for col in columns
        ]
        return QueryResult(result_columns, result_rows)

    def _apply_joins(
        self, base_table: Table, base_rows: List[Row], joins: List[Dict[str, Any]]
    ) -> List[Row]:
        """Apply JOIN operations"""
        result_rows = []

        for join in joins:
            join_table = self.database.get_table(join["table"])
            if not join_table:
                raise ValueError(f"Table '{join['table']}' does not exist")

            join_rows = join_table.scan()
            join_type = join["type"]

            # Parse join condition
            left_col = join["on"]["left"]
            right_col = join["on"]["right"]

            # Extract table and column names
            if "." in left_col:
                left_table, left_col_name = left_col.split(".", 1)
            else:
                left_table = base_table.name
                left_col_name = left_col

            if "." in right_col:
                right_table, right_col_name = right_col.split(".", 1)
            else:
                right_table = join_table.name
                right_col_name = right_col

            # Perform join
            joined_rows = []

            if join_type == "INNER":
                for base_row in base_rows if result_rows == [] else result_rows:
                    for join_row in join_rows:
                        # Get values for comparison
                        left_val = base_row.get(left_col_name)
                        right_val = join_row.get(right_col_name)

                        if left_val == right_val:
                            # Merge rows
                            merged_data = {}

                            # Add base table columns with table prefix
                            for col_name, col_val in base_row.data.items():
                                merged_data[f"{base_table.name}.{col_name}"] = col_val
                                merged_data[
                                    col_name
                                ] = col_val  # Also add without prefix

                            # Add join table columns with table prefix
                            for col_name, col_val in join_row.data.items():
                                merged_data[f"{join_table.name}.{col_name}"] = col_val
                                if col_name not in merged_data:
                                    merged_data[col_name] = col_val

                            joined_rows.append(Row(merged_data, base_row.row_id))

            elif join_type == "LEFT":
                for base_row in base_rows if result_rows == [] else result_rows:
                    matched = False

                    for join_row in join_rows:
                        left_val = base_row.get(left_col_name)
                        right_val = join_row.get(right_col_name)

                        if left_val == right_val:
                            matched = True

                            # Merge rows
                            merged_data = {}

                            for col_name, col_val in base_row.data.items():
                                merged_data[f"{base_table.name}.{col_name}"] = col_val
                                merged_data[col_name] = col_val

                            for col_name, col_val in join_row.data.items():
                                merged_data[f"{join_table.name}.{col_name}"] = col_val
                                if col_name not in merged_data:
                                    merged_data[col_name] = col_val

                            joined_rows.append(Row(merged_data, base_row.row_id))

                    if not matched:
                        # Add base row with NULL values for join table columns
                        merged_data = {}

                        for col_name, col_val in base_row.data.items():
                            merged_data[f"{base_table.name}.{col_name}"] = col_val
                            merged_data[col_name] = col_val

                        for col_name in join_table.columns.keys():
                            merged_data[f"{join_table.name}.{col_name}"] = None

                        joined_rows.append(Row(merged_data, base_row.row_id))

            result_rows = joined_rows if joined_rows else result_rows

        return result_rows if result_rows else base_rows

    def _evaluate_condition(
        self, row: Row, condition: Dict[str, Any], table: Table
    ) -> bool:
        """Evaluate a WHERE condition"""
        if condition["type"] == "LOGICAL":
            # AND/OR
            left_result = self._evaluate_condition(row, condition["left"], table)
            right_result = self._evaluate_condition(row, condition["right"], table)

            if condition["operator"] == "AND":
                return left_result and right_result
            else:  # OR
                return left_result or right_result

        elif condition["type"] == "COMPARISON":
            # Get column value (handle table.column syntax)
            column = condition["column"]
            if "." in column:
                col_value = row.get(column)
            else:
                col_value = row.get(column)

            compare_value = condition["value"]
            operator = condition["operator"]

            # Perform comparison
            if operator == "=":
                return col_value == compare_value
            elif operator in ("!=", "<>"):
                return col_value != compare_value
            elif operator == "<":
                return col_value < compare_value if col_value is not None else False
            elif operator == ">":
                return col_value > compare_value if col_value is not None else False
            elif operator == "<=":
                return col_value <= compare_value if col_value is not None else False
            elif operator == ">=":
                return col_value >= compare_value if col_value is not None else False
            else:
                raise ValueError(f"Unknown operator: {operator}")

        return False

    def _execute_insert(self, parsed: Dict[str, Any]) -> QueryResult:
        """Execute INSERT query"""
        table = self.database.get_table(parsed["table"])
        if not table:
            raise ValueError(f"Table '{parsed['table']}' does not exist")

        # Build row data
        if parsed["columns"]:
            # Column list provided
            if len(parsed["columns"]) != len(parsed["values"]):
                raise ValueError("Column count doesn't match value count")

            row_data = {
                col: val for col, val in zip(parsed["columns"], parsed["values"])
            }
        else:
            # No column list, assume all columns in order
            if len(parsed["values"]) != len(table.column_order):
                raise ValueError("Value count doesn't match table column count")

            row_data = {
                col: val for col, val in zip(table.column_order, parsed["values"])
            }

        # Insert
        row = table.insert(row_data)
        self.database.save()

        return QueryResult([], [], f"Inserted 1 row (row_id={row.row_id})")

    def _execute_update(self, parsed: Dict[str, Any]) -> QueryResult:
        """Execute UPDATE query"""
        table = self.database.get_table(parsed["table"])
        if not table:
            raise ValueError(f"Table '{parsed['table']}' does not exist")

        # Find rows to update
        rows = table.scan()

        if parsed["where"]:
            rows = [
                row
                for row in rows
                if self._evaluate_condition(row, parsed["where"], table)
            ]

        # Update rows
        updated_count = 0
        for row in rows:
            row_index = table.rows.index(row)
            table.update(row_index, parsed["updates"])
            updated_count += 1

        self.database.save()

        return QueryResult([], [], f"Updated {updated_count} row(s)")

    def _execute_delete(self, parsed: Dict[str, Any]) -> QueryResult:
        """Execute DELETE query"""
        table = self.database.get_table(parsed["table"])
        if not table:
            raise ValueError(f"Table '{parsed['table']}' does not exist")

        # Find rows to delete
        rows = table.scan()

        if parsed["where"]:
            rows = [
                row
                for row in rows
                if self._evaluate_condition(row, parsed["where"], table)
            ]

        # Delete rows
        deleted_count = 0
        for row in rows:
            row_index = table.rows.index(row)
            table.delete(row_index)
            deleted_count += 1

        self.database.save()

        return QueryResult([], [], f"Deleted {deleted_count} row(s)")

    def _execute_create_table(self, parsed: Dict[str, Any]) -> QueryResult:
        """Execute CREATE TABLE query"""
        # Build column list
        columns = []
        for col_def in parsed["columns"]:
            col = Column(
                name=col_def["name"],
                data_type=DataType(col_def["type"]),
                length=col_def.get("length"),
                nullable=col_def.get("nullable", True),
                primary_key=col_def.get("primary_key", False),
                unique=col_def.get("unique", False),
                default=col_def.get("default"),
            )
            columns.append(col)

        # Create table
        table = self.database.create_table(parsed["table"], columns)

        return QueryResult([], [], f"Created table '{table.name}'")

    def _execute_create_index(self, parsed: Dict[str, Any]) -> QueryResult:
        """Execute CREATE INDEX query"""
        table = self.database.get_table(parsed["table"])
        if not table:
            raise ValueError(f"Table '{parsed['table']}' does not exist")

        table.create_index(parsed["column"])
        self.database.save()

        return QueryResult(
            [], [], f"Created index on {parsed['table']}.{parsed['column']}"
        )

    def _execute_drop_table(self, parsed: Dict[str, Any]) -> QueryResult:
        """Execute DROP TABLE query"""
        self.database.drop_table(parsed["table"])

        return QueryResult([], [], f"Dropped table '{parsed['table']}'")
