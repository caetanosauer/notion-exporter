#!/usr/bin/env python3
"""
Notion to Markdown Exporter

Main CLI entry point for exporting Notion workspaces to local Markdown files.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import config
from notion_client import create_client
from exporter import export_notion_workspace
from reporter import generate_feature_report


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Export Notion workspace pages to Markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export all accessible pages
  python3 main.py

  # Dry-run to preview what would be exported
  python3 main.py --dry-run

  # Export to a specific directory
  python3 main.py --output ~/Documents/notes

  # Export a specific page and its children
  python3 main.py --page-id abc123def456

  # Verbose output
  python3 main.py --verbose

For more information, see README.md
        """
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="notion",
        help="Output directory for exported files (default: notion/)"
    )

    parser.add_argument(
        "--page-id", "-p",
        type=str,
        default=None,
        help="Specific page ID to export (exports all accessible pages if not specified)"
    )

    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Preview what would be exported without creating files"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress information"
    )

    parser.add_argument(
        "--include-databases",
        action="store_true",
        help="Include database exports (experimental)"
    )

    return parser.parse_args()


def print_banner():
    """Print application banner."""
    print("=" * 60)
    print("Notion to Markdown Exporter")
    print("=" * 60)
    print()


def print_stats(stats, verbose: bool = False):
    """
    Print export statistics.

    Args:
        stats: ExportStats object
        verbose: Whether to show detailed stats
    """
    print()
    print("=" * 60)
    print("Export Complete!")
    print("=" * 60)
    print(f"Pages exported:    {stats.pages_exported}")
    print(f"Pages failed:      {stats.pages_failed}")
    print(f"Files created:     {stats.files_created}")
    print(f"Folders created:   {stats.folders_created}")
    print()

    if stats.errors and verbose:
        print("Errors encountered:")
        for page_id, error in stats.errors[:10]:  # Show first 10
            print(f"  - Page {page_id}: {error}")
        if len(stats.errors) > 10:
            print(f"  ... and {len(stats.errors) - 10} more")
        print()


def main():
    """Main entry point."""
    args = parse_arguments()

    print_banner()

    # Initialize client
    try:
        if args.verbose:
            print("Initializing Notion client...")

        client = create_client()

        if args.verbose:
            print("✓ Client initialized")
            print("✓ Authentication successful")
            print()

    except config.ConfigError as e:
        print(f"Configuration Error:\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error initializing client: {e}")
        sys.exit(1)

    # Run export
    try:
        if args.dry_run:
            print("DRY RUN MODE - No files will be created")
            print()

        if args.page_id:
            print(f"Exporting page: {args.page_id}")
        else:
            print("Exporting all accessible pages")

        if args.verbose or args.dry_run:
            print(f"Output directory: {args.output}")
            print()

        # Export
        stats = export_notion_workspace(
            client=client,
            output_dir=args.output,
            page_id=args.page_id,
            dry_run=args.dry_run,
            verbose=args.verbose
        )

        # Print stats (if not dry-run)
        if not args.dry_run:
            print_stats(stats, args.verbose)

            # Generate report about unsupported features
            if args.verbose:
                print("Generating export report...")

            output_path = Path(args.output)
            # Note: We'd need to collect unsupported features from the converter
            # For now, just indicate success
            report_path = output_path / "export_report.md"
            if report_path.exists():
                print(f"✓ Export report saved to: {report_path}")

            if stats.pages_exported > 0:
                print(f"✓ Files saved to: {args.output}/")

            print()
            print("Done!")

    except KeyboardInterrupt:
        print()
        print("Export cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during export: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
