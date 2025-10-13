"""
Page hierarchy traversal for Notion workspaces.

This module provides functionality to discover and build a hierarchical
tree structure of Notion pages and their relationships.
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from client_wrapper import NotionClientWrapper


@dataclass
class PageNode:
    """Represents a page in the hierarchy tree."""

    page_id: str
    title: str
    parent_id: Optional[str] = None
    children: List['PageNode'] = field(default_factory=list)
    is_database: bool = False
    has_content: bool = True  # Whether the page has any block content

    def __repr__(self) -> str:
        child_count = len(self.children)
        db_marker = " [DB]" if self.is_database else ""
        return f"PageNode('{self.title}', {child_count} children{db_marker})"

    def to_tree_string(self, indent: int = 0, is_last: bool = True) -> str:
        """
        Generate a tree-like string representation.

        Args:
            indent: Current indentation level
            is_last: Whether this is the last child of its parent

        Returns:
            Formatted tree string
        """
        prefix = "  " * indent
        connector = "└─ " if is_last else "├─ "

        if indent == 0:
            connector = ""

        db_marker = " [Database]" if self.is_database else ""
        result = f"{prefix}{connector}{self.title}{db_marker}\n"

        for i, child in enumerate(self.children):
            is_last_child = i == len(self.children) - 1
            result += child.to_tree_string(indent + 1, is_last_child)

        return result


def extract_page_title(page: dict) -> str:
    """
    Extract the title from a Notion page object.

    Args:
        page: Notion page object

    Returns:
        Page title or "Untitled" if no title found
    """
    if "properties" not in page:
        return "Untitled"

    # Look for title property
    for prop_name, prop_value in page["properties"].items():
        if prop_value.get("type") == "title":
            title_array = prop_value.get("title", [])
            if title_array and len(title_array) > 0:
                return title_array[0].get("plain_text", "Untitled")

    return "Untitled"


def extract_child_page_title(block: dict) -> str:
    """
    Extract the title from a child_page block.

    Args:
        block: Notion block object with type "child_page"

    Returns:
        Page title or "Untitled" if no title found
    """
    if block.get("type") == "child_page":
        child_page = block.get("child_page", {})
        return child_page.get("title", "Untitled")

    return "Untitled"


def discover_child_pages(client: NotionClientWrapper, page_id: str) -> List[Dict]:
    """
    Discover all child pages of a given page.

    Args:
        client: Notion client wrapper
        page_id: The parent page ID

    Returns:
        List of child page blocks
    """
    child_pages = []

    try:
        blocks = client.get_block_children(page_id)

        for block in blocks:
            if block.get("type") == "child_page":
                child_pages.append(block)
            elif block.get("type") == "child_database":
                # Treat databases as pages too
                child_pages.append(block)

    except Exception as e:
        print(f"Warning: Could not fetch children of page {page_id}: {e}")

    return child_pages


def build_page_tree(
    client: NotionClientWrapper,
    page_id: str,
    parent_id: Optional[str] = None,
    visited: Optional[Set[str]] = None,
    depth: int = 0,
    max_depth: int = 10
) -> Optional[PageNode]:
    """
    Recursively build a tree of pages starting from a root page.

    Args:
        client: Notion client wrapper
        page_id: The page ID to start from
        parent_id: The parent page ID (None for root)
        visited: Set of already visited page IDs (to prevent cycles)
        depth: Current recursion depth
        max_depth: Maximum recursion depth to prevent infinite loops

    Returns:
        PageNode representing the page and its children, or None if error
    """
    # Initialize visited set on first call
    if visited is None:
        visited = set()

    # Check for cycles
    if page_id in visited:
        print(f"Warning: Circular reference detected for page {page_id}")
        return None

    # Check depth limit
    if depth >= max_depth:
        print(f"Warning: Maximum depth {max_depth} reached for page {page_id}")
        return None

    # Mark as visited
    visited.add(page_id)

    try:
        # Get the page
        page = client.get_page(page_id)

        # Determine if it's a database
        is_database = page.get("object") == "database"

        # Extract title
        title = extract_page_title(page)

        # Create node
        node = PageNode(
            page_id=page_id,
            title=title,
            parent_id=parent_id,
            is_database=is_database
        )

        # Discover child pages
        child_page_blocks = discover_child_pages(client, page_id)

        # Recursively build children
        for child_block in child_page_blocks:
            child_id = child_block["id"]
            child_type = child_block.get("type")

            # Get title from block
            if child_type == "child_page":
                child_title = extract_child_page_title(child_block)
            elif child_type == "child_database":
                child_db = child_block.get("child_database", {})
                child_title = child_db.get("title", "Untitled Database")
            else:
                child_title = "Untitled"

            # Build child tree
            child_node = build_page_tree(
                client,
                child_id,
                parent_id=page_id,
                visited=visited,
                depth=depth + 1,
                max_depth=max_depth
            )

            if child_node:
                # Override title from the full page object
                node.children.append(child_node)

        return node

    except Exception as e:
        print(f"Error processing page {page_id}: {e}")
        return None


def discover_all_root_pages(client: NotionClientWrapper) -> List[Dict]:
    """
    Discover all root-level pages accessible to the integration.

    These are pages that are not children of other pages.

    Args:
        client: Notion client wrapper

    Returns:
        List of root page objects
    """
    try:
        # Search for all pages
        all_pages = client.search_pages()

        # Filter out pages that have a parent page
        # (only keep workspace roots and pages in the workspace)
        root_pages = []

        for page in all_pages:
            parent = page.get("parent", {})
            parent_type = parent.get("type")

            # Root pages have parent type: "workspace" or "page_id" is None
            # We want pages directly in the workspace
            if parent_type == "workspace":
                root_pages.append(page)

        return root_pages

    except Exception as e:
        print(f"Error discovering root pages: {e}")
        return []


def build_full_hierarchy(
    client: NotionClientWrapper,
    root_page_id: Optional[str] = None,
    max_depth: int = 10
) -> List[PageNode]:
    """
    Build the complete page hierarchy.

    Args:
        client: Notion client wrapper
        root_page_id: Optional specific page ID to start from.
                      If None, discovers all root pages.
        max_depth: Maximum depth to traverse

    Returns:
        List of root PageNodes
    """
    roots = []

    if root_page_id:
        # Build tree from specific page
        root_node = build_page_tree(client, root_page_id, max_depth=max_depth)
        if root_node:
            roots.append(root_node)
    else:
        # Discover all root pages and build trees
        root_pages = discover_all_root_pages(client)

        print(f"Discovered {len(root_pages)} root page(s)")

        for page in root_pages:
            page_id = page["id"]
            root_node = build_page_tree(client, page_id, max_depth=max_depth)
            if root_node:
                roots.append(root_node)

    return roots


def print_hierarchy(roots: List[PageNode]) -> None:
    """
    Print the page hierarchy in a tree format.

    Args:
        roots: List of root PageNodes
    """
    if not roots:
        print("No pages found.")
        return

    print("\nPage Hierarchy:")
    print("=" * 50)

    for root in roots:
        print(root.to_tree_string())


if __name__ == '__main__':
    """Test the hierarchy module."""
    print("Building page hierarchy...")
    print()

    try:
        from client_wrapper import create_client

        client = create_client()

        # Build full hierarchy
        roots = build_full_hierarchy(client)

        # Print the tree
        print_hierarchy(roots)

        # Print statistics
        total_pages = sum(count_pages(root) for root in roots)
        print(f"\nTotal pages: {total_pages}")

    except Exception as e:
        print(f"Error: {e}")


def count_pages(node: PageNode) -> int:
    """Count total pages in a tree."""
    return 1 + sum(count_pages(child) for child in node.children)
