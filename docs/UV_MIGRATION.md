# UV Migration Guide

This project has been migrated from pip/setuptools to [UV](https://github.com/astral-sh/uv), a fast Python package installer and resolver written in Rust.

## Why UV?

- **10-100x faster** than pip for installing packages
- **Deterministic** dependency resolution
- **Compatible** with existing Python packaging standards
- **Drop-in replacement** for pip in most cases
- **Better error messages** and conflict resolution

## What Changed?

### 1. Build System
- **Before**: `setuptools` + `wheel`
- **After**: `hatchling` (recommended by UV)

### 2. pyproject.toml
- Changed `build-system` to use `hatchling`
- Moved dev dependencies to `[tool.uv]` section
- Removed `[tool.setuptools.packages.find]` (handled by hatchling)

### 3. Makefile
- All `pip` commands replaced with `uv pip`
- All direct tool commands (`pytest`, `black`, etc.) prefixed with `uv run`
- Added `check-uv` target to verify UV installation
- Virtual environment is now `.venv` (UV default) instead of `venv`

### 4. GitHub Actions
- Added UV installation step to all workflows
- Removed pip cache (UV handles caching internally)
- All commands now activate `.venv` and use UV

### 5. .gitignore
- Added `.uv/` directory (UV cache)
- Added `uv.lock` (UV lock file, if generated)

## Installation

### Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv

# Or with Homebrew
brew install uv
```

### Project Setup

```bash
# Clone repository
git clone <repo-url>
cd ai-agent-demos

# Setup project (creates .venv and installs dependencies)
make setup

# Activate virtual environment
source .venv/bin/activate

# Verify installation
make check-uv
```

## Migration for Existing Developers

If you already have the project set up with the old system:

### 1. Remove old virtual environment
```bash
rm -rf venv/
```

### 2. Install UV
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Re-setup project
```bash
make setup
```

### 4. Activate new virtual environment
```bash
source .venv/bin/activate
```

### 5. Verify everything works
```bash
make test
make lint
```

## UV Command Equivalents

| Old Command | New Command |
|-------------|-------------|
| `pip install package` | `uv pip install package` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip install -e .` | `uv pip install -e .` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |
| `python -m pytest` | `uv run pytest` |
| `python script.py` | `uv run python script.py` |

## Common Tasks

### Install dependencies
```bash
make install
```

### Add a new dependency
```bash
# Edit pyproject.toml to add dependency
# Then sync
uv pip install -e ".[dev,test,docs]"
```

### Run tests
```bash
make test
# or
uv run pytest
```

### Run linters
```bash
make lint
# or
uv run ruff check .
uv run black --check .
```

### Format code
```bash
make format
# or
uv run black .
```

## Troubleshooting

### UV not found
```bash
# Ensure UV is in your PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or for zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Wrong Python version
```bash
# UV respects pyproject.toml requires-python
# Ensure you have Python 3.9+ installed
python3 --version

# If UV tries to download Python and fails, use system Python:
uv venv --python $(which python3)
```

### Certificate/TLS errors
If you see errors like "invalid peer certificate: UnknownIssuer":

```bash
# Option 1: Use native TLS (respects system certificates)
uv pip install --native-tls -e ".[dev,test,docs]"

# Option 2: Configure UV to trust your corporate certificates
export UV_NATIVE_TLS=1
export SSL_CERT_FILE=/path/to/your/ca-bundle.crt

# Option 3: Fallback to pip if UV doesn't work in your environment
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test,docs]"
```

### PyPI 403 Forbidden errors
If you're behind a corporate proxy/firewall:

```bash
# Configure proxy
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

# Or use pip as fallback
pip install -e ".[dev,test,docs]"
```

### Dependencies not resolving
```bash
# Clear UV cache
uv cache clean

# Re-install
make install
```

### Virtual environment issues
```bash
# Remove and recreate
rm -rf .venv
uv venv --python $(which python3)
source .venv/bin/activate
make install
```

### Fallback to pip
If UV doesn't work in your environment, the project still supports pip:

```bash
# Create venv with pip
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev,test,docs]"

# Run commands normally (without uv run prefix)
pytest
black .
ruff check .
```

## Performance Comparison

Approximate installation times for this project:

| Tool | Initial Install | Cached Install |
|------|----------------|----------------|
| pip | ~60 seconds | ~30 seconds |
| UV | ~6 seconds | ~2 seconds |

*Times measured on M1 MacBook Pro*

## Additional Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV Announcement](https://astral.sh/blog/uv)
- [Python Packaging with UV](https://docs.astral.sh/uv/)

## Rollback (if needed)

If you need to rollback to the old system:

```bash
git revert <migration-commit-hash>
rm -rf .venv/
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev,test]"
```

## Support

For issues related to UV migration:
1. Check this document
2. Review [UV documentation](https://github.com/astral-sh/uv)
3. Open an issue in the repository

For general project issues, follow the standard support process.
