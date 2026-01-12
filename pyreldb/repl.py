"""
Interactive REPL for PyRelDB
"""

import sys
import os
from typing import Optional
from pyreldb.storage import Database
from pyreldb.executor import QueryExecutor, QueryResult


class REPL:
    """Read-Eval-Print Loop for database interaction"""

    def __init__(self, db_name: str = "default"):
        self.database = Database(db_name)
        self.executor = QueryExecutor(self.database)
        self.running = True

    def format_table(self, result: QueryResult) -> str:
        """Format query result as a table"""
        if result.message:
            return result.message

        if not result.rows:
            return "No rows returned."

        # Calculate column widths
        col_widths = {}
        for col in result.columns:
            col_widths[col] = len(col)

        for row in result.rows:
            for col in result.columns:
                value = str(row.get(col, ''))
                col_widths[col] = max(col_widths[col], len(value))

        # Build table
        lines = []

        # Header
        header = "| " + " | ".join(col.ljust(col_widths[col]) for col in result.columns) + " |"
        separator = "+" + "+".join("-" * (col_widths[col] + 2) for col in result.columns) + "+"

        lines.append(separator)
        lines.append(header)
        lines.append(separator)

        # Rows
        for row in result.rows:
            row_str = "| " + " | ".join(
                str(row.get(col, '')).ljust(col_widths[col]) for col in result.columns
            ) + " |"
            lines.append(row_str)

        lines.append(separator)
        lines.append(f"\n{len(result.rows)} row(s) returned.")

        return "\n".join(lines)

    def execute_command(self, command: str) -> Optional[str]:
        """Execute a REPL command"""
        command = command.strip()

        if not command:
            return None

        # Meta commands
        if command.startswith('.'):
            return self._execute_meta_command(command)

        # SQL query
        try:
            result = self.executor.execute(command)
            return self.format_table(result)
        except Exception as e:
            return f"Error: {str(e)}"

    def _execute_meta_command(self, command: str) -> str:
        """Execute a meta command (starting with .)"""
        parts = command.split()
        cmd = parts[0].lower()

        if cmd == '.help':
            return self._show_help()
        elif cmd == '.tables':
            return self._show_tables()
        elif cmd == '.schema':
            table_name = parts[1] if len(parts) > 1 else None
            return self._show_schema(table_name)
        elif cmd == '.stats':
            return self._show_stats()
        elif cmd == '.exit' or cmd == '.quit':
            self.running = False
            return "Goodbye!"
        else:
            return f"Unknown command: {cmd}. Type .help for available commands."

    def _show_help(self) -> str:
        """Show help message"""
        return """
Interactive REPL
========================

SQL Commands:
  CREATE TABLE table_name (column_name TYPE [constraints], ...)
  INSERT INTO table_name [(columns)] VALUES (values)
  SELECT columns FROM table_name [WHERE condition] [ORDER BY column] [LIMIT n]
  UPDATE table_name SET column=value [WHERE condition]
  DELETE FROM table_name [WHERE condition]
  DROP TABLE table_name
  CREATE INDEX index_name ON table_name (column)

Supported Data Types:
  INT, VARCHAR(length), FLOAT, BOOLEAN, DATETIME

Constraints:
  PRIMARY KEY, UNIQUE, NOT NULL, DEFAULT value

Meta Commands:
  .help           Show this help message
  .tables         List all tables
  .schema [name]  Show schema for a table (or all tables)
  .stats          Show database statistics
  .exit, .quit    Exit the REPL

Examples:
  CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100) UNIQUE);
  INSERT INTO users (id, name, email) VALUES (1, 'John Doe', 'john@example.com');
  SELECT * FROM users WHERE id = 1;
  UPDATE users SET name = 'Jane Doe' WHERE id = 1;
  DELETE FROM users WHERE id = 1;
"""

    def _show_tables(self) -> str:
        """Show all tables"""
        tables = self.database.list_tables()
        if not tables:
            return "No tables in database."

        output = ["Tables in database:"]
        for table_name in tables:
            table = self.database.get_table(table_name)
            row_count = len(table.scan())
            output.append(f"  - {table_name} ({row_count} rows)")

        return "\n".join(output)

    def _show_schema(self, table_name: Optional[str] = None) -> str:
        """Show table schema"""
        if table_name:
            table = self.database.get_table(table_name)
            if not table:
                return f"Table '{table_name}' does not exist."

            output = [f"\nSchema for table '{table_name}':"]
            output.append("-" * 60)

            for col_name in table.column_order:
                col = table.columns[col_name]
                output.append(f"  {col}")

            if table.indexes:
                output.append(f"\nIndexes:")
                for idx_name, idx in table.indexes.items():
                    output.append(f"  - {idx}")

            return "\n".join(output)
        else:
            # Show all tables
            tables = self.database.list_tables()
            if not tables:
                return "No tables in database."

            output = []
            for tbl_name in tables:
                output.append(self._show_schema(tbl_name))

            return "\n".join(output)

    def _show_stats(self) -> str:
        """Show database statistics"""
        stats = self.database.get_stats()

        output = [f"\nDatabase: {stats['name']}"]
        output.append(f"Tables: {stats['num_tables']}")
        output.append("")

        if stats['tables']:
            output.append("Table Statistics:")
            output.append("-" * 60)

            for table_name, table_stats in stats['tables'].items():
                output.append(f"\n  {table_name}:")
                output.append(f"    Columns: {table_stats['columns']}")
                output.append(f"    Rows: {table_stats['rows']}")
                output.append(f"    Indexes: {table_stats['indexes']}")
                output.append(f"    Size: {table_stats['size_kb']:.2f} KB")

        return "\n".join(output)

    def run(self):
        """Run the REPL"""
        print("╔════════════════════════════════════════════════════════╗")
        print("║         Simple RDBMS v1.0.0                  ║")
        print("║    Pesapal Junior Developer Challenge '26              ║")
        print("╚════════════════════════════════════════════════════════╝")
        print("\nType .help for help, .exit to quit\n")

        buffer = []

        while self.running:
            try:
                # Prompt
                if buffer:
                    line = input("  ... ")
                else:
                    line = input("pyreldb> ")

                # Add to buffer
                buffer.append(line)

                # Check if query is complete (ends with semicolon)
                if line.strip().endswith(';'):
                    # Remove semicolon and execute
                    query = ' '.join(buffer).rstrip(';')
                    buffer = []

                    result = self.execute_command(query)
                    if result:
                        print(result)
                        print()
                elif line.strip().startswith('.'):
                    # Meta command
                    query = ' '.join(buffer)
                    buffer = []

                    result = self.execute_command(query)
                    if result:
                        print(result)
                        print()

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type .exit to quit.")
                buffer = []
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}\n")
                buffer = []


def main():
    """Main entry point"""
    db_name = "default"

    if len(sys.argv) > 1:
        db_name = sys.argv[1]

    repl = REPL(db_name)
    repl.run()


if __name__ == '__main__':
    main()

