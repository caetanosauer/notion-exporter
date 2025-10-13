"""
Notion client wrapper for simplified API access.

This module provides a wrapper around the notion-client SDK with
authentication handling and common operations.
"""

from typing import Optional
from notion_client import Client
from notion_client.errors import APIResponseError
import config


class NotionClientWrapper:
    """Wrapper for the Notion API client with convenience methods."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Notion client.

        Args:
            token: Optional Notion API token. If not provided, will be
                   retrieved from environment or config file.

        Raises:
            config.ConfigError: If token cannot be found or is invalid
        """
        if token is None:
            token = config.get_validated_token()

        self.token = token
        self.client = Client(auth=token)

    def test_connection(self) -> bool:
        """
        Test if the connection and authentication work.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to list users as a simple authentication test
            self.client.users.me()
            return True
        except APIResponseError as e:
            print(f"API Error: {e}")
            return False
        except Exception as e:
            print(f"Connection Error: {e}")
            return False

    def get_bot_info(self) -> dict:
        """
        Get information about the authenticated bot/integration.

        Returns:
            Dictionary with bot information

        Raises:
            APIResponseError: If API request fails
        """
        return self.client.users.me()

    def search_pages(self, query: str = "", page_size: int = 100) -> list:
        """
        Search for pages in the workspace.

        Args:
            query: Optional search query (empty returns all accessible pages)
            page_size: Number of results per page (max 100)

        Returns:
            List of page objects

        Raises:
            APIResponseError: If API request fails
        """
        results = []
        has_more = True
        start_cursor = None

        while has_more:
            response = self.client.search(
                query=query,
                page_size=page_size,
                start_cursor=start_cursor,
                filter={"property": "object", "value": "page"}
            )

            results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return results

    def get_page(self, page_id: str) -> dict:
        """
        Retrieve a page by ID.

        Args:
            page_id: The Notion page ID

        Returns:
            Page object

        Raises:
            APIResponseError: If page not found or not accessible
        """
        return self.client.pages.retrieve(page_id)

    def get_block_children(self, block_id: str, page_size: int = 100) -> list:
        """
        Get all children blocks of a block/page.

        Args:
            block_id: The block or page ID
            page_size: Number of results per page (max 100)

        Returns:
            List of block objects

        Raises:
            APIResponseError: If block not found or not accessible
        """
        results = []
        has_more = True
        start_cursor = None

        while has_more:
            response = self.client.blocks.children.list(
                block_id=block_id,
                page_size=page_size,
                start_cursor=start_cursor
            )

            results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return results

    def get_database(self, database_id: str) -> dict:
        """
        Retrieve a database by ID.

        Args:
            database_id: The Notion database ID

        Returns:
            Database object

        Raises:
            APIResponseError: If database not found or not accessible
        """
        return self.client.databases.retrieve(database_id)

    def query_database(self, database_id: str, page_size: int = 100) -> list:
        """
        Query all entries in a database.

        Args:
            database_id: The Notion database ID
            page_size: Number of results per page (max 100)

        Returns:
            List of page objects (database rows)

        Raises:
            APIResponseError: If database not found or not accessible
        """
        results = []
        has_more = True
        start_cursor = None

        while has_more:
            response = self.client.databases.query(
                database_id=database_id,
                page_size=page_size,
                start_cursor=start_cursor
            )

            results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return results


def create_client(token: Optional[str] = None) -> NotionClientWrapper:
    """
    Factory function to create a Notion client.

    Args:
        token: Optional Notion API token

    Returns:
        NotionClientWrapper instance

    Raises:
        config.ConfigError: If token cannot be found or is invalid
    """
    return NotionClientWrapper(token)


if __name__ == '__main__':
    """Test the Notion client connection."""
    print("Testing Notion API connection...")
    print()

    try:
        client = create_client()
        print("✓ Client initialized")

        # Test connection
        if client.test_connection():
            print("✓ Authentication successful")

            # Get bot info
            bot_info = client.get_bot_info()
            bot_name = bot_info.get("name", "Unknown")
            bot_type = bot_info.get("type", "Unknown")
            print(f"✓ Connected as: {bot_name} (type: {bot_type})")

            # Try to search for pages
            print()
            print("Searching for accessible pages...")
            pages = client.search_pages()
            print(f"✓ Found {len(pages)} accessible page(s)")

            if pages:
                print()
                print("First few pages:")
                for i, page in enumerate(pages[:5], 1):
                    title = "Untitled"
                    if "properties" in page:
                        # Try to get the title from various property types
                        for prop_name, prop_value in page["properties"].items():
                            if prop_value.get("type") == "title":
                                title_array = prop_value.get("title", [])
                                if title_array:
                                    title = title_array[0].get("plain_text", "Untitled")
                                break

                    page_id = page["id"]
                    print(f"  {i}. {title} (ID: {page_id})")

        else:
            print("✗ Authentication failed")

    except config.ConfigError as e:
        print(f"✗ Configuration Error:\n{e}")
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
