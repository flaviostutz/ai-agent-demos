# Getting Started with AI Agents Monorepo

Quick start guide to get you up and running with the AI Agents Monorepo.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **Make** utility installed
- **Git** for version control
- **OpenAI API key** (for LLM functionality)
- **Databricks account** (for production deployment)
- **AWS account** (optional, for cloud resources)

## Quick Start (5 minutes)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-agent-demos

# Create virtual environment and install dependencies
make setup

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

**Minimum required configuration**:
```bash
OPENAI_API_KEY=sk-your-openai-key-here
ENVIRONMENT=development
```

### 3. Generate Policy Documents

```bash
# Install reportlab for PDF generation
pip install reportlab

# Generate sample loan policy PDFs
cd agents/loan-approval/policies
python generate_policies.py
cd ../../..
```

### 4. Run Quality Checks

```bash
# Run linting
make lint

# Run tests
make test
```

### 5. Test the Loan Approval Agent Locally

```bash
# Navigate to loan approval agent
cd agents/loan-approval

# Run the agent API locally
make run-local
```

The API will start on `http://localhost:8000`. Open another terminal and test it:

```bash
# Test API health check
curl http://localhost:8000/health

# Test loan evaluation (example request)
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

## Project Structure Overview

```
ai-agent-demos/
├── agents/                    # All AI agents
│   └── loan-approval/        # Loan approval agent
├── shared/                    # Shared libraries
│   ├── models/               # Data models (Pydantic)
│   ├── monitoring/           # Observability (MLFlow, logging, metrics)
│   └── utils/                # Utilities (PDF loader, security)
├── infrastructure/            # Terraform for IaaC
├── .github/workflows/        # CI/CD pipelines
├── docs/                      # Documentation
└── Makefile                   # Build targets
```

## Common Tasks

### Running Tests

```bash
# Run all unit tests
make test

# Run integration tests
make test-integration

# Run performance tests
cd agents/loan-approval
make performance-test
```

### Code Quality

```bash
# Format code
make format

# Run linter
make lint

# Run type checker
make type-check

# Run all checks
make check
```

### Working with MLFlow

```bash
# Start MLFlow UI (view experiments)
mlflow ui

# Open browser to http://localhost:5000
```

### Creating a New Agent

See the [Developer Guide](docs/developer-guide.md) for detailed instructions on creating a new agent.

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Make Changes

Edit files, add features, fix bugs.

### 3. Test Locally

```bash
make lint
make test
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/my-new-feature
```

### 5. Create Pull Request

Go to GitHub and create a PR. The CI pipeline will automatically run tests.

### 6. After Approval and Merge

Changes to `main` branch automatically deploy to the test environment.

### 7. Create Release

```bash
# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

This triggers deployment to test → acceptance → production.

## Troubleshooting

### Virtual Environment Issues

```bash
# Remove and recreate
rm -rf venv
make setup
source venv/bin/activate
```

### Import Errors

```bash
# Ensure you're in project root
cd /path/to/ai-agent-demos

# Reinstall in development mode
pip install -e .[dev,test]
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process or use different port
export API_PORT=8001
make run-local
```

### MLFlow Tracking Issues

```bash
# Check if MLFlow directory exists
ls -la mlruns/

# Set tracking URI explicitly
export MLFLOW_TRACKING_URI=./mlruns
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

## Next Steps

1. **Read the [Developer Guide](docs/developer-guide.md)** for comprehensive documentation
2. **Explore the loan approval agent** in `agents/loan-approval/`
3. **Review the test cases** in `agents/loan-approval/tests/`
4. **Check the ground truth dataset** in `agents/loan-approval/datasets/`
5. **Read the loan policies** (generate PDFs first)
6. **Experiment with MLFlow** for tracking experiments

## Key Features

### ✅ Complete Monorepo Structure
- Multiple agents in one repository
- Shared libraries for common functionality
- Centralized configuration and tooling

### ✅ Production-Ready AI Agent
- LangGraph-based workflow
- Comprehensive risk assessment
- Policy document integration
- Multiple decision outcomes

### ✅ Enterprise Development Practices
- 80%+ test coverage target
- Automated linting and formatting
- Type checking with mypy
- CI/CD pipelines

### ✅ Observability & Monitoring
- MLFlow for experiment tracking
- Structured logging
- Performance metrics
- MS Teams notifications

### ✅ Security
- Context-based permissioning
- Data leakage prevention
- Environment-based access control

### ✅ Infrastructure as Code
- Terraform for cloud resources
- Databricks configuration
- AWS resource provisioning

## Support & Resources

- **Documentation**: See `docs/` directory
- **Developer Guide**: [docs/developer-guide.md](docs/developer-guide.md)
- **Agent README**: [agents/loan-approval/README.md](agents/loan-approval/README.md)
- **Issues**: Create issues on GitHub
- **Questions**: Contact the team

## License

See [LICENSE](LICENSE) file for details.

---

**Happy coding! 🚀**

For detailed information, see the [Developer Guide](docs/developer-guide.md).