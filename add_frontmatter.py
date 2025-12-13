"""
Add YAML front matter to existing exported Notion markdown files.

This script re-fetches metadata from the Notion API and adds front matter
to already-exported files in a specified directory.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

from client_wrapper import create_client, NotionClientWrapper
from hierarchy import build_full_hierarchy, PageNode
from exporter import sanitize_filename


@dataclass
class PageMetadata:
    """Metadata for a Notion page."""
    page_id: str
    title: str
    created_time: str
    last_edited_time: str


def fetch_page_metadata(client: NotionClientWrapper, page_id: str) -> Optional[PageMetadata]:
    """Fetch metadata for a single page from Notion API."""
    try:
        page = client.get_page(page_id)

        # Extract title from properties
        title = "Untitled"
        if "properties" in page:
            for prop_value in page["properties"].values():
                if prop_value.get("type") == "title":
                    title_array = prop_value.get("title", [])
                    if title_array:
                        title = title_array[0].get("plain_text", "Untitled")
                    break

        return PageMetadata(
            page_id=page_id,
            title=title,
            created_time=page.get("created_time", "unknown"),
            last_edited_time=page.get("last_edited_time", "unknown")
        )
    except Exception as e:
        print(f"  Warning: Could not fetch metadata for {page_id}: {e}")
        return None


def build_path_to_metadata_map(
    client: NotionClientWrapper,
    node: PageNode,
    base_path: Path,
    mapping: Dict[Path, PageMetadata]
) -> None:
    """
    Recursively build a mapping from file paths to page metadata.

    Args:
        client: Notion client wrapper
        node: Current page node
        base_path: Current directory path
        mapping: Dictionary to populate with path -> metadata
    """
    # Fetch metadata for this page
    metadata = fetch_page_metadata(client, node.page_id)
    if not metadata:
        return

    if node.children:
        # Has children: folder/index.md
        folder_name = sanitize_filename(node.title)
        folder_path = base_path / folder_name
        file_path = folder_path / "index.md"
        mapping[file_path] = metadata

        # Recurse into children
        for child in node.children:
            build_path_to_metadata_map(client, child, folder_path, mapping)
    else:
        # No children: single .md file
        file_name = sanitize_filename(node.title) + ".md"
        file_path = base_path / file_name
        mapping[file_path] = metadata


def generate_frontmatter(metadata: PageMetadata, export_date: str = "2025-11-03") -> str:
    """Generate YAML front matter string."""
    # Escape quotes in title
    safe_title = metadata.title.replace('"', '\\"')

    return f'''---
title: "{safe_title}"
source: "Exported from Notion, November 2025"
export_date: {export_date}
notion_id: {metadata.page_id}
created: {metadata.created_time}
last_edited: {metadata.last_edited_time}
---

'''


def has_frontmatter(content: str) -> bool:
    """Check if content already has YAML front matter."""
    return content.startswith('---\n')


def add_frontmatter_to_file(file_path: Path, metadata: PageMetadata, dry_run: bool = False) -> bool:
    """
    Add front matter to a markdown file.

    Returns True if file was modified, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if has_frontmatter(content):
            print(f"  Skipping (already has frontmatter): {file_path.name}")
            return False

        frontmatter = generate_frontmatter(metadata)
        new_content = frontmatter + content

        if dry_run:
            print(f"  [DRY RUN] Would add frontmatter to: {file_path}")
            return True

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"  Added frontmatter: {file_path.name}")
        return True

    except Exception as e:
        print(f"  Error processing {file_path}: {e}")
        return False


def add_frontmatter_to_directory(
    output_dir: str,
    dry_run: bool = False,
    verbose: bool = False
) -> Dict[str, int]:
    """
    Add front matter to all exported markdown files.

    Args:
        output_dir: Directory containing exported markdown files
        dry_run: If True, don't actually modify files
        verbose: Show detailed progress

    Returns:
        Dictionary with statistics
    """
    output_path = Path(output_dir).expanduser()

    if not output_path.exists():
        print(f"Error: Directory not found: {output_path}")
        return {"error": 1}

    print("Connecting to Notion API...")
    client = create_client()

    print("Building page hierarchy from Notion...")
    roots = build_full_hierarchy(client)

    if not roots:
        print("No pages found in Notion.")
        return {"pages_found": 0}

    # Build mapping from file paths to metadata
    print("Fetching page metadata...")
    path_to_metadata: Dict[Path, PageMetadata] = {}
    for root in roots:
        build_path_to_metadata_map(client, root, output_path, path_to_metadata)

    print(f"Found {len(path_to_metadata)} pages with metadata")

    # Process files
    stats = {
        "files_found": 0,
        "files_updated": 0,
        "files_skipped": 0,
        "files_not_matched": 0
    }

    print(f"\nProcessing files in {output_path}...")

    # Walk all markdown files in output directory
    for md_file in output_path.rglob("*.md"):
        # Skip export_report.md
        if md_file.name == "export_report.md":
            continue

        stats["files_found"] += 1

        if md_file in path_to_metadata:
            metadata = path_to_metadata[md_file]
            if add_frontmatter_to_file(md_file, metadata, dry_run):
                stats["files_updated"] += 1
            else:
                stats["files_skipped"] += 1
        else:
            if verbose:
                print(f"  Not matched: {md_file.relative_to(output_path)}")
            stats["files_not_matched"] += 1

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Add YAML front matter to exported Notion markdown files"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="~/notion",
        help="Directory containing exported markdown files (default: ~/notion)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without modifying files"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    stats = add_frontmatter_to_directory(
        args.directory,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Files found: {stats.get('files_found', 0)}")
    print(f"  Files updated: {stats.get('files_updated', 0)}")
    print(f"  Files skipped (already have frontmatter): {stats.get('files_skipped', 0)}")
    print(f"  Files not matched to Notion pages: {stats.get('files_not_matched', 0)}")


if __name__ == "__main__":
    main()
