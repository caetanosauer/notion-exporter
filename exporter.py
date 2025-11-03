"""
Exporter module for writing Notion pages to local markdown files.

This module handles file system operations including folder creation,
filename sanitization, and markdown file writing.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from hierarchy import PageNode
from markdown_converter import MarkdownConverter
from client_wrapper import NotionClientWrapper


class ExportStats:
    """Statistics about the export process."""

    def __init__(self):
        self.pages_exported = 0
        self.pages_failed = 0
        self.files_created = 0
        self.folders_created = 0
        self.errors: List[tuple] = []  # (page_id, error_message)
        self.unsupported_features: List = []  # Will be populated from converter

    def add_error(self, page_id: str, error: str):
        """Record an error."""
        self.errors.append((page_id, error))
        self.pages_failed += 1

    def __repr__(self) -> str:
        return (
            f"ExportStats(exported={self.pages_exported}, "
            f"failed={self.pages_failed}, "
            f"files={self.files_created}, "
            f"folders={self.folders_created})"
        )


def sanitize_filename(name: str, max_length: int = 200) -> str:
    """
    Sanitize a string to be used as a filename.

    Args:
        name: The original name
        max_length: Maximum filename length

    Returns:
        Sanitized filename
    """
    # Replace or remove invalid characters
    # Invalid: / \ : * ? " < > |
    sanitized = re.sub(r'[/\\:*?"<>|]', '_', name)

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')

    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)

    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('. ')

    # Ensure it's not empty
    if not sanitized:
        sanitized = "Untitled"

    return sanitized


def make_unique_filename(base_path: Path, name: str, extension: str = ".md") -> Path:
    """
    Generate a unique filename by appending numbers if necessary.

    Args:
        base_path: Directory where file will be created
        name: Base filename (without extension)
        extension: File extension

    Returns:
        Unique Path object
    """
    sanitized = sanitize_filename(name)
    path = base_path / f"{sanitized}{extension}"

    if not path.exists():
        return path

    # File exists, append number
    counter = 1
    while True:
        path = base_path / f"{sanitized}_{counter}{extension}"
        if not path.exists():
            return path
        counter += 1


class Exporter:
    """Handles exporting Notion pages to markdown files."""

    def __init__(
        self,
        client: NotionClientWrapper,
        output_dir: Path,
        dry_run: bool = False,
        include_databases: bool = False
    ):
        """
        Initialize the exporter.

        Args:
            client: Notion client wrapper
            output_dir: Root directory for export
            dry_run: If True, don't actually create files
            include_databases: If True, export databases (and don't report them as unsupported)
        """
        self.client = client
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.include_databases = include_databases
        # Track skipped databases only when NOT including them
        self.converter = MarkdownConverter(track_skipped_databases=not include_databases)
        self.stats = ExportStats()
        self.used_paths: Set[str] = set()

    def export_page_content(self, page_id: str) -> Optional[str]:
        """
        Export the content of a single page as markdown.

        Args:
            page_id: Notion page ID

        Returns:
            Markdown string or None if error
        """
        try:
            # Get all blocks for this page
            blocks = self.client.get_block_children(page_id)

            # Convert to markdown
            markdown = self.converter.convert_blocks(blocks)

            return markdown

        except Exception as e:
            self.stats.add_error(page_id, str(e))
            print(f"Error exporting page {page_id}: {e}")
            return None

    def create_directory(self, path: Path) -> bool:
        """
        Create a directory if it doesn't exist.

        Args:
            path: Directory path

        Returns:
            True if created or exists, False on error
        """
        if self.dry_run:
            print(f"[DRY RUN] Would create directory: {path}")
            return True

        try:
            path.mkdir(parents=True, exist_ok=True)
            if str(path) not in self.used_paths:
                self.stats.folders_created += 1
                self.used_paths.add(str(path))
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False

    def write_file(self, path: Path, content: str) -> bool:
        """
        Write content to a file.

        Args:
            path: File path
            content: File content

        Returns:
            True if successful, False otherwise
        """
        if self.dry_run:
            print(f"[DRY RUN] Would write file: {path}")
            return True

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.stats.files_created += 1
            return True
        except Exception as e:
            print(f"Error writing file {path}: {e}")
            return False

    def export_node(
        self,
        node: PageNode,
        parent_path: Path,
        verbose: bool = False
    ) -> bool:
        """
        Export a page node and its children recursively.

        Args:
            node: PageNode to export
            parent_path: Parent directory path
            verbose: Show verbose progress

        Returns:
            True if successful, False otherwise
        """
        if verbose:
            print(f"Exporting: {node.title}")

        # Get page content
        content = self.export_page_content(node.page_id)

        if content is None:
            return False

        # Determine file structure based on children
        if node.children:
            # Has children: create folder with index.md
            folder_name = sanitize_filename(node.title)
            folder_path = parent_path / folder_name

            # Create folder
            if not self.create_directory(folder_path):
                self.stats.add_error(node.page_id, "Failed to create directory")
                return False

            # Write index.md
            index_path = folder_path / "index.md"
            if not self.write_file(index_path, content):
                self.stats.add_error(node.page_id, "Failed to write index.md")
                return False

            self.stats.pages_exported += 1

            # Export children
            for child in node.children:
                self.export_node(child, folder_path, verbose)

        else:
            # No children: create single .md file
            file_path = make_unique_filename(parent_path, node.title, ".md")

            if not self.write_file(file_path, content):
                self.stats.add_error(node.page_id, "Failed to write file")
                return False

            self.stats.pages_exported += 1

        return True

    def export_hierarchy(
        self,
        roots: List[PageNode],
        verbose: bool = False
    ) -> ExportStats:
        """
        Export a complete page hierarchy.

        Args:
            roots: List of root PageNodes
            verbose: Show verbose progress

        Returns:
            ExportStats object
        """
        # Create output directory
        if not self.create_directory(self.output_dir):
            print(f"Failed to create output directory: {self.output_dir}")
            return self.stats

        # Export each root
        for root in roots:
            self.export_node(root, self.output_dir, verbose)

        # Copy unsupported features from converter to stats
        self.stats.unsupported_features = self.converter.unsupported_features

        return self.stats

    def print_dry_run_tree(self, roots: List[PageNode]) -> None:
        """
        Print a tree view of what would be exported.

        Args:
            roots: List of root PageNodes
        """
        print("\n[DRY RUN] Files and folders that would be created:")
        print("=" * 60)

        for root in roots:
            self._print_node_structure(root, self.output_dir, 0)

    def _print_node_structure(
        self,
        node: PageNode,
        parent_path: Path,
        indent: int
    ) -> None:
        """Helper method to print node structure recursively."""
        prefix = "  " * indent

        if node.children:
            # Folder with index.md
            folder_name = sanitize_filename(node.title)
            folder_path = parent_path / folder_name

            print(f"{prefix}📁 {folder_name}/")
            print(f"{prefix}  📄 index.md")

            for child in node.children:
                self._print_node_structure(child, folder_path, indent + 1)
        else:
            # Single file
            filename = sanitize_filename(node.title) + ".md"
            print(f"{prefix}📄 {filename}")


def export_notion_workspace(
    client: NotionClientWrapper,
    output_dir: str,
    page_id: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = False,
    include_databases: bool = False
) -> ExportStats:
    """
    Main export function for Notion workspace.

    Args:
        client: Notion client wrapper
        output_dir: Output directory path
        page_id: Optional specific page ID to export
        dry_run: If True, only show what would be done
        verbose: Show detailed progress
        include_databases: If True, export databases

    Returns:
        ExportStats object
    """
    from hierarchy import build_full_hierarchy

    # Build page hierarchy
    if verbose or dry_run:
        print("Building page hierarchy...")

    roots = build_full_hierarchy(client, page_id)

    if not roots:
        print("No pages found to export.")
        return ExportStats()

    # Create exporter
    exporter = Exporter(client, Path(output_dir), dry_run=dry_run, include_databases=include_databases)

    # Dry run preview
    if dry_run:
        exporter.print_dry_run_tree(roots)
        print("\nRun without --dry-run to actually create these files.")
        return ExportStats()

    # Actual export
    if verbose:
        print(f"\nExporting to: {output_dir}")
        print("=" * 60)

    stats = exporter.export_hierarchy(roots, verbose=verbose)

    return stats


if __name__ == '__main__':
    """Test the exporter."""
    from client_wrapper import create_client

    print("Testing exporter with dry run...")

    try:
        client = create_client()
        stats = export_notion_workspace(
            client,
            "notion",
            dry_run=True,
            verbose=True
        )

        print()
        print(f"Stats: {stats}")

    except Exception as e:
        print(f"Error: {e}")
