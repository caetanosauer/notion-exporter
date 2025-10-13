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
- [ ] Implement Notion client connection
- [ ] Test authentication with simple API call

### Page Hierarchy Traversal
- [ ] Create hierarchy.py module
- [ ] Implement recursive page discovery function
- [ ] Build page tree data structure
- [ ] Handle child pages vs nested blocks
- [ ] Add pagination support for large workspaces
- [ ] Commit hierarchy traversal

### Markdown Conversion
- [ ] Create markdown_converter.py module
- [ ] Implement block-to-markdown converters:
  - [ ] Paragraph blocks
  - [ ] Heading blocks (h1, h2, h3)
  - [ ] Bulleted list items
  - [ ] Numbered list items
  - [ ] To-do items (checkboxes)
  - [ ] Code blocks
  - [ ] Quote blocks
  - [ ] Callout blocks
  - [ ] Divider blocks
  - [ ] Toggle blocks
  - [ ] Rich text formatting (bold, italic, code, links)
- [ ] Handle unsupported blocks gracefully
- [ ] Commit markdown converter

### File System Operations
- [ ] Create exporter.py module
- [ ] Implement folder structure creation logic:
  - [ ] Create notion/ root directory
  - [ ] Create folders for pages with children
  - [ ] Create index.md for parent page content
  - [ ] Create .md files for leaf pages
- [ ] Implement safe filename generation (sanitize special chars)
- [ ] Handle duplicate page names
- [ ] Commit file system operations

## Phase 3: Advanced Features

### Dry-Run Mode
- [ ] Add dry-run flag to CLI
- [ ] Implement hierarchical text preview
- [ ] Show what files/folders would be created
- [ ] Display tree structure
- [ ] Commit dry-run feature

### Non-Exportable Features Report
- [ ] Create reporter.py module
- [ ] Track unsupported block types
- [ ] Track unsupported features in blocks
- [ ] Generate report.md with:
  - [ ] List of unsupported features
  - [ ] Page locations where they occur
  - [ ] Suggestions for manual conversion
- [ ] Commit reporter module

### Database Export
- [ ] Implement database query functionality
- [ ] Extract database schema (columns)
- [ ] Extract database rows
- [ ] Convert to markdown table format
- [ ] Handle different property types:
  - [ ] Text
  - [ ] Number
  - [ ] Select/Multi-select
  - [ ] Date
  - [ ] Person
  - [ ] Checkbox
  - [ ] URL
  - [ ] Email
  - [ ] Phone
- [ ] Add note about complex properties
- [ ] Commit database converter

### Error Handling & Progress
- [ ] Add comprehensive try-catch blocks
- [ ] Implement logging module
- [ ] Add progress bar for exports
- [ ] Show current page being processed
- [ ] Continue on errors (don't fail entire export)
- [ ] Collect and report errors at end
- [ ] Commit error handling

## Phase 4: CLI & Polish

### Command-Line Interface
- [ ] Create main.py with argparse
- [ ] Add arguments:
  - [ ] --dry-run: Preview mode
  - [ ] --output: Output directory (default: notion/)
  - [ ] --verbose: Verbose logging
  - [ ] --page-id: Export specific page (optional)
  - [ ] --include-databases: Include database exports
- [ ] Add help text for all arguments
- [ ] Commit CLI implementation

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
