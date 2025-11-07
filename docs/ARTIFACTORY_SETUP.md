# UV with Corporate Artifactory - Setup Guide

This guide explains how to configure UV to work with your corporate Artifactory or private PyPI mirror.

## Option 1: UV Configuration File (Recommended)

Edit `.config/uv/uv.toml`:

```toml
# Set your Artifactory URL
index-url = "https://your-artifactory.company.com/artifactory/api/pypi/pypi-virtual/simple"

# Use native TLS for better certificate handling
native-tls = true

# Optional: Add PyPI as fallback
# extra-index-url = ["https://pypi.org/simple"]

# Optional: For self-signed certificates
# trusted-host = ["your-artifactory.company.com"]
```

## Option 2: Environment Variables

Set these environment variables in your shell:

```bash
# Add to ~/.zshrc or ~/.bashrc
export UV_INDEX_URL="https://your-artifactory.company.com/artifactory/api/pypi/pypi-virtual/simple"
export UV_EXTRA_INDEX_URL="https://pypi.org/simple"  # Optional fallback
```

Then reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

## Option 3: pip.conf (Legacy Compatibility)

Edit `pip.conf` in the project root:

```ini
[global]
index-url = https://your-artifactory.company.com/artifactory/api/pypi/pypi-virtual/simple
timeout = 60
retries = 5

[install]
# Optional: Add PyPI as fallback
# extra-index-url = https://pypi.org/simple
```

## Authentication

### Using .netrc (Recommended)

Create or edit `~/.netrc`:

```
machine your-artifactory.company.com
login your-username
password your-api-token
```

Set permissions:
```bash
chmod 600 ~/.netrc
```

### Using Environment Variables

```bash
export UV_HTTP_BASIC_your_artifactory_company_com_USERNAME="your-username"
export UV_HTTP_BASIC_your_artifactory_company_com_PASSWORD="your-api-token"
```

### Using Keyring

UV can use your system keyring:

```bash
# Install keyring support
pip install keyring

# Store credentials
keyring set your-artifactory.company.com your-username
```

Then enable keyring in `.config/uv/uv.toml`:
```toml
keyring-provider = "subprocess"
```

## Troubleshooting

### Certificate Errors

If you see SSL certificate errors:

1. **Use native TLS** (recommended):
   ```bash
   uv pip install --native-tls <package>
   ```
   Or add to `.config/uv/uv.toml`:
   ```toml
   native-tls = true
   ```

2. **Add trusted host**:
   ```toml
   trusted-host = ["your-artifactory.company.com"]
   ```

3. **Use custom CA bundle**:
   ```bash
   export SSL_CERT_FILE=/path/to/company-ca-bundle.crt
   export REQUESTS_CA_BUNDLE=/path/to/company-ca-bundle.crt
   ```

### Connection Timeouts

Increase timeout in `pip.conf`:
```ini
[global]
timeout = 120
retries = 10
```

### Testing Configuration

Test your Artifactory connection:

```bash
# Test with UV
uv pip install --dry-run requests

# Verbose output for debugging
uv pip install -v requests
```

## Verify Setup

After configuration, run:

```bash
# Check UV version
uv --version

# Test installation
make install

# Or manually
source .venv/bin/activate
uv pip install --native-tls -e ".[dev,test,docs]"
```

## Common Artifactory URLs

Your Artifactory URL typically follows these patterns:

- **Virtual Repository**: `https://artifactory.company.com/artifactory/api/pypi/pypi-virtual/simple`
- **Local Repository**: `https://artifactory.company.com/artifactory/api/pypi/pypi-local/simple`
- **Remote Repository**: `https://artifactory.company.com/artifactory/api/pypi/pypi-remote/simple`

Ask your DevOps team for the correct URL.

## Additional Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [Artifactory PyPI Repository](https://www.jfrog.com/confluence/display/JFROG/PyPI+Repositories)
- [Python .netrc Authentication](https://docs.python.org/3/library/netrc.html)
