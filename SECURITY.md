# Security Guide

This guide covers secure credential management for the AI Agents Monorepo.

## macOS Keychain Integration

### Overview

The application integrates with macOS Keychain to securely store sensitive credentials like API keys. This is more secure than storing them in environment files because:

- **Encrypted Storage**: Credentials are stored in the system keychain with encryption
- **No Plain Text Files**: API keys are not stored in `.env` files that could be accidentally committed
- **Access Control**: macOS Keychain provides system-level access control
- **Automatic Retrieval**: The application automatically retrieves credentials when needed

### Quick Start

#### Using Make (Recommended)

```bash
# Set your OpenAI API key securely
make set-openai-key

# Verify the key is stored (displays the key)
make get-openai-key

# Remove the key from keychain
make delete-openai-key
```

#### Using the Helper Script Directly

```bash
# Set a secret
python3 keychain_helper.py set openai-api-key sk-your-actual-key-here

# Get a secret
python3 keychain_helper.py get openai-api-key

# Delete a secret
python3 keychain_helper.py delete openai-api-key
```

#### Using UV

```bash
# Set your OpenAI API key securely with UV
uv run python3 -c "import keyring; import getpass; key = getpass.getpass('Enter OpenAI API key: '); keyring.set_password('ai-agent-demos', 'openai-api-key', key); print('✓ Stored')"

# Or use the helper script with UV
uv run python3 keychain_helper.py set openai-api-key sk-your-actual-key-here
```

### How It Works

The application checks for credentials in this priority order:

1. **macOS Keychain** (highest priority) - Retrieved using the `keyring` library
2. **Environment Variable** - Falls back to `OPENAI_API_KEY` from `.env` file
3. **Default Value** - Uses test default if neither is available

### Supported Credentials

The keychain can store any credential. Common keys used:

- `openai-api-key` - OpenAI API key for LLM functionality
- `databricks-token` - Databricks authentication token (for future use)

### Configuration

The keychain service name is: **`ai-agent-demos`**

All secrets are stored under this service name in macOS Keychain. You can view them in the Keychain Access app:

1. Open **Keychain Access** app
2. Search for `ai-agent-demos`
3. Double-click to view/manage stored secrets

### Fallback to Environment Files

If you prefer not to use Keychain, you can still use environment files:

```bash
# Copy the example file
cp .env.example .env

# Edit and add your API key
nano .env
# Add: OPENAI_API_KEY=sk-your-key-here
```

**Note**: Environment files should never be committed to version control. The `.env` file is already in `.gitignore`.

### CI/CD and Production

For CI/CD pipelines and production deployments:

- **CI/CD**: Use GitHub Secrets or similar encrypted secret storage
- **Production**: Use cloud provider secret managers:
  - AWS Secrets Manager
  - Azure Key Vault
  - Databricks Secrets
  - Google Secret Manager

The application's keychain integration is primarily for local development on macOS.

### Security Best Practices

1. **Never commit API keys** to version control
2. **Use Keychain for local development** on macOS
3. **Rotate keys regularly** for production environments
4. **Use least privilege** - only grant necessary permissions
5. **Monitor API usage** to detect unauthorized access

### Troubleshooting

#### "Keyring not found" error

```bash
# Install keyring with UV
uv pip install keyring

# Or with pip
pip install keyring
```

#### "Permission denied" when accessing keychain

macOS may prompt you to allow access. Click "Allow" when prompted.

#### Clear and reset keychain entry

```bash
# Delete existing entry
make delete-openai-key

# Set new value
make set-openai-key
```

### Implementation Details

The keychain integration is implemented in:

- **`shared/utils/keychain.py`** - Core keychain utilities
- **`agents/loan_approval/src/config.py`** - Configuration with keychain support
- **`keychain_helper.py`** - CLI helper for manual keychain management

For more details, see the source code in these files.
