# Notion to Markdown Exporter

A Python script that exports your Notion workspace pages to local Markdown files, preserving the page hierarchy and structure.

## Features

- **Hierarchical Export**: Preserves your Notion page hierarchy in local folders
- **Smart File Structure**: Parent pages with children become folders with `index.md`
- **Dry-Run Mode**: Preview what will be exported before running
- **Database Support**: Exports Notion databases as Markdown tables
- **Unsupported Features Report**: Generates a report of features that can't be exported
- **Progress Tracking**: Shows real-time progress during export
- **Error Handling**: Continues export even if individual pages fail

## Prerequisites

- Python 3.7 or higher
- A Notion account
- A Notion integration token (see setup below)

## Getting a Notion API Token

### Step 1: Create a Notion Integration

1. Go to [https://www.notion.com/my-integrations](https://www.notion.com/my-integrations)
2. Click **"+ New integration"**
3. Give it a name (e.g., "Markdown Exporter")
4. Select the workspace you want to export from
5. Click **"Submit"**
6. Copy the **"Internal Integration Secret"** - this is your API token

### Step 2: Share Pages with Your Integration

**Important**: Your integration can only access pages that have been explicitly shared with it.

To share pages:
1. Open the page you want to export in Notion
2. Click the **"•••"** menu in the top-right corner
3. Scroll down to **"Add connections"**
4. Search for and select your integration
5. Repeat for all pages you want to export (or share the top-level parent page to include all children)

### Step 3: Store Your API Token Securely

You have two options:

#### Option A: Environment Variable (Recommended)
```bash
export NOTION_TOKEN="your_secret_token_here"
```

Add this to your `~/.bashrc`, `~/.zshrc`, or `~/.bash_profile` to make it permanent.

#### Option B: Secret File
Create a file at `~/.ssh/secret.env`:
```bash
NOTION_TOKEN=your_secret_token_here
```

**Never commit your token to version control!**

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Export

Export all accessible pages to the `notion/` directory:
```bash
python3 main.py
```

### Dry-Run Mode

Preview what will be exported without creating files:
```bash
python3 main.py --dry-run
```

This will show a hierarchical tree structure of all pages that would be exported.

### Custom Output Directory

Specify a different output location:
```bash
python3 main.py --output ~/Documents/my-notes
```

### Export Specific Page

Export only a specific page and its children:
```bash
python3 main.py --page-id abc123def456
```

To find a page ID:
1. Open the page in Notion
2. Click "Share" → "Copy link"
3. The page ID is the part after the last `/` and before `?` (32 characters)
   - Example: `https://notion.so/My-Page-abc123def456` → `abc123def456`

### Include Databases

Export databases as Markdown tables:
```bash
python3 main.py --include-databases
```

### Verbose Output

Show detailed logging:
```bash
python3 main.py --verbose
```

## Output Structure

The exporter creates the following structure:

```
notion/
├── Simple Page.md              # Leaf page (no children)
├── Parent Page/                 # Page with children becomes a folder
│   ├── index.md                # Parent page content
│   ├── Child Page 1.md
│   └── Child Page 2/
│       ├── index.md
│       └── Nested Child.md
└── unsupported_features_report.md  # Report of non-exportable features
```

## Supported Block Types

The exporter supports most common Notion block types:

- **Text Blocks**: Paragraphs, headings (H1-H3), quotes
- **Lists**: Bulleted lists, numbered lists, to-do lists
- **Code**: Code blocks with syntax highlighting
- **Formatting**: Bold, italic, strikethrough, inline code, links
- **Structure**: Dividers, callouts, toggles
- **Data**: Tables (simple tables), databases (as markdown tables)
- **Media**: Images (links preserved), files (links preserved)

## Unsupported Features

Some Notion features cannot be perfectly represented in Markdown:

- Advanced database views (board, calendar, gallery, timeline)
- Equations (LaTeX)
- Embedded content (videos, maps, etc.)
- Synced blocks (content will be duplicated)
- Advanced formatting (colors, highlights)
- Comments and discussions
- Page icons and covers

When unsupported features are encountered, they will be documented in `unsupported_features_report.md`.

## Troubleshooting

### "Unauthorized" Error
- Make sure your `NOTION_TOKEN` is set correctly
- Verify you've shared the pages with your integration

### "Object not found" Error
- The page ID doesn't exist or hasn't been shared with your integration
- Check that you've shared the page (see "Share Pages with Your Integration" above)

### Missing Pages
- Only pages explicitly shared with your integration will be exported
- Share parent pages to include all their children automatically

### Rate Limiting
- The Notion API has rate limits (3 requests per second)
- The exporter handles this automatically with delays

## Development

To contribute or modify the exporter:

1. See `TASKS.md` for the development roadmap
2. See `CLAUDE.md` for project context and architecture
3. Run tests (when available): `python3 -m pytest`

## Project Structure

```
.
├── main.py                 # CLI entry point
├── config.py              # Configuration and API token handling
├── hierarchy.py           # Page hierarchy traversal
├── markdown_converter.py  # Block to markdown conversion
├── exporter.py           # File system operations
├── reporter.py           # Unsupported features reporting
├── requirements.txt      # Python dependencies
├── TASKS.md             # Development task list
├── CLAUDE.md            # Project context for LLMs
└── README.md            # This file
```

## License

This project is provided as-is for personal use. Use at your own risk.

## Acknowledgments

- Built using the official [notion-sdk-py](https://github.com/ramnes/notion-sdk-py)
- Inspired by [notion2md](https://github.com/echo724/notion2md)
