# Notion to Markdown Exporter - Project Context

## Project Overview

This is a Python-based tool that exports Notion workspace pages to local Markdown files while preserving the hierarchical structure of pages and folders.

## Key Design Decisions

### Why notion-sdk-py Instead of notion2md?

We chose to build on top of the official `notion-sdk-py` library rather than using the pre-built `notion2md` library because:

1. **Better hierarchy support**: notion2md has limited support for child pages and nested structures
2. **Full control**: We need to detect and report unsupported features, which requires low-level access
3. **Custom requirements**: Our specific folder structure logic (index.md for parent pages) isn't supported by existing tools
4. **Simplicity**: Direct API access is actually simpler than working around the limitations of higher-level tools

### Core Architecture

The project is organized into focused modules:

- **config.py**: Handles API token retrieval from environment or ~/.ssh/secret.env
- **hierarchy.py**: Recursive page discovery and tree building
- **markdown_converter.py**: Converts Notion blocks to Markdown strings
- **exporter.py**: File system operations (creating folders, writing files)
- **reporter.py**: Tracks and reports unsupported features
- **main.py**: CLI interface using argparse

### File Structure Logic

The key logic for the file structure is:

1. **Leaf pages** (no children) → `Page Name.md`
2. **Parent pages** (with children) → `Page Name/index.md` + child files
3. All files go into the `notion/` output directory by default

This design allows:
- Clean hierarchical browsing
- Parent page content is preserved in index.md
- Works well with static site generators
- Natural folder organization

### Notion API Fundamentals

#### Authentication
- Requires an Internal Integration token
- Set via `NOTION_TOKEN` environment variable
- Pages must be explicitly shared with the integration

#### API Structure
- **Pages**: Retrieved via `notion.pages.retrieve(page_id)`
- **Blocks**: Retrieved via `notion.blocks.children.list(block_id)`
- **Child pages**: Appear as blocks with `type: "child_page"`
- **Databases**: Queried via `notion.databases.query(database_id)`

#### Important API Details
- Blocks endpoint is paginated (use `has_more` and `next_cursor`)
- Page content is in blocks, not in the page object itself
- Need to recursively fetch blocks that have children
- Unsupported blocks have `type: "unsupported"`
- Rate limit: 3 requests per second

### Block Type Mapping

Common Notion blocks map to Markdown as follows:

```
paragraph → plain text
heading_1 → # Heading
heading_2 → ## Heading
heading_3 → ### Heading
bulleted_list_item → - item
numbered_list_item → 1. item
to_do → - [ ] item (unchecked) or - [x] item (checked)
code → ```language\ncode\n```
quote → > quote text
divider → ---
callout → > 💡 callout text
```

### Rich Text Handling

Notion's rich text is an array of text objects with annotations:

```python
{
    "type": "text",
    "text": {"content": "Hello"},
    "annotations": {
        "bold": true,
        "italic": false,
        "code": false,
        # ...
    },
    "href": "https://..."
}
```

Convert to Markdown:
- bold → `**text**`
- italic → `*text*`
- code → `` `text` ``
- link → `[text](url)`

### Challenges and Solutions

#### Challenge: Filename Sanitization
Pages can have any Unicode characters in titles, but filesystems have restrictions.

**Solution**: Sanitize filenames by:
- Removing/replacing special characters (/, \, :, *, ?, ", <, >, |)
- Handling duplicate names by appending numbers
- Limiting length to avoid filesystem issues

#### Challenge: Unsupported Block Types
Not all Notion features can be represented in Markdown.

**Solution**:
- Convert what we can
- Track unsupported features in a list
- Generate a report at the end
- Include page location for manual review

#### Challenge: Recursive Block Fetching
Blocks can have children (toggles, lists, etc.) requiring recursive fetching.

**Solution**:
- Check `has_children` property on each block
- Recursively fetch children when present
- Use a stack or recursion to handle arbitrary depth

#### Challenge: Database Export
Databases are complex with many property types.

**Solution**:
- Query database for all pages/rows
- Extract properties and convert to table
- Use Markdown table format
- Add note about complex properties that don't convert well

## Development Workflow

1. **Check TASKS.md** for current status and next tasks
2. **Update TASKS.md** after completing each major task
3. **Commit frequently** after each self-contained change
4. **Test incrementally** - don't write everything before testing
5. **Handle errors gracefully** - never crash on a single page error

## Testing Strategy

Since we don't have formal tests yet, manually test with:

1. **Simple page**: Single page with basic text
2. **Nested pages**: Parent with 2-3 child pages
3. **Complex blocks**: Code, lists, quotes, callouts
4. **Databases**: A simple database with various property types
5. **Edge cases**: Empty pages, pages with special characters in names

## Common Gotchas

1. **Page IDs**: Need to remove hyphens from URLs (or the SDK handles it)
2. **Pagination**: Always check `has_more` and use `next_cursor`
3. **Rate limits**: Add small delays between bulk operations
4. **Authentication**: Pages must be shared with integration explicitly
5. **Block children**: Page IDs can be used as block IDs to get content

## Future Enhancement Ideas

See TASKS.md for detailed suggestions marked with [?] for user approval:
- Incremental updates (only export changed pages)
- Asset downloading (images, files)
- Front matter metadata (YAML headers)
- Configuration file support
- Page filtering options

## Code Style Guidelines

- Use type hints throughout (Python 3.7+ style)
- Keep functions focused and small (< 50 lines ideal)
- Use descriptive variable names (no single letters except loop counters)
- Add docstrings to all public functions
- Handle errors explicitly (no bare except clauses)
- Log progress for user feedback

## Dependencies

- **notion-client**: Official Notion SDK for Python
- Standard library only for everything else (no extra dependencies)

## Notion API Version

This project uses Notion API version 2022-06-28 (latest stable as of implementation). The version is set in API request headers.

## Resources

- Notion API Docs: https://developers.notion.com/
- notion-sdk-py GitHub: https://github.com/ramnes/notion-sdk-py
- Notion Block Types: https://developers.notion.com/reference/block
- Markdown Guide: https://www.markdownguide.org/

## Notes for Future Development

- Keep the focus on simplicity - don't over-engineer
- Prioritize the 80% use case - perfect export isn't possible
- Provide good error messages - API failures are common
- Make dry-run mode work perfectly - it builds user confidence
- Generate useful reports - help users handle limitations

## Current Implementation Status

See TASKS.md for the complete checklist. As of project initialization:
- ✅ Project structure and documentation
- ⏳ Core implementation in progress
- ⏳ Advanced features pending
- ⏳ Testing and polish pending
