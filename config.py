"""
Configuration module for Notion API token handling.

This module provides functionality to retrieve the Notion API token from:
1. NOTION_TOKEN environment variable
2. ~/.ssh/secret.env file
"""

import os
from pathlib import Path
from typing import Optional


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


def load_env_file(file_path: Path) -> dict:
    """
    Load environment variables from a file.

    Args:
        file_path: Path to the environment file

    Returns:
        Dictionary of environment variables
    """
    env_vars = {}

    if not file_path.exists():
        return env_vars

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value
    except Exception as e:
        raise ConfigError(f"Error reading {file_path}: {e}")

    return env_vars


def get_notion_token() -> str:
    """
    Retrieve the Notion API token from environment or secret file.

    Checks in order:
    1. NOTION_TOKEN environment variable
    2. NOTION_TOKEN in ~/.ssh/secret.env file

    Returns:
        The Notion API token

    Raises:
        ConfigError: If token cannot be found or retrieved
    """
    # Check environment variable first
    token = os.environ.get('NOTION_TOKEN')

    if token:
        return token

    # Check ~/.ssh/secret.env file
    secret_file = Path.home() / '.ssh' / 'secret.env'

    if secret_file.exists():
        env_vars = load_env_file(secret_file)
        token = env_vars.get('NOTION_TOKEN')

        if token:
            return token

    # Token not found
    raise ConfigError(
        "Notion API token not found!\n\n"
        "Please set your token using one of these methods:\n\n"
        "1. Environment variable:\n"
        "   export NOTION_TOKEN='your_token_here'\n\n"
        "2. Create ~/.ssh/secret.env with:\n"
        "   NOTION_TOKEN=your_token_here\n\n"
        "To get a token:\n"
        "1. Go to https://www.notion.com/my-integrations\n"
        "2. Create a new integration\n"
        "3. Copy the 'Internal Integration Secret'\n"
        "4. Share your pages with the integration"
    )


def validate_token(token: str) -> bool:
    """
    Validate that a token looks correct (basic format check).

    Args:
        token: The token to validate

    Returns:
        True if token appears valid, False otherwise
    """
    if not token:
        return False

    # Notion tokens typically start with "secret_" and are quite long
    if not token.startswith('secret_'):
        return False

    if len(token) < 20:
        return False

    return True


def get_validated_token() -> str:
    """
    Get and validate the Notion API token.

    Returns:
        The validated Notion API token

    Raises:
        ConfigError: If token is missing or appears invalid
    """
    token = get_notion_token()

    if not validate_token(token):
        raise ConfigError(
            "The Notion token appears to be invalid.\n"
            "Tokens should start with 'secret_' and be quite long.\n"
            "Please check your token and try again."
        )

    return token


if __name__ == '__main__':
    """Test the config module."""
    try:
        token = get_validated_token()
        print(f"✓ Token found: {token[:20]}... (length: {len(token)})")
    except ConfigError as e:
        print(f"✗ Error: {e}")
