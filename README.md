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
├── frontend/                  # Web Frontend
│   ├── src/                  # React application
│   │   ├── components/       # React components
│   │   └── api.js           # API client
│   └── Makefile              # Frontend build targets
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

- **Python 3.10+** installed
- **[UV](https://github.com/astral-sh/uv)** - Fast Python package installer
- **Make** utility installed
- **Git** for version control
- **OpenAI API key** (for LLM functionality)
- **Node.js 18+** and **pnpm** (for frontend)
- **Databricks account** (optional, for production deployment)

### Install UV

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Or with Homebrew
brew install uv
```

### 5-Minute Setup

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

3. **Configure API key**:

```bash
# Option 1: Store in macOS Keychain (Recommended for security)
make set-openai-key
# You'll be prompted to enter your key - it will be stored securely

# Copy and configure remaining environment variables
cp .env.example .env
nano .env  # Configure other settings (OPENAI_API_KEY not needed if using Keychain)
```

```bash
# Option 2: Use environment file
cp .env.example .env
nano .env
# Set: OPENAI_API_KEY=sk-your-key-here
```

**Note**: The `make run` command will automatically use the Keychain key if `OPENAI_API_KEY` is not set in your environment.

4. **Generate policy documents** (optional):
```bash
cd agents/loan-approval/policies
python generate_policies.py
cd ../../..
```

5. **Run the loan approval agent**:
```bash
make run
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

6. **Test the API**:
```bash
# Health check
curl http://localhost:8000/health

# Example loan evaluation
curl -X POST http://localhost:8000/api/v1/loan/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-001",
    "applicant": {
      "first_name": "John",
      "last_name": "Doe",
      "date_of_birth": "1985-06-15",
      "ssn": "123-45-6789",
      "email": "john.doe@email.com",
      "phone": "+15551234567",
      "address": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "zip_code": "62701"
    },
    "employment": {
      "status": "employed",
      "employer_name": "Tech Corp",
      "job_title": "Engineer",
      "years_employed": 5.0,
      "monthly_income": 8000,
      "additional_income": 0
    },
    "financial": {
      "monthly_debt_payments": 1500,
      "checking_balance": 10000,
      "savings_balance": 25000,
      "has_bankruptcy": false,
      "has_foreclosure": false
    },
    "credit_history": {
      "credit_score": 720,
      "number_of_credit_cards": 3,
      "total_credit_limit": 40000,
      "credit_utilization": 30,
      "number_of_late_payments_12m": 0,
      "number_of_late_payments_24m": 0,
      "number_of_inquiries_6m": 1,
      "oldest_credit_line_years": 10
    },
    "loan_details": {
      "amount": 300000,
      "purpose": "home_purchase",
      "term_months": 360,
      "property_value": 350000,
      "down_payment": 50000
    }
  }'
```

### Run the Web Frontend (Optional)

The project includes a modern React.js web application for submitting loan applications:

1. **Install frontend dependencies**:
```bash
cd frontend
make install
```

2. **Start the frontend** (in a new terminal):
```bash
make dev
```

The web application will be available at http://localhost:3000

3. **Use the application**:
- Fill out the comprehensive loan application form
- Submit for instant AI-powered evaluation
- View detailed decision with reasoning and recommendations

See [frontend/README.md](frontend/README.md) for more details.

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

## 🛠️ Development Workflow

### 1. Create Feature Branch

## 📝 Available Make Targets

### Root Level
- `make setup` - Initial project setup with UV
- `make install` - Install all dependencies with UV
- `make sync` - Sync dependencies to exact versions
- `make set-openai-key` - Store OpenAI API key in macOS Keychain (secure)
- `make get-openai-key` - Retrieve OpenAI API key from Keychain
- `make delete-openai-key` - Delete OpenAI API key from Keychain
- `make run` - Run the loan approval agent locally
- `make lint` - Run linters across all agents
- `make lint-fix` - Auto-fix linting issues
- `make test` - Run all unit tests
- `make test-integration` - Run integration tests
- `make test-performance` - Run performance tests
- `make build` - Build all agents
- `make deploy` - Deploy all agents
- `make undeploy` - Undeploy all agents
- `make clean` - Clean build artifacts
- `make check-uv` - Verify UV installation
- `make ci` - Run full CI pipeline locally

### Agent Level (in agents/*/Makefile)
- `make install` - Install agent dependencies
- `make clean` - Clean build artifacts
- `make lint` - Run linters
- `make lint-fix` - Auto-fix linting issues
- `make test` - Run all unit tests
- `make test-integration` - Run integration tests
- `make test-performance` - Run performance tests
- `make run-local` - Run agent locally
- `make build` - Build agent
- `make deploy` - Deploy agent to environment
- `make undeploy` - Remove deployment
- `make all` - Build and run all quality checks
- `make validate-dataset` - Validate ground truth dataset (loan approval specific)

## 📊 Monitoring and Observability


### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes and Test Locally
```bash
make lint
make test
```

### 3. Commit and Push
```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/your-feature-name
```

### 4. Create Pull Request
- PR will trigger automated checks
- Requires at least 1 approval
- All CI checks must pass

### 5. Merge to Main
- Automatically deploys to Test environment

### 6. Create Release Tag
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
make test-performance
```

## 🔧 Troubleshooting

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf .venv
make setup
source .venv/bin/activate
```

### Import Errors
```bash
# Ensure you're in project root
cd /path/to/ai-agent-demos

# Reinstall in development mode
make install
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process or use different port
export API_PORT=8001
make run
```

### MLFlow Tracking Issues
```bash
# Check if MLFlow directory exists
ls -la mlruns/

# Set tracking URI explicitly
export MLFLOW_TRACKING_URI=./mlruns

# Start MLFlow UI
mlflow ui
# Open browser to http://localhost:5000
```

### Tests Failing
```bash
# Clean everything
make clean

# Reinstall dependencies
make install

# Run tests with verbose output
pytest -v -s
```

## 📊 Monitoring and Observability

- **MLFlow**: Model tracking and versioning at `/mlruns`
- **Databricks Mosaic AI**: Real-time monitoring and alerts
- **MS Teams**: Automated notifications for failures and alerts

## 🔒 Security

- **Context-based tool permissioning** prevents data leakage
- **macOS Keychain integration** for secure credential storage (use `make set-openai-key`)
- **Environment-based secrets management** with optional macOS Keychain support
- **No credentials in code** or version control
- See [SECURITY.md](SECURITY.md) for detailed security practices

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
