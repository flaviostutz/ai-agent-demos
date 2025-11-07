# AI Agents Monorepo

A production-ready monorepo for AI agents with focus on loan processing, built on Databricks, LangGraph, and MLFlow.

## 🏗️ Architecture

This monorepo follows enterprise-grade practices for AI agent development and deployment:

- **Platform Stack**: Databricks, LangGraph, MLFlow, Databricks Mosaic AI
- **Infrastructure**: Terraform CDK for IaaC
- **Observability**: Databricks Mosaic AI monitoring, MLFlow tracking, MS Teams alerts
- **Security**: Context-based permissioning, data leakage prevention
- **CI/CD**: GitHub Actions with automated quality gates

## 📁 Project Structure

```
.
├── agents/                    # AI Agents
│   └── loan-approval/        # Loan approval agent
│       ├── src/              # Agent source code
│       ├── tests/            # Unit and integration tests
│       ├── datasets/         # Ground truth datasets
│       ├── policies/         # Loan policy documents
│       └── Makefile          # Agent-specific build targets
├── shared/                    # Shared libraries
│   ├── models/               # Common data models
│   ├── utils/                # Utility functions
│   └── monitoring/           # Observability helpers
├── infrastructure/            # Infrastructure as Code
│   ├── terraform/            # Terraform CDK configs
│   └── databricks/           # Databricks configurations
├── .github/                   # GitHub Actions workflows
├── docs/                      # Documentation
│   └── developer-guide.md    # Developer onboarding guide
├── Makefile                   # Root-level make targets
└── pyproject.toml            # Python project configuration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [UV](https://github.com/astral-sh/uv) - Fast Python package installer
- Make
- Docker (optional, for local testing)
- Databricks CLI
- Terraform

### Install UV

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Or with Homebrew
brew install uv
```

### Configure Artifactory (Corporate Environment)

If you're using a corporate Artifactory or private PyPI mirror:

1. **Edit `.config/uv/uv.toml`** and update the index URL:
```toml
index-url = "https://your-artifactory.company.com/artifactory/api/pypi/pypi-virtual/simple"
native-tls = true
```

2. **Or edit `pip.conf`** for pip-compatible configuration:
```ini
[global]
index-url = https://your-artifactory.company.com/artifactory/api/pypi/pypi-virtual/simple
```

3. **Set environment variables** for authentication (if needed):
```bash
export UV_INDEX_URL="https://your-artifactory.company.com/artifactory/api/pypi/pypi-virtual/simple"
export UV_EXTRA_INDEX_URL="https://pypi.org/simple"  # Optional fallback
```

### Local Development

1. **Clone and setup**:
```bash
git clone <repository-url>
cd ai-agent-demos
make setup
```

2. **Activate virtual environment**:
```bash
source .venv/bin/activate
```

3. **Run an agent locally**:
```bash
cd agents/loan-approval
make run-local
```

4. **Run tests**:
```bash
make test
```

5. **Check code quality**:
```bash
make lint
```

## 📝 Available Make Targets

### Root Level
- `make setup` - Initial project setup with UV
- `make install` - Install all dependencies with UV
- `make sync` - Sync dependencies to exact versions
- `make lint` - Run linters across all agents
- `make test` - Run all tests
- `make build` - Build all agents
- `make clean` - Clean build artifacts
- `make check-uv` - Verify UV installation

### Agent Level (in agents/*/Makefile)
- `make install` - Install agent dependencies
- `make lint` - Lint agent code
- `make test` - Run agent tests
- `make run-local` - Run agent locally
- `make build` - Build agent
- `make deploy` - Deploy agent
- `make undeploy` - Remove deployment
- `make performance-test` - Run performance tests

## 🔄 Development Workflow

1. **Create a feature branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make changes and test locally**:
```bash
make lint
make test
```

3. **Create a Pull Request**:
   - PR will trigger automated checks
   - Requires at least 1 approval
   - All CI checks must pass

4. **Merge to main**:
   - Automatically deploys to Test environment

5. **Create a release tag**:
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```
   - Automatically deploys to Acceptance and Production

## 🧪 Testing

### Unit Tests
```bash
make test
```

### Integration Tests
```bash
make test-integration
```

### Performance Tests
```bash
cd agents/loan-approval
make performance-test
```

## 📊 Monitoring and Observability

- **MLFlow**: Model tracking and versioning at `/mlruns`
- **Databricks Mosaic AI**: Real-time monitoring and alerts
- **MS Teams**: Automated notifications for failures and alerts

## 🔒 Security

- Context-based tool permissioning prevents data leakage
- Secrets managed via environment variables
- No credentials in code or version control

## 📖 Documentation

See [Developer Guide](docs/developer-guide.md) for detailed instructions on:
- Creating new agents
- Local development setup
- Deployment process
- Troubleshooting

## 🤝 Contributing

1. Follow the PR review process
2. Ensure 80%+ test coverage
3. Pass all lint checks
4. Update documentation as needed

## 📄 License

See LICENSE file for details.
