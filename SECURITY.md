# Security Guide

This guide covers secure credential management for the AI Agents Monorepo.

## Credential Management

### Overview

The application supports two methods for managing sensitive credentials like API keys:

1. **Environment Variables** (`.env` file) - Primary method
2. **macOS Keychain** (Optional) - For enhanced local security on macOS

### Environment Variables (Primary Method)

```bash
# Copy the example file
cp .env.example .env

# Edit and add your API key
nano .env
# Add: OPENAI_API_KEY=sk-your-key-here
```

**Note**: Environment files should never be committed to version control. The `.env` file is already in `.gitignore`.

### macOS Keychain (Optional, Local Development Only)

For enhanced security on macOS during local development, you can store your API key in the macOS Keychain instead of the `.env` file:

```bash
# Store your OpenAI API key in macOS Keychain
security add-generic-password -s "ai-agent-demos" -a "openai-api-key" -w
# When prompted, enter your API key

# The 'make run' command will automatically fetch it if OPENAI_API_KEY is not set in .env

# To retrieve the key manually:
security find-generic-password -s "ai-agent-demos" -a "openai-api-key" -w

# To delete the key:
security delete-generic-password -s "ai-agent-demos" -a "openai-api-key"
```

**How It Works**: When you run `make run`, if the `OPENAI_API_KEY` environment variable is not set, it will automatically fetch the key from the macOS Keychain and set it as an environment variable at runtime.

### Supported Credentials

- `openai-api-key` - OpenAI API key for LLM functionality
- Other credentials can be managed similarly

### CI/CD and Production

For CI/CD pipelines and production deployments:

- **CI/CD**: Use GitHub Secrets or similar encrypted secret storage
- **Production**: Use cloud provider secret managers:
  - AWS Secrets Manager
  - Azure Key Vault
  - Databricks Secrets
  - Google Secret Manager

The macOS Keychain integration is designed only for local development convenience.

### Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for configuration
3. **Use macOS Keychain (optional)** for additional local security on macOS
4. **Rotate keys regularly** for production environments
5. **Use least privilege** - only grant necessary permissions
6. **Monitor API usage** to detect unauthorized access

## Context-Based Permissioning

The application implements context-based tool permissioning to prevent data leakage and ensure proper access control. See `shared/utils/security.py` for implementation details.
