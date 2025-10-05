# Developer Guide

This guide provides comprehensive information for developers working on the AI Agent platform.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Code Organization](#code-organization)
3. [Development Workflow](#development-workflow)
4. [Testing Guidelines](#testing-guidelines)
5. [Code Style](#code-style)
6. [Debugging](#debugging)
7. [Common Tasks](#common-tasks)

## Development Setup

### Initial Setup

1. **Install Prerequisites:**
   ```bash
   # Python 3.11+
   python --version  # Should be 3.11 or higher
   
   # Install Poetry
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Verify installation
   poetry --version
   ```

2. **Clone and Setup Project:**
   ```bash
   git clone https://github.com/flaviostutz/ai-agent-demos.git
   cd ai-agent-demos
   
   # Run setup
   make setup
   ```

3. **Configure Environment:**
   ```bash
   # Create .env file
   cat > .env << EOF
   OPENAI_API_KEY=your_key_here
   DATABRICKS_HOST=https://your-databricks.cloud.databricks.com
   DATABRICKS_TOKEN=your_token_here
   TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
   EOF
   ```

4. **Generate Documents:**
   ```bash
   make generate-docs
   make load-docs
   ```

## Code Organization

### Monorepo Structure

```
ai-agent-demos/
├── agents/              # Agent implementations (one folder per agent)
├── shared/              # Shared libraries used across agents
├── tests/               # Test suite mirroring source structure
├── infrastructure/      # IaC for deployment
├── config/              # Configuration files
├── scripts/             # Utility scripts
└── data/                # Data files (documents, vector stores)
```

### Agent Structure

Each agent follows this structure:

```
agents/agent_name/
├── agent.py         # Core agent logic (LangGraph)
├── api.py           # FastAPI REST API
├── __init__.py      # Package exports
└── Dockerfile       # Container image (if needed)
```

### Shared Libraries

- `logging_utils.py` - Structured logging with tracing
- `metrics.py` - Prometheus metrics collection
- `security.py` - Security context and PII masking
- `config.py` - Configuration management
- `alerting.py` - MS Teams alerting
- `mlflow_tracking.py` - MLFlow experiment tracking

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

- Write code following style guidelines
- Add/update tests
- Update documentation

### 3. Run Local Tests

```bash
# Run linting
make lint

# Run tests
make test

# Run coverage check
make test-coverage
```

### 4. Test Locally

```bash
# Run agent locally
make dev

# In another terminal, test the API
curl http://localhost:8000/health
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"  # Use conventional commits
```

### 6. Push and Create PR

```bash
git push origin feature/my-feature
# Create pull request on GitHub
```

## Testing Guidelines

### Test Types

1. **Unit Tests** (`tests/agents/`, `tests/shared/`)
   - Test individual functions/methods
   - Mock external dependencies
   - Fast execution

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - May use real services (with test data)
   - Moderate execution time

3. **Performance Tests** (`tests/performance/`)
   - Measure response times
   - Check resource usage
   - Validate scalability

### Writing Tests

```python
# tests/agents/my_agent/test_agent.py
import pytest
from agents.my_agent import MyAgent, MyAgentRequest

class TestMyAgent:
    @pytest.fixture(autouse=True)
    def setup(self, security_context):
        self.agent = MyAgent(security_context=security_context)
    
    def test_process_request(self):
        request = MyAgentRequest(request_id="TEST-001")
        response = self.agent.process_request(request)
        
        assert response is not None
        assert response.request_id == "TEST-001"
```

### Test Coverage

- Minimum coverage: **80%**
- Run: `make test-coverage`
- View report: `open htmlcov/index.html`

## Code Style

### Python Style Guide

We follow PEP 8 with these tools:

- **Ruff**: Fast Python linter
- **Black**: Code formatter
- **MyPy**: Static type checker

### Formatting

```bash
# Auto-format code
make lint-fix

# Check formatting
make lint
```

### Type Hints

Always use type hints:

```python
def process_data(data: dict[str, Any]) -> ProcessResult:
    """Process incoming data.
    
    Args:
        data: Input data dictionary
        
    Returns:
        ProcessResult with status and results
    """
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """Short description.
    
    Longer description explaining the function's purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
    """
    pass
```

## Debugging

### Local Debugging

1. **VS Code Launch Configuration:**

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "agents.loan_approval.api:app",
                "--reload"
            ],
            "jinja": true
        }
    ]
}
```

2. **Set Breakpoints:**
   - Click in the gutter next to line numbers
   - Use `breakpoint()` in code

3. **Logging:**

```python
from shared.logging_utils import get_logger

logger = get_logger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message", extra={"data": some_data})
```

### Debugging Tests

```bash
# Run specific test with output
poetry run pytest tests/agents/loan_approval/test_agent.py::test_name -v -s

# Debug with pdb
poetry run pytest --pdb tests/agents/loan_approval/test_agent.py
```

## Common Tasks

### Create a New Agent

```bash
make create-agent AGENT_NAME=my_agent
```

### Add a Dependency

```bash
# Add production dependency
poetry add package-name

# Add dev dependency
poetry add --group dev package-name

# Update lock file
poetry lock

# Install
poetry install
```

### Update Configuration

Edit `config/config.yaml`:

```yaml
agents:
  my_agent:
    llm:
      model: "gpt-4"
      temperature: 0.0
```

### Add a New Test

1. Create test file: `tests/agents/my_agent/test_feature.py`
2. Write test using pytest fixtures
3. Run: `make test-agent AGENT_NAME=my_agent`

### View Metrics Locally

```bash
# Start agent
make dev

# In another terminal
curl http://localhost:8000/metrics
```

### Generate New Documents

1. Add PDF generation logic to `scripts/generate_loan_docs.py`
2. Run: `make generate-docs`
3. Load to vector store: `make load-docs`

## Best Practices

### 1. Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Implement proper security context
- Apply PII masking where needed

### 2. Performance

- Use async/await for I/O operations
- Cache frequently accessed data
- Monitor agent performance
- Set appropriate timeouts

### 3. Error Handling

```python
try:
    result = agent.process_request(request)
except ValueError as e:
    logger.error(f"Validation error: {e}")
    metrics.record_error(error_type="validation")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    metrics.record_error(error_type="unknown")
    alerter.send_agent_error(agent_name="my_agent", error_message=str(e))
    raise
```

### 4. Testing

- Write tests before or alongside code
- Test edge cases and error conditions
- Use meaningful test names
- Keep tests independent

### 5. Documentation

- Update README when adding features
- Document complex logic with comments
- Keep API documentation current
- Update changelog

## Troubleshooting

### Poetry Issues

```bash
# Clear cache
poetry cache clear pypi --all

# Reinstall
rm -rf .venv
poetry install
```

### Test Failures

```bash
# Run with verbose output
poetry run pytest -v -s

# Run specific test
poetry run pytest tests/path/to/test.py::test_name -v

# Check coverage
make test-coverage
```

### Import Errors

```bash
# Ensure project is installed
poetry install

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Getting Help

- Check existing documentation
- Review code examples in `/agents`
- Ask questions in team channels
- Create GitHub issues for bugs

---

Happy coding! 🚀
