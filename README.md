# AI Agent Demos - Enterprise AI Agent Platform

A production-ready monorepo for building, deploying, and managing AI agents using LangGraph, Databricks, and enterprise-grade infrastructure.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/flaviostutz/ai-agent-demos.git
cd ai-agent-demos

# Set up development environment
make dev-setup

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run the loan approval agent locally
make dev
```

Visit http://localhost:8000/docs for the interactive API documentation.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development](#development)
- [Testing](#testing)
- [CI/CD Integration](#cicd-integration)
- [Deployment](#deployment)
- [Creating New Agents](#creating-new-agents)
- [Contributing](#contributing)

## ✨ Features

### Agent Capabilities
- **Loan Approval Agent**: Automated loan decision-making with risk assessment
- **RAG (Retrieval Augmented Generation)**: Document-based decision making using Chroma vector store
- **LangGraph Integration**: Stateful, multi-step agent workflows
- **Security & Permissioning**: Context-based access control and PII masking

### Development Experience
- **Monorepo Architecture**: Multiple agents and shared libraries in one place
- **Local Development**: Run agents locally with hot-reload
- **Comprehensive Testing**: Unit tests, integration tests, and performance tests
- **Code Quality**: Automated linting (Ruff, Black, MyPy), pre-commit hooks
- **Makefiles**: Consistent build/test/deploy commands across platforms
- **CI/CD Parity**: Run exact same CI checks locally - `make ci-all` before pushing

### Production-Ready Infrastructure
- **Multi-Environment**: Automated deployment to test, acceptance, and production
- **AWS Infrastructure**: ECS Fargate, ALB, VPC, ECR - fully managed via Terraform
- **Databricks Integration**: MLFlow tracking, experiment management, and Mosaic AI monitoring
- **Observability**: MLFlow metrics, CloudWatch logs, OpenTelemetry tracing
- **Model Evaluation**: Automated performance testing with drift detection
- **CI/CD**: GitHub Actions pipelines for lint, test, and deployment
- **Monitoring & Alerting**: MS Teams notifications for errors and performance issues

### Quality & Security
- **80% Test Coverage**: Comprehensive test suite with pytest
- **Performance Testing**: Automated agent performance validation
- **Security Scanning**: Bandit security checks in CI pipeline
- **Data Leakage Prevention**: Automatic PII masking and context filtering
- **Pull Request Reviews**: Automated checks for code quality and coverage

## 🏗️ Architecture

```
┌─────────────────┐
│   API Gateway   │
│   (AWS ALB)     │
└────────┬────────┘
         │
    ┌────▼────┐
    │   ECS   │
    │ Fargate │
    └────┬────┘
         │
    ┌────▼─────────────────────┐
    │  Agent Container (API)   │
    │  ┌──────────────────┐   │
    │  │  LangGraph Agent │   │
    │  │  - Validation    │   │
    │  │  - RAG Retrieval │   │
    │  │  - Risk Analysis │   │
    │  │  - Decision      │   │
    │  └──────────────────┘   │
    └──┬───────────┬───────┬──┘
       │           │       │
┌──────▼──┐  ┌────▼───┐  ┌▼────────┐
│ Chroma  │  │ MLFlow │  │  Teams  │
│ Vector  │  │Tracking│  │ Alerts  │
│  Store  │  │Dataset │  │         │
│         │  │ Eval   │  │         │
└─────────┘  └────────┘  └─────────┘
                 │
         ┌───────▼────────┐
         │  Databricks    │
         │  Workspace     │
         │  - Experiments │
         │  - Model Reg   │
         │  - Mosaic AI   │
         └────────────────┘
```

## 📁 Project Structure

```
ai-agent-demos/
├── agents/                      # Agent implementations
│   └── loan_approval/
│       ├── agent.py            # LangGraph agent logic
│       ├── api.py              # FastAPI REST API
│       ├── Dockerfile          # Container image
│       └── __init__.py
├── shared/                      # Shared libraries
│   ├── logging_utils.py        # Logging with tracing
│   ├── metrics.py              # Prometheus metrics
│   ├── security.py             # Security & permissioning
│   ├── config.py               # Configuration management
│   ├── alerting.py             # MS Teams integration
│   └── mlflow_tracking.py      # MLFlow integration
├── tests/                       # Test suite
│   ├── agents/                 # Agent-specific tests
│   ├── shared/                 # Shared library tests
│   ├── performance/            # Performance tests
│   └── conftest.py            # Pytest fixtures
├── infrastructure/              # Infrastructure as Code
│   ├── terraform/
│   │   ├── main.tf            # Terraform configuration
│   │   ├── networking.tf      # VPC, subnets, security groups
│   │   ├── ecs.tf             # ECS cluster, services
│   │   └── environments/      # Environment-specific configs
│   └── Makefile
├── config/                      # Configuration files
│   ├── config.yaml            # Default configuration
│   ├── config.test.yaml       # Test environment
│   └── config.prod.yaml       # Production environment
├── scripts/                     # Utility scripts
│   ├── generate_loan_docs.py  # Generate PDF documents
│   ├── load_documents.py      # Load docs to vector store
│   └── create_agent.sh        # Create new agent template
├── data/                        # Data files
│   ├── documents/              # PDF rule documents
│   └── chroma/                 # Vector store persistence
├── docs/                        # Documentation
│   ├── DEVELOPER_GUIDE.md
│   ├── DEPLOYMENT.md
│   ├── ARCHITECTURE.md
│   └── CREATING_AGENTS.md
├── .github/
│   └── workflows/              # GitHub Actions
│       ├── ci-cd.yml          # Main CI/CD pipeline
│       └── pr-checks.yml      # Pull request checks
├── pyproject.toml              # Python dependencies
├── Makefile                    # Development commands
└── README.md                   # This file
```

## 🛠️ Getting Started

### Prerequisites

- Python 3.11+
- Poetry (package manager)
- Docker (for containerization)
- AWS CLI (for deployment)
- Terraform (for infrastructure)
- OpenAI API key

### Installation

1. **Clone and setup:**
   ```bash
   git clone https://github.com/flaviostutz/ai-agent-demos.git
   cd ai-agent-demos
   make setup
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your keys:
   # - OPENAI_API_KEY
   # - DATABRICKS_HOST
   # - DATABRICKS_TOKEN
   # - TEAMS_WEBHOOK_URL
   ```

3. **Generate loan rule documents:**
   ```bash
   make generate-docs
   ```

4. **Load documents to vector store:**
   ```bash
   make load-docs
   ```

5. **Run the agent locally:**
   ```bash
   make dev
   ```

## 💻 Development

### Available Make Commands

```bash
make help              # Show all available commands
make install           # Install dependencies
make lint              # Run linting checks
make lint-fix          # Fix linting issues
make test              # Run tests
make test-coverage     # Run tests with coverage report
make evaluate          # Evaluate agent on test dataset
make evaluate-agent    # Evaluate specific agent
make evaluate-drift    # Check for model drift
make dev               # Run agent API locally with hot-reload
make build             # Build (lint + test)
make clean             # Clean build artifacts
make create-agent      # Create new agent from template
```

### Running CI Checks Locally

Run the **exact same checks** that run in the CI pipeline:

```bash
# Run all CI checks locally (lint, test, security, build)
make ci-all

# Run individual CI checks
make ci-lint           # Linting checks (Ruff, Black, MyPy)
make ci-test           # Tests with coverage XML
make ci-security       # Security scan with Bandit
make ci-build          # Build package with Poetry

# Install dependencies (CI mode - non-interactive)
make ci-install
```

**Why use CI targets?**
- **Reproduce CI failures**: If tests fail in GitHub Actions, run `make ci-all` locally to debug
- **Pre-push validation**: Catch issues before pushing to remote
- **Identical environment**: Same flags and configurations as CI pipeline
- **Faster feedback**: No waiting for CI to detect issues

**Example workflow:**
```bash
# Before pushing changes
make ci-all

# If lint fails, fix issues
make lint-fix

# If tests fail, debug specific tests
make ci-test

# Once all checks pass, commit and push
git commit -am "Fix: resolved lint issues"
git push
```

### Model Evaluation & Monitoring

This project uses **MLFlow** and **Databricks** for comprehensive monitoring and evaluation. See [MLFlow Monitoring Guide](docs/MLFLOW_MONITORING.md) for details.

```bash
# Evaluate agent on test dataset
make evaluate

# Evaluate specific agent and dataset
make evaluate-agent AGENT_NAME=loan_approval DATASET=my_test_set

# Check for performance drift
make evaluate-drift BASELINE=baseline_v1 CURRENT=current_month

# View evaluation results in MLFlow UI
mlflow ui --port 5000
```

**Evaluation Features:**
- Automated accuracy, precision, recall, F1-score calculation
- Latency measurement (avg, p95, p99)
- Drift detection against baseline datasets
- Cost tracking (token usage, API costs)
- Confusion matrix analysis
- Results logged to MLFlow/Databricks

### Running Tests

```bash
# Run all tests
make test

# Run with coverage (requires 80%)
make test-coverage

# Run tests for specific agent
make test-agent AGENT_NAME=loan_approval

# Run performance tests
make performance-test AGENT_NAME=loan_approval
```

### Code Quality

```bash
# Run linting
make lint

# Auto-fix issues
make lint-fix

# Security scan
make security-scan
```

## 🧪 Testing

### Test Structure

- **Unit Tests**: `tests/agents/` and `tests/shared/`
- **Integration Tests**: `tests/integration/`
- **Performance Tests**: `tests/performance/`
- **Coverage Requirement**: 80% minimum

### Example Test

```python
def test_loan_approval(sample_loan_request_data, security_context):
    request = LoanRequest(**sample_loan_request_data)
    agent = LoanApprovalAgent(security_context=security_context)
    
    decision = agent.process_request(request)
    
    assert decision.outcome in ["approved", "disapproved", "additional_info_needed"]
    assert decision.risk_score is not None
```

## � CI/CD Integration

### Running CI Checks Locally

**Run the exact same checks that run in the CI pipeline:**

```bash
# Run all CI checks (lint, test, security, build)
make ci-all

# Run individual checks
make ci-lint           # Linting (Ruff, Black, MyPy)
make ci-test           # Tests with coverage XML
make ci-security       # Security scan (Bandit)
make ci-build          # Build package
```

**Why use CI targets?**
- ✅ **Reproduce CI failures** locally before pushing
- ✅ **Faster feedback** - catch issues before CI runs
- ✅ **Identical environment** - same flags/configs as GitHub Actions
- ✅ **Pre-push validation** - ensure code will pass CI

**Example workflow:**
```bash
# Before pushing changes
make ci-all

# If lint fails, fix issues
make lint-fix

# Once all checks pass, push
git push
```

**📚 Complete Guide:** See [CI/CD Integration Guide](docs/CI_CD_INTEGRATION.md) for detailed debugging steps, environment variables, and troubleshooting.

## �🚢 Deployment

### Environments

- **Test**: Automated deployment on push to `develop` branch
- **Acceptance**: Automated deployment on push to `main` branch  
- **Production**: Manual deployment on release tags

### Deploy Commands

```bash
# Deploy to test
make deploy ENV=test

# Deploy to acceptance
make deploy ENV=acceptance

# Deploy to production (requires approval)
make deploy ENV=prod

# Undeploy
make undeploy ENV=test
```

### Infrastructure Setup

```bash
cd infrastructure

# Initialize Terraform
make init ENV=test

# Plan changes
make plan ENV=test

# Apply changes
make deploy ENV=test
```

## 🔧 Creating New Agents

Use the agent template to quickly create a new agent:

```bash
make create-agent AGENT_NAME=my_new_agent
```

This creates:
- Agent implementation skeleton
- FastAPI REST API
- Test structure
- Configuration template

See [docs/CREATING_AGENTS.md](docs/CREATING_AGENTS.md) for detailed instructions.

## 📊 Observability

### Metrics

Access Prometheus metrics at: `/metrics` endpoint

Key metrics:
- `agent_requests_total` - Total requests by agent and status
- `agent_request_duration_seconds` - Request duration histogram
- `agent_errors_total` - Total errors by type
- `agent_token_usage_total` - LLM token consumption

### Logs

- **Local**: Console logs with structured format
- **Production**: CloudWatch Logs with log groups per agent

### Tracing

OpenTelemetry tracing integrated with:
- Request ID tracking
- Span creation for agent operations
- Performance insights

### Alerts

MS Teams alerts for:
- High-risk loan approvals
- Agent errors
- Performance degradation
- Deployment notifications

## 🔒 Security

### Features

- **Context-based Permissions**: Role-based access control
- **PII Masking**: Automatic redaction of sensitive data
- **Data Domain Filtering**: Document access based on user permissions
- **Tool Access Control**: Granular permission for agent tools
- **Secrets Management**: AWS Secrets Manager for sensitive configuration

### Security Context

```python
context = SecurityContext(
    user_id="user123",
    roles=["loan_officer"],
    permissions={"tool:loan_approval", "pii_access"},
    allowed_data_domains={"public", "internal"}
)
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. **Run CI checks locally**: `make ci-all`
4. Create a pull request
5. Automated checks will run (same as your local checks)
6. Wait for code review

**Tip:** Always run `make ci-all` before pushing to catch issues early!

## 📚 Documentation

- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Comprehensive development guide
- [Architecture](docs/ARCHITECTURE.md) - System architecture and design decisions
- [Creating Agents](docs/CREATING_AGENTS.md) - Step-by-step agent creation
- [Deployment Guide](docs/DEPLOYMENT.md) - Deployment procedures
- [MLFlow Monitoring](docs/MLFLOW_MONITORING.md) - Model evaluation and monitoring guide
- [CI/CD Integration](docs/CI_CD_INTEGRATION.md) - Running CI checks locally and debugging

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙋 Support

For questions or issues:
- Create a GitHub issue
- Check existing documentation
- Contact the team via MS Teams

---

**Built with ❤️ using LangGraph, Databricks, and AWS**
