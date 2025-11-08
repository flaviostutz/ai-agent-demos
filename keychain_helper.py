#!/usr/bin/env python3
"""Helper script to manage secrets in macOS Keychain."""

import sys

try:
    import keyring
except ImportError:
    print("Error: keyring library not installed")
    print("Install it with: pip install keyring")
    sys.exit(1)

SERVICE_NAME = "ai-agent-demos"


def store_secret(key: str, value: str) -> None:
    """Store a secret in the keychain."""
    try:
        keyring.set_password(SERVICE_NAME, key, value)
        print(f"✓ Successfully stored '{key}' in macOS Keychain")
    except Exception as e:
        print(f"✗ Error storing secret: {e}")
        sys.exit(1)


def get_secret(key: str) -> str | None:
    """Retrieve a secret from the keychain."""
    try:
        secret = keyring.get_password(SERVICE_NAME, key)
        if secret:
            return secret

        print(f"✗ Secret '{key}' not found in keychain")
        return None
    except Exception as e:
        print(f"✗ Error retrieving secret: {e}")
        return None


def delete_secret(key: str) -> None:
    """Delete a secret from the keychain."""
    try:
        keyring.delete_password(SERVICE_NAME, key)
        print(f"✓ Successfully deleted '{key}' from macOS Keychain")
    except keyring.errors.PasswordDeleteError:
        print(f"✗ Secret '{key}' not found in keychain")
    except Exception as e:
        print(f"✗ Error deleting secret: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the keychain helper."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Store a secret:    python keychain_helper.py set <key> <value>")
        print("  Retrieve a secret: python keychain_helper.py get <key>")
        print("  Delete a secret:   python keychain_helper.py delete <key>")
        print()
        print("Common keys:")
        print("  openai-api-key     - OpenAI API key")
        print("  databricks-token   - Databricks authentication token")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "set" and len(sys.argv) >= 4:
        key = sys.argv[2]
        value = sys.argv[3]
        store_secret(key, value)

    elif command == "get" and len(sys.argv) >= 3:
        key = sys.argv[2]
        secret = get_secret(key)
        if secret:
            print(f"Secret value: {secret}")

    elif command == "delete" and len(sys.argv) >= 3:
        key = sys.argv[2]
        delete_secret(key)

    else:
        print("Invalid command or missing arguments")
        print("Run without arguments to see usage")
        sys.exit(1)


if __name__ == "__main__":
    main()
