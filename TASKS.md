# Notion to Markdown Exporter - Task List

## Legend
- [ ] Todo
- [x] Completed
- [?] Pending user approval

## Phase 1: Project Setup

### Documentation
- [x] Create TASKS.md with detailed task breakdown
- [x] Write README.md with API setup instructions
- [x] Write CLAUDE.md for future LLM context

### Environment Setup
- [x] Set up Python virtual environment
- [x] Install notion-client dependency
- [x] Create requirements.txt
- [x] Commit initial project structure

## Phase 2: Core Implementation

### Configuration & Authentication
- [x] Create config.py module for API key handling
  - [x] Support NOTION_TOKEN environment variable
  - [x] Support reading from ~/.ssh/secret.env
  - [x] Add validation and error messages
- [x] Implement Notion client connection
- [x] Test authentication with simple API call

### Page Hierarchy Traversal
- [x] Create hierarchy.py module
- [x] Implement recursive page discovery function
- [x] Build page tree data structure
- [x] Handle child pages vs nested blocks
- [x] Add pagination support for large workspaces
- [x] Commit hierarchy traversal

### Markdown Conversion
- [x] Create markdown_converter.py module
- [x] Implement block-to-markdown converters:
  - [x] Paragraph blocks
  - [x] Heading blocks (h1, h2, h3)
  - [x] Bulleted list items
  - [x] Numbered list items
  - [x] To-do items (checkboxes)
  - [x] Code blocks
  - [x] Quote blocks
  - [x] Callout blocks
  - [x] Divider blocks
  - [x] Toggle blocks
  - [x] Rich text formatting (bold, italic, code, links)
- [x] Handle unsupported blocks gracefully
- [x] Commit markdown converter

### File System Operations
- [x] Create exporter.py module
- [x] Implement folder structure creation logic:
  - [x] Create notion/ root directory
  - [x] Create folders for pages with children
  - [x] Create index.md for parent page content
  - [x] Create .md files for leaf pages
- [x] Implement safe filename generation (sanitize special chars)
- [x] Handle duplicate page names
- [x] Commit file system operations

## Phase 3: Advanced Features

### Dry-Run Mode
- [x] Add dry-run flag to CLI
- [x] Implement hierarchical text preview
- [x] Show what files/folders would be created
- [x] Display tree structure
- [x] Commit dry-run feature

### Non-Exportable Features Report
- [x] Create reporter.py module
- [x] Track unsupported block types
- [x] Track unsupported features in blocks
- [x] Generate report.md with:
  - [x] List of unsupported features
  - [x] Page locations where they occur
  - [x] Suggestions for manual conversion
- [x] Commit reporter module

### Database Export
- [x] Implement database query functionality
- [x] Extract database schema (columns)
- [x] Extract database rows
- [x] Convert to markdown table format
- [x] Handle different property types:
  - [x] Text
  - [x] Number
  - [x] Select/Multi-select
  - [x] Date
  - [x] Person
  - [x] Checkbox
  - [x] URL
  - [x] Email
  - [x] Phone
- [x] Add note about complex properties
- [x] Commit database converter

### Error Handling & Progress
- [x] Add comprehensive try-catch blocks
- [x] Implement logging module
- [x] Add progress bar for exports
- [x] Show current page being processed
- [x] Continue on errors (don't fail entire export)
- [x] Collect and report errors at end
- [x] Commit error handling

## Phase 4: CLI & Polish

### Command-Line Interface
- [x] Create main.py with argparse
- [x] Add arguments:
  - [x] --dry-run: Preview mode
  - [x] --output: Output directory (default: notion/)
  - [x] --verbose: Verbose logging
  - [x] --page-id: Export specific page (optional)
  - [x] --include-databases: Include database exports
- [x] Add help text for all arguments
- [x] Commit CLI implementation

### Testing & Refinement
- [ ] Test with simple page structure
- [ ] Test with nested pages (3+ levels)
- [ ] Test with various block types
- [ ] Test with databases
- [ ] Test error handling
- [ ] Test dry-run mode
- [ ] Fix any bugs discovered
- [ ] Commit bug fixes

### Final Documentation
- [ ] Update README.md with usage examples
- [ ] Add troubleshooting section
- [ ] Add example output
- [ ] Final review and polish
- [ ] Final commit

## Suggested Additional Features (Pending User Approval)

### [?] Incremental Updates
- [ ] Store metadata about last export (timestamps)
- [ ] Compare with Notion's last_edited_time
- [ ] Only export modified pages
- [ ] Add --force flag to override

### [?] Asset Management
- [ ] Download images from Notion
- [ ] Download attached files
- [ ] Create assets/ directory structure
- [ ] Update markdown links to local assets
- [ ] Add --skip-assets flag

### [?] Front Matter Metadata
- [ ] Add YAML front matter to markdown files
- [ ] Include page properties:
  - [ ] Created date
  - [ ] Last modified date
  - [ ] Tags/Categories
  - [ ] Custom properties
- [ ] Make front matter optional via flag

### [?] Configuration File
- [ ] Support .notion-export.yml config file
- [ ] Store default preferences
- [ ] Support ignore patterns (pages to skip)
- [ ] Support custom output templates

### [?] Export Statistics
- [ ] Count total pages exported
- [ ] Count pages with errors
- [ ] List skipped pages
- [ ] Show export duration
- [ ] Display summary at end

### [?] Rate Limiting
- [ ] Add configurable delays between API calls
- [ ] Handle Notion API rate limits gracefully
- [ ] Implement exponential backoff on errors
- [ ] Show rate limit warnings

### [?] Page Filtering
- [ ] Filter by page title pattern
- [ ] Filter by last modified date
- [ ] Filter by tags/properties
- [ ] Add --exclude flag for pages to skip

## Notes

- Each task should result in a git commit when completed
- Update this file after completing each task
- Mark suggested features with [?] until user approves
- Focus on simplicity and clarity in code
- Use type hints throughout for better documentation
