"""
SQL parser for PyRelDB

Supports:
- CREATE TABLE
- INSERT INTO
- SELECT (with WHERE, JOIN, ORDER BY, LIMIT)
- UPDATE
- DELETE
- CREATE INDEX
- DROP TABLE
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from pyreldb.types import DataType


class Token:
    """Represents a token in the SQL query"""

    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class Tokenizer:
    """Tokenizes SQL queries"""

    KEYWORDS = {
        "SELECT",
        "FROM",
        "WHERE",
        "INSERT",
        "INTO",
        "VALUES",
        "UPDATE",
        "SET",
        "DELETE",
        "CREATE",
        "TABLE",
        "DROP",
        "INDEX",
        "ON",
        "PRIMARY",
        "KEY",
        "UNIQUE",
        "NOT",
        "NULL",
        "DEFAULT",
        "AND",
        "OR",
        "JOIN",
        "INNER",
        "LEFT",
        "RIGHT",
        "OUTER",
        "ORDER",
        "BY",
        "ASC",
        "DESC",
        "LIMIT",
        "INT",
        "VARCHAR",
        "FLOAT",
        "BOOLEAN",
        "DATETIME",
    }

    def __init__(self, query: str):
        self.query = query
        self.pos = 0
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """Tokenize the entire query"""
        while self.pos < len(self.query):
            self._skip_whitespace()

            if self.pos >= len(self.query):
                break

            char = self.query[self.pos]

            # Comments
            if (
                char == "-"
                and self.pos + 1 < len(self.query)
                and self.query[self.pos + 1] == "-"
            ):
                self._skip_comment()
                continue

            # Strings
            if char in ("'", '"'):
                self.tokens.append(self._read_string())
            # Numbers
            elif char.isdigit() or (
                char == "-"
                and self.pos + 1 < len(self.query)
                and self.query[self.pos + 1].isdigit()
            ):
                self.tokens.append(self._read_number())
            # Identifiers and keywords
            elif char.isalpha() or char == "_":
                self.tokens.append(self._read_identifier())
            # Operators and punctuation
            elif char in "(),;=<>!*.":
                self.tokens.append(self._read_operator())
            else:
                raise ValueError(f"Unexpected character: {char}")

        return self.tokens

    def _skip_whitespace(self):
        """Skip whitespace characters"""
        while self.pos < len(self.query) and self.query[self.pos].isspace():
            self.pos += 1

    def _skip_comment(self):
        """Skip SQL comments (-- to end of line)"""
        while self.pos < len(self.query) and self.query[self.pos] != "\n":
            self.pos += 1

    def _read_string(self) -> Token:
        """Read a string literal"""
        quote = self.query[self.pos]
        self.pos += 1
        start = self.pos

        while self.pos < len(self.query) and self.query[self.pos] != quote:
            if self.query[self.pos] == "\\":
                self.pos += 2  # Skip escaped character
            else:
                self.pos += 1

        value = self.query[start : self.pos]
        self.pos += 1  # Skip closing quote
        return Token("STRING", value)

    def _read_number(self) -> Token:
        """Read a numeric literal"""
        start = self.pos

        if self.query[self.pos] == "-":
            self.pos += 1

        while self.pos < len(self.query) and (
            self.query[self.pos].isdigit() or self.query[self.pos] == "."
        ):
            self.pos += 1

        value = self.query[start : self.pos]
        return Token("NUMBER", value)

    def _read_identifier(self) -> Token:
        """Read an identifier or keyword"""
        start = self.pos

        while self.pos < len(self.query) and (
            self.query[self.pos].isalnum() or self.query[self.pos] == "_"
        ):
            self.pos += 1

        value = self.query[start : self.pos]
        token_type = "KEYWORD" if value.upper() in self.KEYWORDS else "IDENTIFIER"
        return Token(token_type, value.upper() if token_type == "KEYWORD" else value)

    def _read_operator(self) -> Token:
        """Read an operator or punctuation"""
        char = self.query[self.pos]
        self.pos += 1

        # Check for two-character operators
        if self.pos < len(self.query):
            two_char = char + self.query[self.pos]
            if two_char in ("<=", ">=", "!=", "<>"):
                self.pos += 1
                return Token("OPERATOR", two_char)

        return Token("OPERATOR" if char in "=<>!" else "PUNCT", char)


class SQLParser:
    """Parser for SQL queries"""

    def __init__(self):
        self.tokens: List[Token] = []
        self.pos = 0

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse an SQL query

        Returns:
            Dictionary containing parsed query structure
        """
        # Tokenize
        tokenizer = Tokenizer(query)
        self.tokens = tokenizer.tokenize()
        self.pos = 0

        if not self.tokens:
            raise ValueError("Empty query")

        # Determine query type
        first_token = self.tokens[0]

        if first_token.type != "KEYWORD":
            raise ValueError(f"Expected keyword, got {first_token.value}")

        keyword = first_token.value.upper()

        if keyword == "SELECT":
            return self._parse_select()
        elif keyword == "INSERT":
            return self._parse_insert()
        elif keyword == "UPDATE":
            return self._parse_update()
        elif keyword == "DELETE":
            return self._parse_delete()
        elif keyword == "CREATE":
            return self._parse_create()
        elif keyword == "DROP":
            return self._parse_drop()
        else:
            raise ValueError(f"Unsupported query type: {keyword}")

    def _current_token(self) -> Optional[Token]:
        """Get current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _advance(self) -> Optional[Token]:
        """Move to next token"""
        token = self._current_token()
        self.pos += 1
        return token

    def _expect(self, expected: str, token_type: str = "KEYWORD") -> Token:
        """Expect a specific token"""
        token = self._current_token()
        if (
            not token
            or token.type != token_type
            or token.value.upper() != expected.upper()
        ):
            raise ValueError(
                f"Expected {expected}, got {token.value if token else 'EOF'}"
            )
        return self._advance()

    def _parse_select(self) -> Dict[str, Any]:
        """Parse SELECT query"""
        self._advance()  # Skip SELECT

        # Parse columns
        columns = []
        while True:
            token = self._current_token()
            if not token:
                break

            if token.value == "*":
                columns.append("*")
                self._advance()
            elif token.type == "IDENTIFIER":
                col_name = token.value
                self._advance()

                # Check for table.column syntax
                if self._current_token() and self._current_token().value == ".":
                    self._advance()
                    col_part = self._current_token()
                    if col_part and col_part.type == "IDENTIFIER":
                        col_name = f"{col_name}.{col_part.value}"
                        self._advance()

                columns.append(col_name)

            # Check for comma
            if self._current_token() and self._current_token().value == ",":
                self._advance()
            else:
                break

        # Parse FROM
        self._expect("FROM")
        table_name = self._current_token()
        if not table_name or table_name.type != "IDENTIFIER":
            raise ValueError("Expected table name")
        self._advance()

        result = {
            "type": "SELECT",
            "columns": columns,
            "table": table_name.value,
            "joins": [],
            "where": None,
            "order_by": None,
            "limit": None,
        }

        # Parse optional clauses
        while self._current_token():
            token = self._current_token()

            if token.value.upper() in ("INNER", "LEFT", "RIGHT"):
                result["joins"].append(self._parse_join())
            elif token.value.upper() == "JOIN":
                result["joins"].append(self._parse_join(join_type="INNER"))
            elif token.value.upper() == "WHERE":
                result["where"] = self._parse_where()
            elif token.value.upper() == "ORDER":
                result["order_by"] = self._parse_order_by()
            elif token.value.upper() == "LIMIT":
                result["limit"] = self._parse_limit()
            else:
                break

        return result

    def _parse_join(self, join_type: Optional[str] = None) -> Dict[str, Any]:
        """Parse JOIN clause"""
        if not join_type:
            join_type = self._current_token().value.upper()
            self._advance()

        self._expect("JOIN")

        table = self._current_token()
        if not table or table.type != "IDENTIFIER":
            raise ValueError("Expected table name in JOIN")
        self._advance()

        self._expect("ON")

        # Parse join condition
        left = self._current_token()
        if not left or left.type != "IDENTIFIER":
            raise ValueError("Expected column name in JOIN condition")
        self._advance()

        # Handle table.column
        if self._current_token() and self._current_token().value == ".":
            self._advance()
            left_col = self._current_token()
            if not left_col or left_col.type != "IDENTIFIER":
                raise ValueError("Expected column name")
            left_value = f"{left.value}.{left_col.value}"
            self._advance()
        else:
            left_value = left.value

        operator = self._current_token()
        if not operator or operator.value != "=":
            raise ValueError("Expected = in JOIN condition")
        self._advance()

        right = self._current_token()
        if not right or right.type != "IDENTIFIER":
            raise ValueError("Expected column name in JOIN condition")
        self._advance()

        # Handle table.column
        if self._current_token() and self._current_token().value == ".":
            self._advance()
            right_col = self._current_token()
            if not right_col or right_col.type != "IDENTIFIER":
                raise ValueError("Expected column name")
            right_value = f"{right.value}.{right_col.value}"
            self._advance()
        else:
            right_value = right.value

        return {
            "type": join_type,
            "table": table.value,
            "on": {"left": left_value, "operator": "=", "right": right_value},
        }

    def _parse_where(self) -> Dict[str, Any]:
        """Parse WHERE clause"""
        self._advance()  # Skip WHERE

        return self._parse_condition()

    def _parse_condition(self) -> Dict[str, Any]:
        """Parse a condition (supports AND/OR)"""
        left = self._parse_simple_condition()

        while self._current_token() and self._current_token().value.upper() in (
            "AND",
            "OR",
        ):
            operator = self._current_token().value.upper()
            self._advance()
            right = self._parse_simple_condition()
            left = {
                "type": "LOGICAL",
                "operator": operator,
                "left": left,
                "right": right,
            }

        return left

    def _parse_simple_condition(self) -> Dict[str, Any]:
        """Parse a simple condition (column op value)"""
        column = self._current_token()
        if not column or column.type != "IDENTIFIER":
            raise ValueError("Expected column name in WHERE clause")
        self._advance()

        # Handle table.column
        column_value = column.value
        if self._current_token() and self._current_token().value == ".":
            self._advance()
            col_part = self._current_token()
            if not col_part or col_part.type != "IDENTIFIER":
                raise ValueError("Expected column name")
            column_value = f"{column.value}.{col_part.value}"
            self._advance()

        operator = self._current_token()
        if not operator or operator.type != "OPERATOR":
            raise ValueError("Expected operator in WHERE clause")
        self._advance()

        value = self._current_token()
        if not value:
            raise ValueError("Expected value in WHERE clause")

        value_data = self._parse_value(value)
        self._advance()

        return {
            "type": "COMPARISON",
            "column": column_value,
            "operator": operator.value,
            "value": value_data,
        }

    def _parse_value(self, token: Token) -> Any:
        """Parse a value token"""
        if token.type == "STRING":
            return token.value
        elif token.type == "NUMBER":
            if "." in token.value:
                return float(token.value)
            return int(token.value)
        elif token.type == "KEYWORD":
            if token.value.upper() == "NULL":
                return None
            elif token.value.upper() in ("TRUE", "FALSE"):
                return token.value.upper() == "TRUE"
        return token.value

    def _parse_order_by(self) -> Dict[str, Any]:
        """Parse ORDER BY clause"""
        self._expect("ORDER")
        self._expect("BY")

        column = self._current_token()
        if not column or column.type != "IDENTIFIER":
            raise ValueError("Expected column name in ORDER BY")
        self._advance()

        direction = "ASC"
        if self._current_token() and self._current_token().value.upper() in (
            "ASC",
            "DESC",
        ):
            direction = self._current_token().value.upper()
            self._advance()

        return {"column": column.value, "direction": direction}

    def _parse_limit(self) -> int:
        """Parse LIMIT clause"""
        self._advance()  # Skip LIMIT

        limit = self._current_token()
        if not limit or limit.type != "NUMBER":
            raise ValueError("Expected number in LIMIT")
        self._advance()

        return int(limit.value)

    def _parse_insert(self) -> Dict[str, Any]:
        """Parse INSERT query"""
        self._advance()  # Skip INSERT
        self._expect("INTO")

        table = self._current_token()
        if not table or table.type != "IDENTIFIER":
            raise ValueError("Expected table name")
        self._advance()

        # Parse column list (optional)
        columns = None
        if self._current_token() and self._current_token().value == "(":
            columns = []
            self._advance()

            while True:
                col = self._current_token()
                if not col or col.type != "IDENTIFIER":
                    raise ValueError("Expected column name")
                columns.append(col.value)
                self._advance()

                if self._current_token() and self._current_token().value == ",":
                    self._advance()
                elif self._current_token() and self._current_token().value == ")":
                    self._advance()
                    break
                else:
                    raise ValueError("Expected , or ) in column list")

        self._expect("VALUES")
        self._expect("(", "PUNCT")

        # Parse values
        values = []
        while True:
            val = self._current_token()
            if not val:
                raise ValueError("Expected value")

            values.append(self._parse_value(val))
            self._advance()

            if self._current_token() and self._current_token().value == ",":
                self._advance()
            elif self._current_token() and self._current_token().value == ")":
                self._advance()
                break
            else:
                raise ValueError("Expected , or ) in VALUES")

        return {
            "type": "INSERT",
            "table": table.value,
            "columns": columns,
            "values": values,
        }

    def _parse_update(self) -> Dict[str, Any]:
        """Parse UPDATE query"""
        self._advance()  # Skip UPDATE

        table = self._current_token()
        if not table or table.type != "IDENTIFIER":
            raise ValueError("Expected table name")
        self._advance()

        self._expect("SET")

        # Parse SET clause
        updates = {}
        while True:
            col = self._current_token()
            if not col or col.type != "IDENTIFIER":
                raise ValueError("Expected column name in SET")
            self._advance()

            self._expect("=", "OPERATOR")

            val = self._current_token()
            if not val:
                raise ValueError("Expected value in SET")

            updates[col.value] = self._parse_value(val)
            self._advance()

            if self._current_token() and self._current_token().value == ",":
                self._advance()
            else:
                break

        # Parse WHERE (optional)
        where = None
        if self._current_token() and self._current_token().value.upper() == "WHERE":
            where = self._parse_where()

        return {
            "type": "UPDATE",
            "table": table.value,
            "updates": updates,
            "where": where,
        }

    def _parse_delete(self) -> Dict[str, Any]:
        """Parse DELETE query"""
        self._advance()  # Skip DELETE
        self._expect("FROM")

        table = self._current_token()
        if not table or table.type != "IDENTIFIER":
            raise ValueError("Expected table name")
        self._advance()

        # Parse WHERE (optional)
        where = None
        if self._current_token() and self._current_token().value.upper() == "WHERE":
            where = self._parse_where()

        return {"type": "DELETE", "table": table.value, "where": where}

    def _parse_create(self) -> Dict[str, Any]:
        """Parse CREATE query"""
        self._advance()  # Skip CREATE

        token = self._current_token()
        if not token:
            raise ValueError("Expected TABLE or INDEX")

        if token.value.upper() == "TABLE":
            return self._parse_create_table()
        elif token.value.upper() == "INDEX":
            return self._parse_create_index()
        else:
            raise ValueError(f"Unexpected token after CREATE: {token.value}")

    def _parse_create_table(self) -> Dict[str, Any]:
        """Parse CREATE TABLE query"""
        self._advance()  # Skip TABLE

        table = self._current_token()
        if not table or table.type != "IDENTIFIER":
            raise ValueError("Expected table name")
        self._advance()

        self._expect("(", "PUNCT")

        # Parse column definitions
        columns = []
        while True:
            col_name = self._current_token()
            if not col_name or col_name.type != "IDENTIFIER":
                raise ValueError("Expected column name")
            self._advance()

            col_type = self._current_token()
            if not col_type or col_type.type != "KEYWORD":
                raise ValueError("Expected column type")

            # Parse type
            type_name = col_type.value.upper()
            length = None
            self._advance()

            # Check for length (e.g., VARCHAR(100))
            if self._current_token() and self._current_token().value == "(":
                self._advance()
                length_token = self._current_token()
                if not length_token or length_token.type != "NUMBER":
                    raise ValueError("Expected number for type length")
                length = int(length_token.value)
                self._advance()
                self._expect(")", "PUNCT")

            # Parse constraints
            primary_key = False
            unique = False
            nullable = True
            default = None

            while self._current_token() and self._current_token().type == "KEYWORD":
                keyword = self._current_token().value.upper()

                if keyword == "PRIMARY":
                    self._advance()
                    self._expect("KEY")
                    primary_key = True
                elif keyword == "UNIQUE":
                    self._advance()
                    unique = True
                elif keyword == "NOT":
                    self._advance()
                    self._expect("NULL")
                    nullable = False
                elif keyword == "DEFAULT":
                    self._advance()
                    default_token = self._current_token()
                    if not default_token:
                        raise ValueError("Expected default value")
                    default = self._parse_value(default_token)
                    self._advance()
                else:
                    break

            columns.append(
                {
                    "name": col_name.value,
                    "type": type_name,
                    "length": length,
                    "primary_key": primary_key,
                    "unique": unique,
                    "nullable": nullable,
                    "default": default,
                }
            )

            if self._current_token() and self._current_token().value == ",":
                self._advance()
            elif self._current_token() and self._current_token().value == ")":
                self._advance()
                break
            else:
                raise ValueError("Expected , or ) in column definition")

        return {"type": "CREATE_TABLE", "table": table.value, "columns": columns}

    def _parse_create_index(self) -> Dict[str, Any]:
        """Parse CREATE INDEX query"""
        self._advance()  # Skip INDEX

        index_name = self._current_token()
        if not index_name or index_name.type != "IDENTIFIER":
            raise ValueError("Expected index name")
        self._advance()

        self._expect("ON")

        table = self._current_token()
        if not table or table.type != "IDENTIFIER":
            raise ValueError("Expected table name")
        self._advance()

        self._expect("(", "PUNCT")

        column = self._current_token()
        if not column or column.type != "IDENTIFIER":
            raise ValueError("Expected column name")
        self._advance()

        self._expect(")", "PUNCT")

        return {
            "type": "CREATE_INDEX",
            "index_name": index_name.value,
            "table": table.value,
            "column": column.value,
        }

    def _parse_drop(self) -> Dict[str, Any]:
        """Parse DROP query"""
        self._advance()  # Skip DROP
        self._expect("TABLE")

        table = self._current_token()
        if not table or table.type != "IDENTIFIER":
            raise ValueError("Expected table name")
        self._advance()

        return {"type": "DROP_TABLE", "table": table.value}
