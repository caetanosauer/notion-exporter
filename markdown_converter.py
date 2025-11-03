"""
Markdown converter for Notion blocks.

This module converts Notion block objects into Markdown format,
handling various block types and rich text formatting.
"""

from typing import List, Dict, Any, Tuple, Optional


class UnsupportedFeature:
    """Represents an unsupported feature encountered during conversion."""

    def __init__(self, block_type: str, feature: str, block_id: str):
        self.block_type = block_type
        self.feature = feature
        self.block_id = block_id

    def __repr__(self) -> str:
        return f"Unsupported: {self.block_type}.{self.feature} (block: {self.block_id})"


class MarkdownConverter:
    """Converts Notion blocks to Markdown format."""

    def __init__(self, track_skipped_databases: bool = True):
        self.unsupported_features: List[UnsupportedFeature] = []
        self.track_skipped_databases = track_skipped_databases

    def add_unsupported(self, block_type: str, feature: str, block_id: str):
        """Record an unsupported feature."""
        self.unsupported_features.append(
            UnsupportedFeature(block_type, feature, block_id)
        )

    def convert_rich_text(self, rich_text_array: List[Dict]) -> str:
        """
        Convert Notion rich text array to Markdown.

        Args:
            rich_text_array: Array of rich text objects

        Returns:
            Markdown formatted string
        """
        if not rich_text_array:
            return ""

        result = []

        for text_obj in rich_text_array:
            text_type = text_obj.get("type", "text")

            if text_type == "text":
                content = text_obj.get("text", {}).get("content", "")
                link = text_obj.get("text", {}).get("link")
            elif text_type == "mention":
                # Handle mentions (user, page, database, date)
                mention = text_obj.get("mention", {})
                mention_type = mention.get("type")

                if mention_type == "user":
                    content = f"@{text_obj.get('plain_text', 'user')}"
                elif mention_type == "page":
                    content = text_obj.get('plain_text', '[page]')
                elif mention_type == "database":
                    content = text_obj.get('plain_text', '[database]')
                elif mention_type == "date":
                    content = text_obj.get('plain_text', '[date]')
                else:
                    content = text_obj.get('plain_text', '[mention]')
                link = None
            elif text_type == "equation":
                # LaTeX equations - use inline code as fallback
                expression = text_obj.get("equation", {}).get("expression", "")
                content = f"${expression}$"
                link = None
            else:
                content = text_obj.get("plain_text", "")
                link = None

            # Apply annotations (formatting)
            annotations = text_obj.get("annotations", {})

            if annotations.get("code"):
                content = f"`{content}`"
            if annotations.get("bold"):
                content = f"**{content}**"
            if annotations.get("italic"):
                content = f"*{content}*"
            if annotations.get("strikethrough"):
                content = f"~~{content}~~"

            # Handle links
            href = text_obj.get("href") or (link.get("url") if link else None)
            if href:
                # If it's already formatted with code/bold/italic, wrap the markdown
                content = f"[{content}]({href})"

            result.append(content)

        return "".join(result)

    def convert_paragraph(self, block: Dict) -> str:
        """Convert a paragraph block to Markdown."""
        paragraph = block.get("paragraph", {})
        rich_text = paragraph.get("rich_text", [])
        text = self.convert_rich_text(rich_text)
        return text

    def convert_heading(self, block: Dict, level: int) -> str:
        """Convert a heading block to Markdown."""
        heading_key = f"heading_{level}"
        heading = block.get(heading_key, {})
        rich_text = heading.get("rich_text", [])
        text = self.convert_rich_text(rich_text)
        return f"{'#' * level} {text}"

    def convert_bulleted_list_item(self, block: Dict) -> str:
        """Convert a bulleted list item to Markdown."""
        item = block.get("bulleted_list_item", {})
        rich_text = item.get("rich_text", [])
        text = self.convert_rich_text(rich_text)
        return f"- {text}"

    def convert_numbered_list_item(self, block: Dict, number: int = 1) -> str:
        """Convert a numbered list item to Markdown."""
        item = block.get("numbered_list_item", {})
        rich_text = item.get("rich_text", [])
        text = self.convert_rich_text(rich_text)
        return f"{number}. {text}"

    def convert_to_do(self, block: Dict) -> str:
        """Convert a to-do item to Markdown checkbox."""
        todo = block.get("to_do", {})
        rich_text = todo.get("rich_text", [])
        checked = todo.get("checked", False)
        text = self.convert_rich_text(rich_text)
        checkbox = "[x]" if checked else "[ ]"
        return f"- {checkbox} {text}"

    def convert_toggle(self, block: Dict) -> str:
        """Convert a toggle block to Markdown (as bold text)."""
        toggle = block.get("toggle", {})
        rich_text = toggle.get("rich_text", [])
        text = self.convert_rich_text(rich_text)
        # Toggles don't have a direct Markdown equivalent
        # Use bold text as a compromise
        return f"**{text}**"

    def convert_code(self, block: Dict) -> str:
        """Convert a code block to Markdown."""
        code = block.get("code", {})
        rich_text = code.get("rich_text", [])
        language = code.get("language", "")

        # Get the code text (no formatting needed inside code blocks)
        code_text = "".join([
            text_obj.get("plain_text", "")
            for text_obj in rich_text
        ])

        return f"```{language}\n{code_text}\n```"

    def convert_quote(self, block: Dict) -> str:
        """Convert a quote block to Markdown."""
        quote = block.get("quote", {})
        rich_text = quote.get("rich_text", [])
        text = self.convert_rich_text(rich_text)
        return f"> {text}"

    def convert_callout(self, block: Dict) -> str:
        """Convert a callout block to Markdown blockquote."""
        callout = block.get("callout", {})
        rich_text = callout.get("rich_text", [])
        icon = callout.get("icon", {})

        # Get icon emoji if available
        icon_str = ""
        if icon.get("type") == "emoji":
            icon_str = icon.get("emoji", "")

        text = self.convert_rich_text(rich_text)
        return f"> {icon_str} {text}".strip()

    def convert_divider(self, block: Dict) -> str:
        """Convert a divider to Markdown horizontal rule."""
        return "---"

    def convert_table_row(self, block: Dict) -> List[str]:
        """
        Convert a table row to list of cell contents.

        Args:
            block: Table row block

        Returns:
            List of cell contents as strings
        """
        table_row = block.get("table_row", {})
        cells = table_row.get("cells", [])

        return [self.convert_rich_text(cell) for cell in cells]

    def convert_table(self, block: Dict, rows: List[Dict]) -> str:
        """
        Convert a table block with its rows to Markdown table.

        Args:
            block: Table block
            rows: List of table_row blocks

        Returns:
            Markdown table string
        """
        if not rows:
            return ""

        table = block.get("table", {})
        has_column_header = table.get("has_column_header", False)
        has_row_header = table.get("has_row_header", False)

        # Convert all rows
        all_rows = [self.convert_table_row(row) for row in rows]

        if not all_rows:
            return ""

        # Determine column count
        col_count = max(len(row) for row in all_rows)

        # Pad rows to have same column count
        for row in all_rows:
            while len(row) < col_count:
                row.append("")

        result = []

        # If first row is header, format it specially
        if has_column_header and all_rows:
            header = all_rows[0]
            result.append("| " + " | ".join(header) + " |")
            result.append("|" + "|".join(["---"] * col_count) + "|")
            data_rows = all_rows[1:]
        else:
            # No header, add empty header
            result.append("| " + " | ".join([f"Column {i+1}" for i in range(col_count)]) + " |")
            result.append("|" + "|".join(["---"] * col_count) + "|")
            data_rows = all_rows

        # Add data rows
        for row in data_rows:
            result.append("| " + " | ".join(row) + " |")

        return "\n".join(result)

    def convert_block(self, block: Dict, list_counter: Optional[Dict[str, int]] = None) -> Tuple[str, bool]:
        """
        Convert a single Notion block to Markdown.

        Args:
            block: Notion block object
            list_counter: Dictionary to track numbered list positions

        Returns:
            Tuple of (markdown_string, is_supported)
        """
        if list_counter is None:
            list_counter = {}

        block_type = block.get("type")
        block_id = block.get("id", "unknown")

        if block_type == "paragraph":
            return self.convert_paragraph(block), True

        elif block_type == "heading_1":
            return self.convert_heading(block, 1), True

        elif block_type == "heading_2":
            return self.convert_heading(block, 2), True

        elif block_type == "heading_3":
            return self.convert_heading(block, 3), True

        elif block_type == "bulleted_list_item":
            return self.convert_bulleted_list_item(block), True

        elif block_type == "numbered_list_item":
            # Track list position
            if "numbered" not in list_counter:
                list_counter["numbered"] = 1
            else:
                list_counter["numbered"] += 1

            md = self.convert_numbered_list_item(block, list_counter["numbered"])
            return md, True

        elif block_type == "to_do":
            return self.convert_to_do(block), True

        elif block_type == "toggle":
            return self.convert_toggle(block), True

        elif block_type == "code":
            return self.convert_code(block), True

        elif block_type == "quote":
            return self.convert_quote(block), True

        elif block_type == "callout":
            return self.convert_callout(block), True

        elif block_type == "divider":
            return self.convert_divider(block), True

        elif block_type == "child_page":
            # Child pages are handled separately in hierarchy
            return "", True

        elif block_type == "child_database":
            # Child databases are handled separately
            if self.track_skipped_databases:
                self.add_unsupported("child_database", "not_exported", block_id)
            return "", True

        elif block_type == "table":
            # Tables need their row children, will be handled specially
            return "", True

        elif block_type == "table_row":
            # Table rows are handled as part of table
            return "", True

        elif block_type == "image":
            # Handle images
            image = block.get("image", {})
            image_type = image.get("type")

            if image_type == "external":
                url = image.get("external", {}).get("url", "")
            elif image_type == "file":
                url = image.get("file", {}).get("url", "")
            else:
                url = ""

            caption = image.get("caption", [])
            caption_text = self.convert_rich_text(caption) if caption else "image"

            if url:
                return f"![{caption_text}]({url})", True
            else:
                self.add_unsupported("image", "no_url", block_id)
                return f"[Image: {caption_text}]", False

        elif block_type == "file":
            # Handle file attachments
            file = block.get("file", {})
            file_type = file.get("type")

            if file_type == "external":
                url = file.get("external", {}).get("url", "")
            elif file_type == "file":
                url = file.get("file", {}).get("url", "")
            else:
                url = ""

            caption = file.get("caption", [])
            caption_text = self.convert_rich_text(caption) if caption else "file"

            if url:
                return f"[{caption_text}]({url})", True
            else:
                return f"[File: {caption_text}]", False

        elif block_type == "bookmark":
            bookmark = block.get("bookmark", {})
            url = bookmark.get("url", "")
            caption = bookmark.get("caption", [])
            caption_text = self.convert_rich_text(caption) if caption else url

            if url:
                return f"[{caption_text}]({url})", True
            else:
                return "[Bookmark]", False

        elif block_type == "equation":
            equation = block.get("equation", {})
            expression = equation.get("expression", "")
            return f"$$\n{expression}\n$$", True

        elif block_type == "unsupported":
            self.add_unsupported("unsupported", "unknown", block_id)
            return "[Unsupported block]", False

        else:
            # Unknown block type
            self.add_unsupported(block_type, "unknown_type", block_id)
            return f"[Unsupported: {block_type}]", False

    def convert_blocks(self, blocks: List[Dict]) -> str:
        """
        Convert a list of Notion blocks to Markdown.

        Args:
            blocks: List of Notion block objects

        Returns:
            Markdown string
        """
        result = []
        list_counter = {}

        i = 0
        while i < len(blocks):
            block = blocks[i]
            block_type = block.get("type")

            # Handle tables specially (need to collect rows)
            if block_type == "table":
                table_block = block
                rows = []

                # Collect following table_row blocks
                j = i + 1
                while j < len(blocks) and blocks[j].get("type") == "table_row":
                    rows.append(blocks[j])
                    j += 1

                md = self.convert_table(table_block, rows)
                if md:
                    result.append(md)

                i = j  # Skip the rows we just processed
                list_counter = {}  # Reset list counter after table
                continue

            # Reset numbered list counter if we're not in a numbered list
            if block_type != "numbered_list_item":
                list_counter.pop("numbered", None)

            # Convert block
            md, is_supported = self.convert_block(block, list_counter)

            if md:
                result.append(md)

            i += 1

        return "\n\n".join(result)


if __name__ == '__main__':
    """Test the markdown converter."""
    # Example test blocks
    test_blocks = [
        {
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": "Test Heading"}, "annotations": {}}]
            }
        },
        {
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": "This is "}, "annotations": {}},
                    {"type": "text", "text": {"content": "bold"}, "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": " and "}, "annotations": {}},
                    {"type": "text", "text": {"content": "italic"}, "annotations": {"italic": True}},
                ]
            }
        },
    ]

    converter = MarkdownConverter()
    markdown = converter.convert_blocks(test_blocks)

    print("Test Markdown Conversion:")
    print("=" * 50)
    print(markdown)
    print()
    print(f"Unsupported features: {len(converter.unsupported_features)}")
