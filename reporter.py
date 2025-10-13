"""
Reporter module for generating reports about unsupported features.

This module collects information about features that couldn't be exported
and generates a comprehensive report for manual review.
"""

from typing import List, Dict, Set
from pathlib import Path
from collections import defaultdict
from markdown_converter import UnsupportedFeature
from hierarchy import PageNode


class ExportReport:
    """Generates reports about the export process."""

    def __init__(self):
        self.unsupported_features: List[UnsupportedFeature] = []
        self.page_mapping: Dict[str, str] = {}  # page_id -> page_title

    def add_unsupported_features(
        self,
        features: List[UnsupportedFeature],
        page_id: str,
        page_title: str
    ):
        """
        Add unsupported features from a page.

        Args:
            features: List of unsupported features
            page_id: Page ID
            page_title: Page title
        """
        self.unsupported_features.extend(features)
        self.page_mapping[page_id] = page_title

    def generate_report(self) -> str:
        """
        Generate a markdown report of unsupported features.

        Returns:
            Markdown formatted report
        """
        if not self.unsupported_features:
            return self._generate_success_report()

        # Group features by type
        by_type = defaultdict(list)
        for feature in self.unsupported_features:
            key = f"{feature.block_type}.{feature.feature}"
            by_type[key].append(feature)

        # Generate report
        lines = [
            "# Unsupported Features Report",
            "",
            "This report lists Notion features that could not be fully exported to Markdown.",
            "",
            f"**Total unsupported features:** {len(self.unsupported_features)}",
            "",
            "---",
            "",
        ]

        # Summary section
        lines.extend([
            "## Summary by Feature Type",
            "",
        ])

        for feature_type in sorted(by_type.keys()):
            count = len(by_type[feature_type])
            lines.append(f"- **{feature_type}**: {count} occurrence(s)")

        lines.extend(["", "---", ""])

        # Detailed section
        lines.extend([
            "## Detailed Breakdown",
            "",
        ])

        for feature_type in sorted(by_type.keys()):
            features = by_type[feature_type]
            lines.extend([
                f"### {feature_type}",
                "",
                f"**Occurrences:** {len(features)}",
                "",
            ])

            # Group by page
            by_page = defaultdict(list)
            for feature in features:
                # Try to find page title
                # Note: block_id might not be a page_id, it's the block's own ID
                by_page["Unknown Page"].append(feature.block_id)

            for page, block_ids in by_page.items():
                lines.append(f"**{page}:**")
                for block_id in block_ids[:5]:  # Limit to first 5
                    lines.append(f"- Block ID: `{block_id}`")
                if len(block_ids) > 5:
                    lines.append(f"- ... and {len(block_ids) - 5} more")
                lines.append("")

        # Recommendations section
        lines.extend([
            "---",
            "",
            "## Recommendations",
            "",
            self._get_recommendations(),
        ])

        return "\n".join(lines)

    def _generate_success_report(self) -> str:
        """Generate a report when everything was exported successfully."""
        return "\n".join([
            "# Export Report",
            "",
            "All pages were exported successfully!",
            "",
            "No unsupported features were encountered during the export process.",
        ])

    def _get_recommendations(self) -> str:
        """Get recommendations for handling unsupported features."""
        return """### How to Handle Unsupported Features

Notion has many rich features that don't have direct Markdown equivalents. Here's how to handle them:

#### Unsupported Block Types

- **Databases (advanced views)**: Databases are exported as simple Markdown tables. Board, calendar, gallery, and timeline views cannot be represented in Markdown. Consider exporting these separately from the Notion UI.

- **Embedded Content**: Videos, maps, and other embedded content appear as links. Download these manually if needed.

- **Synced Blocks**: Content from synced blocks is duplicated in each location. You may want to manually deduplicate this content.

- **Equations**: LaTeX equations are preserved with `$equation$` or `$$equation$$` syntax. Ensure your Markdown renderer supports LaTeX.

#### Rich Formatting

- **Colors and Highlights**: Text colors and background highlights are not supported in standard Markdown and are lost during export.

- **Page Icons and Covers**: These are not exported. Consider adding them manually if they're important.

- **Comments**: Comments and discussions are not included in the export. Review important comments in Notion before exporting.

#### Mentions

- **User Mentions**: Converted to `@username` format
- **Page Links**: Converted to plain text page names
- **Date Mentions**: Converted to plain text dates

#### What to Do

1. Review the blocks listed above in your original Notion pages
2. Manually export or copy content that's critical
3. For databases, consider using Notion's CSV export for data preservation
4. Test your Markdown files in your target renderer (e.g., static site generator)

### Need More Features?

If you need better support for specific block types, please open an issue on the project repository.
"""

    def save_report(self, output_path: Path) -> bool:
        """
        Save the report to a file.

        Args:
            output_path: Path where report should be saved

        Returns:
            True if successful, False otherwise
        """
        try:
            report = self.generate_report()

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)

            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False


def generate_feature_report(
    output_dir: Path,
    unsupported_features: List[UnsupportedFeature],
    page_nodes: List[PageNode] = None
) -> bool:
    """
    Generate and save an unsupported features report.

    Args:
        output_dir: Directory where report should be saved
        unsupported_features: List of unsupported features
        page_nodes: Optional list of page nodes for context

    Returns:
        True if successful, False otherwise
    """
    reporter = ExportReport()

    # Add features (without page context for now)
    if unsupported_features:
        reporter.unsupported_features = unsupported_features

    # Save report
    report_path = output_dir / "export_report.md"
    return reporter.save_report(report_path)


if __name__ == '__main__':
    """Test the reporter module."""

    # Create some test unsupported features
    test_features = [
        UnsupportedFeature("image", "no_url", "block_123"),
        UnsupportedFeature("image", "no_url", "block_456"),
        UnsupportedFeature("equation", "complex", "block_789"),
        UnsupportedFeature("unsupported", "unknown", "block_abc"),
    ]

    reporter = ExportReport()
    reporter.unsupported_features = test_features

    report = reporter.generate_report()

    print("Test Report:")
    print("=" * 60)
    print(report)
