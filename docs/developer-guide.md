# Developer Guide

Complete guide for developers working with the AI Agents Monorepo.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Creating a New Agent](#creating-a-new-agent)
4. [Local Development](#local-development)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Make
- Git
- Databricks CLI (for deployment)
- Docker (optional, for containerized development)

### Initial Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ai-agent-demos
```

2. **Create virtual environment and install dependencies**:
```bash
make setup
source venv/bin/activate
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Required environment variables:
- `OPENAI_API_KEY`: OpenAI API key for LLM
- `MLFLOW_TRACKING_URI`: MLFlow tracking server (optional, defaults to local)
- `DATABRICKS_HOST`: Databricks workspace URL
- `DATABRICKS_TOKEN`: Databricks access token
- `TEAMS_WEBHOOK_URL`: MS Teams webhook for notifications

4. **Verify installation**:
```bash
make check
```

## Project Structure

```
ai-agent-demos/
├── agents/                    # All AI agents
│   ├── loan-approval/        # Loan approval agent
│   │   ├── src/              # Agent source code
│   │   │   ├── agent.py      # Main agent implementation
│   │   │   ├── tools.py      # Agent tools
│   │   │   ├── config.py     # Configuration
│   │   │   └── api.py        # REST API
│   │   ├── tests/            # Tests
│   │   ├── datasets/         # Ground truth datasets
│   │   ├── policies/         # Policy documents
│   │   ├── Makefile          # Agent build targets
│   │   └── README.md         # Agent documentation
│   └── [other-agents]/       # Additional agents
├── shared/                    # Shared libraries
│   ├── models/               # Data models
│   ├── monitoring/           # Observability utilities
│   └── utils/                # Common utilities
├── infrastructure/            # Infrastructure as Code
├── .github/                   # CI/CD workflows
├── docs/                      # Documentation
├── Makefile                   # Root build targets
└── pyproject.toml            # Python project config
```

## Creating a New Agent

### Step 1: Create Agent Directory Structure

```bash
# Create agent directory
mkdir -p agents/my-agent/{src,tests,datasets,policies}

# Create necessary files
touch agents/my-agent/src/{__init__.py,agent.py,config.py,tools.py,api.py}
touch agents/my-agent/tests/{__init__.py,test_agent.py,test_performance.py}
touch agents/my-agent/{README.md,Makefile}
```

### Step 2: Define Data Models

Create your agent's data models in `shared/models/` if they will be reused, or in your agent's `src/` directory if agent-specific.

Example:
```python
# shared/models/my_model.py
from pydantic import BaseModel, Field
from typing import Optional

class MyRequest(BaseModel):
    request_id: str
    data: str
    # ... other fields

class MyResponse(BaseModel):
    result: str
    confidence: float
```

### Step 3: Implement Agent Configuration

```python
# agents/my-agent/src/config.py
from pydantic_settings import BaseSettings

class AgentConfig(BaseSettings):
    agent_name: str = "my-agent"
    agent_version: str = "0.1.0"
    openai_api_key: str
    # ... other config

config = AgentConfig()
```

### Step 4: Implement Agent Logic

Use LangGraph to build your agent's workflow:

```python
# agents/my-agent/src/agent.py
from langgraph.graph import StateGraph
from typing import Dict, Any

class MyAgent:
    def __init__(self):
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(Dict[str, Any])
        
        # Add nodes
        workflow.add_node("process", self._process)
        workflow.add_node("validate", self._validate)
        
        # Define edges
        workflow.set_entry_point("validate")
        workflow.add_edge("validate", "process")
        workflow.add_edge("process", END)
        
        return workflow.compile()
    
    def _validate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Validation logic
        return state
    
    def _process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Processing logic
        return state
    
    def execute(self, request: MyRequest) -> MyResponse:
        result = self.workflow.invoke({"request": request})
        return MyResponse(**result)
```

### Step 5: Create REST API

```python
# agents/my-agent/src/api.py
from fastapi import FastAPI
from agents.my_agent.src.agent import MyAgent

app = FastAPI(title="My Agent API")
agent = MyAgent()

@app.post("/api/v1/process")
async def process(request: MyRequest) -> MyResponse:
    return agent.execute(request)
```

### Step 6: Write Tests

```python
# agents/my-agent/tests/test_agent.py
import pytest
from agents.my_agent.src.agent import MyAgent

@pytest.fixture
def agent():
    return MyAgent()

def test_agent_execution(agent):
    request = MyRequest(request_id="test", data="test data")
    response = agent.execute(request)
    assert response.result is not None
```

### Step 7: Create Makefile

```makefile
# agents/my-agent/Makefile
.PHONY: install test run-local deploy

install:
	pip install -e ../../[dev,test]

test:
	cd ../.. && pytest agents/my-agent/tests/ -v

run-local:
	cd src && python api.py

deploy:
	# Add deployment logic
	@echo "Deploying my-agent..."
```

### Step 8: Document Your Agent

Create a comprehensive README.md with:
- Agent overview
- Input/output schemas
- Configuration options
- Local development instructions
- Deployment guide

### Step 9: Add Ground Truth Dataset

```json
{
  "dataset_version": "1.0",
  "test_cases": [
    {
      "request_id": "test-001",
      "expected_output": {...},
      "request": {...}
    }
  ]
}
```

## Local Development

### Running an Agent Locally

```bash
# Navigate to agent directory
cd agents/loan-approval

# Install dependencies
make install

# Run locally
make run-local

# Test the API
curl -X POST http://localhost:8000/api/v1/loan/evaluate \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### Development Workflow

1. **Create a feature branch**:
```bash
git checkout -b feature/my-feature
```

2. **Make changes and test**:
```bash
make lint
make test
```

3. **Commit changes**:
```bash
git add .
git commit -m "feat: add new feature"
```

4. **Push and create PR**:
```bash
git push origin feature/my-feature
# Create PR on GitHub
```

### Using MLFlow for Tracking

```python
from shared.monitoring import MetricsTracker

tracker = MetricsTracker(experiment_name="my-experiment")

with tracker.start_run(run_name="test-run"):
    tracker.log_params({"param1": "value1"})
    tracker.log_metrics({"accuracy": 0.95})
    # Your code here
```

View MLFlow UI:
```bash
mlflow ui --backend-store-uri ./mlruns
# Open http://localhost:5000
```

## Testing

### Unit Tests

```bash
# Run all unit tests
make test

# Run specific test file
pytest agents/loan-approval/tests/test_agent.py -v

# Run with coverage
pytest --cov=agents --cov-report=html
```

### Integration Tests

```bash
# Run integration tests
make test-integration

# Run for specific agent
cd agents/loan-approval
make test-integration
```

### Performance Tests

```bash
# Run performance tests against ground truth
cd agents/loan-approval
make performance-test

# View results in MLFlow
mlflow ui
```

### Writing Tests

Follow these conventions:
- Use `pytest` framework
- Mark tests with appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
- Aim for >= 80% code coverage
- Use fixtures for common setup
- Test edge cases and error conditions

## Deployment

### Deployment Environments

- **Test**: Automated deployment on merge to `main`
- **Acceptance**: Automated deployment on tag creation
- **Production**: Manual approval required after acceptance

### Manual Deployment

```bash
# Deploy to test environment
cd agents/loan-approval
make deploy ENV=test

# Deploy to production
make deploy ENV=production
```

### Automated Deployment

Deployments are triggered by:
1. **Push to main**: Deploys to test environment
2. **Create tag** (v*.*.*): Deploys to test → acceptance → production

Example:
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Rollback

```bash
# Undeploy current version
make undeploy ENV=production

# Deploy previous version
git checkout v0.9.0
make deploy ENV=production
```

## Troubleshooting

### Common Issues

**Issue: Import errors**
```bash
# Ensure you're in the project root and virtual environment is activated
source venv/bin/activate
pip install -e .[dev,test]
```

**Issue: MLFlow tracking not working**
```bash
# Set MLFlow tracking URI
export MLFLOW_TRACKING_URI=./mlruns
# Or use remote tracking server
export MLFLOW_TRACKING_URI=https://mlflow.example.com
```

**Issue: Tests failing locally**
```bash
# Clean and reinstall
make clean
make install
make test
```

**Issue: API not starting**
```bash
# Check if port is in use
lsof -i :8000
# Use different port
export API_PORT=8001
make run-local
```

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
make run-local
```

### Getting Help

1. Check agent-specific README
2. Review existing test cases
3. Check MLFlow experiment logs
4. Review CI/CD pipeline logs
5. Contact team on Slack #ai-agents channel

## Best Practices

### Code Quality

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all public functions
- Keep functions small and focused
- Use meaningful variable names

### Security

- Never commit API keys or secrets
- Use environment variables for configuration
- Implement proper permission checking
- Validate all inputs
- Use security context for tool access

### Performance

- Monitor processing times with MLFlow
- Set performance thresholds in tests
- Use async where appropriate
- Cache expensive operations
- Optimize LLM token usage

### Observability

- Log important events and decisions
- Track metrics for all operations
- Use structured logging
- Set up alerts for errors
- Monitor costs and usage

### Documentation

- Keep README files up to date
- Document configuration options
- Add inline comments for complex logic
- Update API documentation
- Create examples for common use cases

### Testing

- Write tests before fixing bugs
- Test edge cases
- Use ground truth datasets
- Monitor test coverage
- Keep tests fast and focused

## Additional Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [MLFlow Documentation](https://mlflow.org/docs/latest/index.html)
- [Databricks Documentation](https://docs.databricks.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Support

For questions or issues:
- Create an issue on GitHub
- Contact the team on Slack
- Review the documentation
- Check existing PRs for examples