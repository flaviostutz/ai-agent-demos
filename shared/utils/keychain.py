"""Keychain utilities for secure credential storage on macOS."""

import os
from typing import Optional

import keyring

from shared.monitoring.logger import get_logger

logger = get_logger(__name__)

# Service name for keychain storage
KEYCHAIN_SERVICE_NAME = "ai-agent-demos"


def get_secret(key: str, fallback_env_var: Optional[str] = None) -> Optional[str]:
    """Retrieve a secret from macOS Keychain with optional environment variable fallback.

    Args:
        key: The key/account name for the secret in the keychain
        fallback_env_var: Optional environment variable to check if keychain lookup fails

    Returns:
        The secret value or None if not found

    """
    try:
        # Try to get from keychain first
        secret = keyring.get_password(KEYCHAIN_SERVICE_NAME, key)
        if secret:
            logger.info(f"Retrieved secret '{key}' from keychain")
            return secret

        logger.debug(f"Secret '{key}' not found in keychain")

    except Exception as e:
        logger.warning(f"Error accessing keychain for '{key}': {e}")

    # Fallback to environment variable if provided
    if fallback_env_var:
        env_value = os.getenv(fallback_env_var)
        if env_value:
            logger.info(f"Using fallback environment variable '{fallback_env_var}' for '{key}'")
            return env_value

    return None


def set_secret(key: str, value: str) -> bool:
    """Store a secret in macOS Keychain.

    Args:
        key: The key/account name for the secret in the keychain
        value: The secret value to store

    Returns:
        True if successful, False otherwise

    """
    try:
        keyring.set_password(KEYCHAIN_SERVICE_NAME, key, value)
        logger.info(f"Successfully stored secret '{key}' in keychain")
        return True
    except Exception as e:
        logger.error(f"Error storing secret '{key}' in keychain: {e}")
        return False


def delete_secret(key: str) -> bool:
    """Delete a secret from macOS Keychain.

    Args:
        key: The key/account name for the secret in the keychain

    Returns:
        True if successful, False otherwise

    """
    try:
        keyring.delete_password(KEYCHAIN_SERVICE_NAME, key)
        logger.info(f"Successfully deleted secret '{key}' from keychain")
        return True
    except keyring.errors.PasswordDeleteError:
        logger.warning(f"Secret '{key}' not found in keychain (already deleted or never existed)")
        return False
    except Exception as e:
        logger.error(f"Error deleting secret '{key}' from keychain: {e}")
        return False
