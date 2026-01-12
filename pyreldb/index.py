"""
Indexing implementation for PyRelDB
"""

from typing import Any, List, Optional, Tuple
import bisect


class BTreeNode:
    """Node in a Index"""

    def __init__(self, is_leaf: bool = True, order: int = 3):
        self.is_leaf = is_leaf
        self.keys: List[Any] = []
        self.values: List[int] = []  # Row indices
        self.children: List["BTreeNode"] = []
        self.order = order

    def is_full(self) -> bool:
        """Check if node is full"""
        return len(self.keys) >= 2 * self.order - 1


class BTreeIndex:
    """
    Index implementation for efficient lookups
    Supports O(log n) search, insert, and delete operations
    """

    def __init__(self, column_name: str, order: int = 3):
        self.column_name = column_name
        self.order = order
        self.root = BTreeNode(is_leaf=True, order=order)
        self.size = 0

    def search(self, key: Any) -> List[int]:
        """
        Search for a key and return all matching row indices

        Args:
            key: The value to search for

        Returns:
            List of row indices where the key was found
        """
        return self._search_node(self.root, key)

    def _search_node(self, node: BTreeNode, key: Any) -> List[int]:
        """Recursively search for a key in the tree"""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            if node.is_leaf:
                return [node.values[i]]
            else:
                # For internal nodes, also check children
                return [node.values[i]] + self._search_node(node.children[i + 1], key)
        elif node.is_leaf:
            return []
        else:
            return self._search_node(node.children[i], key)

    def range_search(self, start: Any, end: Any) -> List[int]:
        """
        Search for all keys in a range [start, end]

        Args:
            start: Start of range (inclusive)
            end: End of range (inclusive)

        Returns:
            List of row indices for keys in range
        """
        result = []
        self._range_search_node(self.root, start, end, result)
        return result

    def _range_search_node(
        self, node: BTreeNode, start: Any, end: Any, result: List[int]
    ):
        """Recursively search for keys in range"""
        i = 0
        while i < len(node.keys):
            if node.keys[i] >= start and node.keys[i] <= end:
                result.append(node.values[i])

            if not node.is_leaf and node.keys[i] <= end:
                self._range_search_node(node.children[i], start, end, result)

            i += 1

        if not node.is_leaf and (len(node.keys) == 0 or node.keys[-1] <= end):
            self._range_search_node(node.children[-1], start, end, result)

    def insert(self, key: Any, row_index: int):
        """
        Insert a key-value pair into the index

        Args:
            key: The indexed value
            row_index: The row index in the table
        """
        if self.root.is_full():
            # Split root
            new_root = BTreeNode(is_leaf=False, order=self.order)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root

        self._insert_non_full(self.root, key, row_index)
        self.size += 1

    def _insert_non_full(self, node: BTreeNode, key: Any, row_index: int):
        """Insert into a node that is not full"""
        i = len(node.keys) - 1

        if node.is_leaf:
            # Insert into leaf node
            node.keys.append(None)
            node.values.append(None)

            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1

            node.keys[i + 1] = key
            node.values[i + 1] = row_index
        else:
            # Find child to insert into
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            if node.children[i].is_full():
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key, row_index)

    def _split_child(self, parent: BTreeNode, index: int):
        """Split a full child node"""
        order = self.order
        full_child = parent.children[index]
        new_child = BTreeNode(is_leaf=full_child.is_leaf, order=order)

        mid = order - 1

        # Move half of keys to new node
        new_child.keys = full_child.keys[mid + 1 :]
        new_child.values = full_child.values[mid + 1 :]
        full_child.keys = full_child.keys[:mid]
        full_child.values = full_child.values[:mid]

        if not full_child.is_leaf:
            new_child.children = full_child.children[mid + 1 :]
            full_child.children = full_child.children[: mid + 1]

        # Insert middle key into parent
        parent.keys.insert(
            index,
            full_child.keys[mid] if mid < len(full_child.keys) else new_child.keys[0],
        )
        parent.values.insert(
            index,
            full_child.values[mid]
            if mid < len(full_child.values)
            else new_child.values[0],
        )
        parent.children.insert(index + 1, new_child)

    def delete(self, key: Any, row_index: int):
        """
        Delete a key-value pair from the index

        Args:
            key: The indexed value
            row_index: The row index to remove
        """
        self._delete_from_node(self.root, key, row_index)
        self.size -= 1

    def _delete_from_node(self, node: BTreeNode, key: Any, row_index: int):
        """Delete from a node (simplified implementation)"""
        try:
            i = node.keys.index(key)
            if node.values[i] == row_index:
                del node.keys[i]
                del node.values[i]
                if not node.is_leaf and i < len(node.children):
                    del node.children[i]
                return True
        except ValueError:
            pass

        # If not found in current node, search children
        if not node.is_leaf:
            for child in node.children:
                if self._delete_from_node(child, key, row_index):
                    return True

        return False

    def to_dict(self) -> dict:
        """Serialize index to dictionary"""
        return {
            "column_name": self.column_name,
            "order": self.order,
            "size": self.size,
            "entries": self._collect_entries(self.root),
        }

    def _collect_entries(self, node: BTreeNode) -> List[Tuple[Any, int]]:
        """Collect all key-value pairs from tree"""
        entries = []
        for i in range(len(node.keys)):
            entries.append((node.keys[i], node.values[i]))

        if not node.is_leaf:
            for child in node.children:
                entries.extend(self._collect_entries(child))

        return entries

    @classmethod
    def from_dict(cls, data: dict) -> "BTreeIndex":
        """Deserialize index from dictionary"""
        index = cls(data["column_name"], data["order"])
        for key, row_index in data["entries"]:
            index.insert(key, row_index)
        return index

    def __repr__(self) -> str:
        return f"BTreeIndex(column={self.column_name}, size={self.size})"


class SimpleIndex:
    """
    Simple hash-based index for exact match lookups
    Faster than B-tree for equality checks, but doesn't support range queries
    """

    def __init__(self, column_name: str):
        self.column_name = column_name
        self.index: dict[Any, List[int]] = {}

    def insert(self, key: Any, row_index: int):
        """Insert a key-value pair"""
        if key not in self.index:
            self.index[key] = []
        self.index[key].append(row_index)

    def search(self, key: Any) -> List[int]:
        """Search for a key"""
        return self.index.get(key, [])

    def delete(self, key: Any, row_index: int):
        """Delete a key-value pair"""
        if key in self.index:
            try:
                self.index[key].remove(row_index)
                if not self.index[key]:
                    del self.index[key]
            except ValueError:
                pass

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "column_name": self.column_name,
            "index": {str(k): v for k, v in self.index.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SimpleIndex":
        """Deserialize from dictionary"""
        index = cls(data["column_name"])
        index.index = {k: v for k, v in data["index"].items()}
        return index
