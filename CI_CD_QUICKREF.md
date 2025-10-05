# CI/CD Quick Reference Card

## 🚀 Before You Push

```bash
# Run ALL CI checks locally (takes ~2-3 minutes)
make ci-all
```

✅ If all pass → Safe to push  
❌ If any fail → Fix locally before pushing

---

## 🔧 Individual CI Commands

```bash
make ci-install     # Install dependencies (non-interactive)
make ci-lint        # Ruff + Black + MyPy checks
make ci-test        # Tests with coverage XML (80% required)
make ci-security    # Bandit security scan
make ci-build       # Build Python package
```

---

## 🐛 Debugging CI Failures

### Lint Failed in CI?
```bash
make ci-lint        # Run exact CI lint checks
make lint-fix       # Auto-fix formatting issues
make ci-lint        # Verify fixes
```

### Tests Failed in CI?
```bash
make ci-test        # Run exact CI test command
poetry run pytest tests/path/to/test.py -vv  # Debug specific test
```

### Coverage Too Low?
```bash
poetry run pytest --cov=agents --cov=shared --cov-report=html
open htmlcov/index.html  # See what's not covered (red lines)
# Add tests for uncovered code
```

### Security Scan Issues?
```bash
make ci-security
cat bandit-report.json | jq '.results'  # View findings
# Fix high-severity issues or add # nosec comments
```

---

## 📋 Common Workflows

### Before Committing
```bash
make ci-all                           # Run all checks
git add .                             # Stage changes
git commit -m "Your message"          # Commit
git push                              # Push (CI will pass!)
```

### Fixing CI Failures
```bash
# 1. Reproduce locally
make ci-<job>  # e.g., make ci-lint, make ci-test

# 2. Fix the issue
make lint-fix  # For lint issues
# or edit code for test/security issues

# 3. Verify fix
make ci-all

# 4. Push
git commit --amend --no-edit
git push --force-with-lease
```

### Adding New Code
```bash
# 1. Write code
# 2. Write tests (maintain 80% coverage)
# 3. Run checks
make ci-all

# 4. If coverage fails, add more tests
poetry run pytest --cov=agents --cov=shared --cov-report=term-missing

# 5. Push when green
git push
```

---

## 🎯 CI Pipeline Jobs

| Job | Command | What It Does | On Failure |
|-----|---------|--------------|------------|
| **Lint** | `make ci-lint` | Ruff + Black + MyPy | Run `make lint-fix` |
| **Test** | `make ci-test` | Pytest with coverage | Check coverage report |
| **Security** | `make ci-security` | Bandit scan | Review `bandit-report.json` |
| **Build** | `make ci-build` | Poetry build | Check `dist/` artifacts |
| **Deploy** | `make ci-deploy-<env>` | Terraform + ECS | Check AWS logs |

---

## 🔑 Environment Variables

### Local (`.env` file)
```bash
OPENAI_API_KEY=sk-...
DATABRICKS_HOST=https://your-workspace.databricks.com
DATABRICKS_TOKEN=dapi...
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
```

### GitHub Actions (Repository Secrets)
```
OPENAI_API_KEY
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
DATABRICKS_HOST
DATABRICKS_TOKEN
TEAMS_WEBHOOK_URL
```

---

## 💡 Pro Tips

1. **Run `make ci-all` before every push** - Saves time waiting for CI
2. **Use `make lint-fix`** - Auto-fixes most formatting issues
3. **Check coverage locally** - Don't wait for CI to tell you it's too low
4. **Debug with `-vv`** - More verbose test output for debugging
5. **Use `--lf`** - Rerun only last failed tests: `pytest --lf`

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Poetry not found" | `curl -sSL https://install.python-poetry.org \| python3 -` |
| Tests pass locally, fail in CI | Check Python version, env vars, dependencies |
| Coverage XML missing | Use `make ci-test`, not `make test` |
| Lint passes locally, fails in CI | Use `make ci-lint` to match exact CI checks |
| "No module named X" | Run `make ci-install` to reinstall dependencies |

---

## 📚 Full Documentation

For detailed debugging, environment setup, and advanced workflows:

👉 **[CI/CD Integration Guide](docs/CI_CD_INTEGRATION.md)**

---

## ⚡ One-Liner

```bash
make ci-all && git push
```

✅ Checks pass locally → Pushes to remote  
❌ Checks fail → Stays local until fixed

---

**Remember:** What runs in CI should run locally! 🎯
