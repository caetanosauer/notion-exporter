Let's ultrathink and write a python script that connects with the notion API to export all my notes into local markdown files. Requirements:
## Dealing with hierarchies of notes and folders
- I want the whole hierarchy of pages to be reflected into a local directory `notion/`.
- If there are pages that contain other pages inside them, create a folder for the parent page and put the note contents into an `index.md` file.
- Pages that do not have any nested pages inside them should just be named after the title of the page with the `.md` suffix.
## Non-exportable features
- If there are features that cannot be exported to Markdown, please create a separate report with what they are and in what page they occur.
- For databases, just create a markdown table.
## Other requirements
- The script has a dry-run mode in which it lists all notes that would be created, in a hierarchical text representation.
- The API keys are not stored in any file but set via environment variable, or read from the file `~/.ssh/secret.env`
## Documentation
- Write a documentation on how to run the script and get API keys (search the web to find out) in README.md
- Write CLAUDE.md to describe the project to further LLM sessions
## The plan
- Create a detailed TASKS.md file with all individual building blocks, and use that to keep track of your progress
- This folder has a fresly initialized git repo; make sure every step is committed to it, including the TASKS.md updates
- Suggest ther functionality and requirements that you think are essential and mark them explicitly in TASKS.md for my review and approval
