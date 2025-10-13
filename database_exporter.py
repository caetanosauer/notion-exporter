"""
Database exporter module for converting Notion databases to Markdown tables.

This module handles querying Notion databases and converting them to
Markdown table format.
"""

from typing import List, Dict, Any, Optional
from notion_client import NotionClientWrapper


def extract_property_value(prop: Dict, prop_type: str) -> str:
    """
    Extract a simple string value from a Notion property.

    Args:
        prop: Property object
        prop_type: Property type

    Returns:
        String representation of the property value
    """
    try:
        if prop_type == "title":
            title_array = prop.get("title", [])
            if title_array:
                return title_array[0].get("plain_text", "")
            return ""

        elif prop_type == "rich_text":
            text_array = prop.get("rich_text", [])
            if text_array:
                return " ".join([t.get("plain_text", "") for t in text_array])
            return ""

        elif prop_type == "number":
            num = prop.get("number")
            return str(num) if num is not None else ""

        elif prop_type == "select":
            select = prop.get("select")
            return select.get("name", "") if select else ""

        elif prop_type == "multi_select":
            multi = prop.get("multi_select", [])
            return ", ".join([s.get("name", "") for s in multi])

        elif prop_type == "date":
            date = prop.get("date")
            if date:
                start = date.get("start", "")
                end = date.get("end")
                if end:
                    return f"{start} → {end}"
                return start
            return ""

        elif prop_type == "people":
            people = prop.get("people", [])
            names = []
            for person in people:
                name = person.get("name")
                if name:
                    names.append(name)
            return ", ".join(names)

        elif prop_type == "checkbox":
            checked = prop.get("checkbox", False)
            return "✓" if checked else ""

        elif prop_type == "url":
            url = prop.get("url")
            return url if url else ""

        elif prop_type == "email":
            email = prop.get("email")
            return email if email else ""

        elif prop_type == "phone_number":
            phone = prop.get("phone_number")
            return phone if phone else ""

        elif prop_type == "status":
            status = prop.get("status")
            return status.get("name", "") if status else ""

        elif prop_type == "formula":
            formula = prop.get("formula", {})
            formula_type = formula.get("type")
            if formula_type == "string":
                return formula.get("string", "")
            elif formula_type == "number":
                num = formula.get("number")
                return str(num) if num is not None else ""
            elif formula_type == "boolean":
                return "Yes" if formula.get("boolean") else "No"
            elif formula_type == "date":
                date = formula.get("date", {})
                return date.get("start", "")
            return ""

        elif prop_type == "relation":
            # Relations are complex, just show count
            relations = prop.get("relation", [])
            return f"{len(relations)} item(s)"

        elif prop_type == "rollup":
            rollup = prop.get("rollup", {})
            rollup_type = rollup.get("type")
            if rollup_type == "number":
                num = rollup.get("number")
                return str(num) if num is not None else ""
            elif rollup_type == "array":
                array = rollup.get("array", [])
                return f"{len(array)} item(s)"
            return ""

        elif prop_type == "created_time":
            return prop.get("created_time", "")

        elif prop_type == "created_by":
            user = prop.get("created_by", {})
            return user.get("name", "")

        elif prop_type == "last_edited_time":
            return prop.get("last_edited_time", "")

        elif prop_type == "last_edited_by":
            user = prop.get("last_edited_by", {})
            return user.get("name", "")

        elif prop_type == "files":
            files = prop.get("files", [])
            if files:
                names = []
                for file in files:
                    name = file.get("name", "file")
                    names.append(name)
                return ", ".join(names)
            return ""

        else:
            return f"[{prop_type}]"

    except Exception as e:
        return f"[Error: {e}]"


def database_to_markdown_table(
    client: NotionClientWrapper,
    database_id: str,
    max_rows: Optional[int] = None
) -> str:
    """
    Convert a Notion database to a Markdown table.

    Args:
        client: Notion client wrapper
        database_id: Database ID
        max_rows: Optional maximum number of rows to export

    Returns:
        Markdown table string
    """
    try:
        # Get database schema
        database = client.get_database(database_id)
        properties = database.get("properties", {})

        # Get column names and types
        columns = []
        column_types = {}

        for prop_name, prop_info in properties.items():
            prop_type = prop_info.get("type")
            columns.append(prop_name)
            column_types[prop_name] = prop_type

        if not columns:
            return "_Empty database_"

        # Query database for all rows
        rows = client.query_database(database_id)

        if max_rows:
            rows = rows[:max_rows]

        # Build table
        lines = []

        # Header row
        header = "| " + " | ".join(columns) + " |"
        lines.append(header)

        # Separator row
        separator = "|" + "|".join(["---"] * len(columns)) + "|"
        lines.append(separator)

        # Data rows
        for row in rows:
            row_properties = row.get("properties", {})
            values = []

            for col_name in columns:
                if col_name in row_properties:
                    prop = row_properties[col_name]
                    prop_type = column_types[col_name]
                    value = extract_property_value(prop, prop_type)
                    # Escape pipes in values
                    value = value.replace("|", "\\|")
                    values.append(value)
                else:
                    values.append("")

            row_line = "| " + " | ".join(values) + " |"
            lines.append(row_line)

        # Add note if truncated
        if max_rows and len(rows) == max_rows:
            lines.append("")
            lines.append(f"_Table truncated to {max_rows} rows_")

        return "\n".join(lines)

    except Exception as e:
        return f"_Error exporting database: {e}_"


def export_database_to_file(
    client: NotionClientWrapper,
    database_id: str,
    output_path: str,
    max_rows: Optional[int] = None
) -> bool:
    """
    Export a database to a Markdown file.

    Args:
        client: Notion client wrapper
        database_id: Database ID
        output_path: Output file path
        max_rows: Optional maximum number of rows

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get database info
        database = client.get_database(database_id)
        title_array = database.get("title", [])
        title = "Untitled Database"
        if title_array:
            title = title_array[0].get("plain_text", "Untitled Database")

        # Convert to markdown table
        table = database_to_markdown_table(client, database_id, max_rows)

        # Create content with title
        content = f"# {title}\n\n{table}\n"

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"Error exporting database: {e}")
        return False


if __name__ == '__main__':
    """Test the database exporter."""
    from notion_client import create_client

    print("Database Exporter Test")
    print("=" * 60)
    print()

    try:
        client = create_client()

        # Search for databases
        print("Searching for databases...")
        response = client.client.search(
            filter={"property": "object", "value": "database"}
        )

        databases = response.get("results", [])
        print(f"Found {len(databases)} database(s)")

        if databases:
            print()
            print("Databases:")
            for i, db in enumerate(databases[:5], 1):
                title_array = db.get("title", [])
                title = "Untitled"
                if title_array:
                    title = title_array[0].get("plain_text", "Untitled")

                db_id = db["id"]
                print(f"  {i}. {title} (ID: {db_id})")

            print()
            print("To export a database, call:")
            print(f"  database_to_markdown_table(client, 'database_id')")

    except Exception as e:
        print(f"Error: {e}")
