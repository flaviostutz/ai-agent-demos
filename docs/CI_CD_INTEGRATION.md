# CI/CD Integration Guide

## Overview

This project follows a principle: **"What runs in CI should run locally."** All CI pipeline commands are exposed as Makefile targets, allowing developers to run identical checks on their local machines before pushing code.

## Architecture

```
┌─────────────────────┐
│  Developer Machine  │
│                     │
│  $ make ci-all     │
│  ├─ ci-install     │
│  ├─ ci-lint        │
│  ├─ ci-test        │
│  ├─ ci-security    │
│  └─ ci-build       │
└──────────┬──────────┘
           │
           │ git push
           ▼
┌─────────────────────┐
│  GitHub Actions     │
│  (.github/workflows)│
│                     │
│  $ make ci-all     │
│  ├─ ci-install     │
│  ├─ ci-lint        │
│  ├─ ci-test        │
│  ├─ ci-security    │
│  └─ ci-build       │
└─────────────────────┘
```

Both local and CI environments execute the **same Makefile targets** with **identical flags and configurations**.

## CI Pipeline Jobs

### 1. Lint Job
**Purpose:** Code quality checks (style, formatting, type hints)

**Commands:**
```bash
make ci-lint
```

**What it does:**
- Runs Ruff linter on `agents/`, `shared/`, `tests/`
- Checks Black formatting (no auto-fix)
- Runs MyPy type checker (continues on error)

**Local debugging:**
```bash
# Run lint checks
make ci-lint

# Auto-fix issues
make lint-fix

# Check specific files
poetry run ruff check agents/loan_approval/agent.py
poetry run black --check agents/loan_approval/agent.py
```

### 2. Test Job
**Purpose:** Unit and integration tests with coverage

**Commands:**
```bash
make ci-test
```

**What it does:**
- Runs pytest on `tests/` directory
- Generates coverage XML for Codecov
- Requires 80% coverage minimum
- Outputs verbose test results

**Local debugging:**
```bash
# Run all tests with coverage
make ci-test

# Run specific test file
poetry run pytest tests/agents/test_loan_approval.py -v

# Run specific test
poetry run pytest tests/agents/test_loan_approval.py::test_approved_loan -v

# View coverage report
poetry run pytest --cov=agents --cov=shared --cov-report=html
open htmlcov/index.html
```

### 3. Security Job
**Purpose:** Security vulnerability scanning

**Commands:**
```bash
make ci-security
```

**What it does:**
- Runs Bandit security scanner
- Scans `agents/` and `shared/` directories
- Generates JSON report (`bandit-report.json`)
- Continues on warnings (doesn't fail build)

**Local debugging:**
```bash
# Run security scan
make ci-security

# View detailed report
cat bandit-report.json | jq

# Scan specific file
poetry run bandit agents/loan_approval/agent.py
```

### 4. Build Job
**Purpose:** Package building

**Commands:**
```bash
make ci-build
```

**What it does:**
- Builds Python package with Poetry
- Creates wheel and source distributions
- Outputs to `dist/` directory

**Local debugging:**
```bash
# Build package
make ci-build

# Inspect artifacts
ls -lh dist/
```

### 5. Deploy Jobs (Test, Acceptance, Production)
**Purpose:** Environment-specific deployments

**Commands:**
```bash
make ci-deploy-test          # Deploy to test environment
make ci-deploy-acceptance    # Deploy to acceptance environment
make ci-deploy-prod          # Deploy to production environment
```

**What it does:**
- Authenticates with AWS
- Deploys infrastructure via Terraform
- Updates ECS services
- Runs smoke tests
- Sends deployment notifications

**Local debugging:**
```bash
# Deploy to test environment
make ci-deploy-test

# Check deployment status
aws ecs describe-services --cluster ai-agents-test --services loan-approval

# View logs
aws logs tail /ecs/ai-agents/test/loan-approval --follow
```

## Running All CI Checks Locally

### Quick Start

```bash
# Run all CI checks in one command
make ci-all
```

This will:
1. ✅ Install dependencies (non-interactive mode)
2. ✅ Run lint checks (Ruff, Black, MyPy)
3. ✅ Run tests with coverage
4. ✅ Run security scan
5. ✅ Build package

### Step-by-Step Workflow

```bash
# 1. Install dependencies
make ci-install

# 2. Run lint checks
make ci-lint

# 3. Run tests
make ci-test

# 4. Run security scan
make ci-security

# 5. Build package
make ci-build
```

## Debugging CI Failures

### Scenario 1: Lint Failure in CI

**Problem:** CI lint job fails, but local `make lint` passes.

**Solution:**
```bash
# Run exact CI lint checks
make ci-lint

# Fix formatting issues
make lint-fix

# Verify
make ci-lint
```

### Scenario 2: Test Failure in CI

**Problem:** Tests pass locally but fail in CI.

**Solution:**
```bash
# Run exact CI test command
make ci-test

# Check for environment differences
echo $OPENAI_API_KEY  # Ensure API key is set

# Run with verbose output
poetry run pytest tests/ -vv

# Check for race conditions
poetry run pytest tests/ --count=10  # Run tests 10 times
```

### Scenario 3: Security Scan Issues

**Problem:** Security scan finds vulnerabilities.

**Solution:**
```bash
# Run security scan
make ci-security

# Review findings
cat bandit-report.json | jq '.results'

# Fix high-severity issues
# Review each issue and:
# - Update dependencies
# - Add # nosec comment with justification
# - Refactor code to avoid vulnerability
```

### Scenario 4: Coverage Failure

**Problem:** Coverage drops below 80% threshold.

**Solution:**
```bash
# Generate HTML coverage report
poetry run pytest --cov=agents --cov=shared --cov-report=html

# Open in browser
open htmlcov/index.html

# Identify uncovered lines (highlighted in red)
# Add tests for uncovered code paths
```

## CI vs Local Differences

### CI Targets Use Non-Interactive Flags

**Why:** CI environments don't have terminal input, so Poetry must run without prompts.

```bash
# CI mode (non-interactive)
poetry install --no-interaction --no-root
poetry install --no-interaction

# Local mode (interactive)
poetry install
```

### CI Targets Generate XML/JSON Reports

**Why:** GitHub Actions needs structured output for integrations (Codecov, artifact uploads).

```bash
# CI test (XML coverage for Codecov)
poetry run pytest tests/ -v --cov=agents --cov=shared --cov-report=xml --cov-report=term

# Local test (HTML coverage for browser)
poetry run pytest tests/ -v --cov=agents --cov=shared --cov-report=html
```

### MyPy Continues on Error in CI

**Why:** Type hints are improving gradually; we don't want to block builds on type errors yet.

```bash
# CI lint (continues on MyPy errors)
poetry run mypy agents/ shared/ --ignore-missing-imports || true

# Local lint (stops on MyPy errors)
poetry run mypy agents/ shared/ --ignore-missing-imports
```

## Best Practices

### 1. Pre-Push Validation

Always run CI checks before pushing:
```bash
# Before committing
make ci-all

# If all pass, commit and push
git commit -am "Your commit message"
git push
```

### 2. Fix Issues Locally First

Don't rely on CI to find issues:
```bash
# Run lint + auto-fix
make lint-fix

# Run tests
make ci-test

# Only push if all pass
```

### 3. Use CI Targets for Debugging

If CI fails, reproduce locally:
```bash
# Run exact CI command that failed
make ci-lint   # If lint job failed
make ci-test   # If test job failed
make ci-security  # If security job failed
```

### 4. Check Coverage Before Pushing

```bash
# Generate coverage report
make test-coverage

# Ensure coverage is >= 80%
# Add tests if coverage is low
```

### 5. Keep Makefile and CI in Sync

**Critical:** When updating CI pipeline, always update Makefile targets (or vice versa).

**Bad:**
```yaml
# .github/workflows/ci-cd.yml
- name: Run tests
  run: poetry run pytest tests/ -v --new-flag  # Added --new-flag
```

**Good:**
```makefile
# Makefile
ci-test:
    $(POETRY) run pytest tests/ -v --cov=agents --cov=shared --cov-report=xml --new-flag
```

```yaml
# .github/workflows/ci-cd.yml
- name: Run tests
  run: make ci-test  # Uses updated Makefile target
```

## Environment Variables

### Required for CI

Set in GitHub repository settings (Settings → Secrets and variables → Actions):

```
OPENAI_API_KEY              # OpenAI API key for agent testing
AWS_ACCESS_KEY_ID           # AWS credentials for deployment
AWS_SECRET_ACCESS_KEY       # AWS secret key
DATABRICKS_HOST             # Databricks workspace URL
DATABRICKS_TOKEN            # Databricks API token
TEAMS_WEBHOOK_URL           # MS Teams webhook for notifications
```

### Required for Local

Set in `.env` file:

```bash
# .env
OPENAI_API_KEY=sk-...
DATABRICKS_HOST=https://your-workspace.databricks.com
DATABRICKS_TOKEN=dapi...
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

## Troubleshooting

### Issue: "Poetry not found"

**Solution:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or use pip
pip install poetry

# Verify installation
poetry --version
```

### Issue: "Coverage XML not found"

**Solution:**
```bash
# Ensure you run ci-test (not just test)
make ci-test

# Verify coverage.xml exists
ls -lh coverage.xml
```

### Issue: "Bandit report missing"

**Solution:**
```bash
# Run security scan
make ci-security

# Verify report exists
ls -lh bandit-report.json
```

### Issue: "Tests fail in CI but pass locally"

**Possible causes:**
1. **Environment variables missing** - Check GitHub secrets
2. **Different Python version** - Match CI Python version (3.11)
3. **Cached dependencies** - Clear cache and reinstall
4. **Race conditions** - Tests may be order-dependent

**Solution:**
```bash
# Use exact CI Python version
pyenv install 3.11
pyenv local 3.11

# Clear cache and reinstall
rm -rf .venv
poetry install

# Run tests in random order
poetry run pytest tests/ --random-order
```

## Summary

### Key Benefits of CI/Local Parity

✅ **Faster debugging**: Reproduce CI failures locally  
✅ **Confidence**: Know your code will pass CI before pushing  
✅ **Consistency**: Same commands, flags, and results everywhere  
✅ **Developer experience**: No surprises from CI pipeline  
✅ **Maintainability**: Single source of truth (Makefile)  

### Quick Reference

```bash
# Run all CI checks
make ci-all

# Run individual checks
make ci-lint
make ci-test
make ci-security
make ci-build

# Auto-fix issues
make lint-fix

# Deploy to environments
make ci-deploy-test
make ci-deploy-acceptance
make ci-deploy-prod
```

### Related Documentation

- [Developer Guide](DEVELOPER_GUIDE.md) - Comprehensive development guide
- [Deployment Guide](DEPLOYMENT.md) - Infrastructure and deployment details
- [MLFlow Monitoring](MLFLOW_MONITORING.md) - Model evaluation and monitoring
- [Architecture](ARCHITECTURE.md) - System architecture overview
