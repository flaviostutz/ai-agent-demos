# Main Makefile for AI Agent Monorepo

.PHONY: help install lint test build deploy undeploy clean generate-docs load-docs setup dev-setup

# Default target
.DEFAULT_GOAL := help

# Environment variables
PYTHON := python3
POETRY := $(shell command -v poetry 2>/dev/null || echo "$$HOME/.local/bin/poetry")
AGENT_NAME ?= loan_approval
ENV ?= test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

check-poetry: ## Check if Poetry is installed
	@command -v poetry >/dev/null 2>&1 || command -v $(HOME)/.local/bin/poetry >/dev/null 2>&1 || { \
		echo "❌ Poetry not found!"; \
		echo ""; \
		echo "Install Poetry with one of these methods:"; \
		echo "  1. Official installer (recommended):"; \
		echo "     curl -sSL https://install.python-poetry.org | python3 -"; \
		echo "     export PATH=\"\$$HOME/.local/bin:\$$PATH\""; \
		echo ""; \
		echo "  2. Using pipx:"; \
		echo "     pipx install poetry"; \
		echo ""; \
		echo "  3. Using pip:"; \
		echo "     pip3 install --user poetry"; \
		echo ""; \
		echo "After installation, add Poetry to your PATH or restart your terminal."; \
		exit 1; \
	}

setup: check-poetry ## Initial setup - install dependencies
	@echo "Setting up project..."
	$(POETRY) install
	$(POETRY) run pre-commit install
	@echo "Setup complete! ✅"

dev-setup: setup generate-docs load-docs ## Complete development setup
	@echo "Development environment ready! 🚀"
	@echo "Run 'make dev' to start the loan approval API locally"

install: ## Install dependencies
	$(POETRY) install

install-dev: ## Install development dependencies
	$(POETRY) install --with dev

lint: ## Run linting checks
	@echo "Running lint checks..."
	$(POETRY) run ruff check agents/ shared/ tests/
	$(POETRY) run black --check agents/ shared/ tests/
	$(POETRY) run mypy agents/ shared/

lint-fix: ## Fix linting issues
	@echo "Fixing lint issues..."
	$(POETRY) run ruff check --fix agents/ shared/ tests/
	$(POETRY) run black agents/ shared/ tests/

test: ## Run tests
	@echo "Running tests..."
	$(POETRY) run pytest tests/ -v

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	$(POETRY) run pytest tests/ -v --cov=agents --cov=shared --cov-report=html --cov-report=term

test-agent: ## Run tests for specific agent (use AGENT_NAME=<name>)
	@echo "Running tests for $(AGENT_NAME)..."
	$(POETRY) run pytest tests/agents/$(AGENT_NAME)/ -v

generate-docs: ## Generate loan rule PDF documents
	@echo "Generating loan rule documents..."
	$(POETRY) run python scripts/generate_loan_docs.py

load-docs: ## Load documents into vector store
	@echo "Loading documents into vector store..."
	$(POETRY) run python scripts/load_documents.py

evaluate: ## Run agent evaluation on test dataset
	@echo "Evaluating loan approval agent..."
	$(POETRY) run python scripts/evaluate_agent.py --agent loan_approval --dataset loan_approval_test_set

evaluate-agent: ## Evaluate specific agent (use AGENT_NAME=<name> DATASET=<dataset>)
	@echo "Evaluating $(AGENT_NAME) on dataset $(DATASET)..."
	$(POETRY) run python scripts/evaluate_agent.py --agent $(AGENT_NAME) --dataset $(DATASET)

evaluate-drift: ## Check for model drift (use BASELINE=<dataset> CURRENT=<dataset>)
	@echo "Checking for drift between $(BASELINE) and $(CURRENT)..."
	$(POETRY) run python scripts/evaluate_agent.py --agent loan_approval --dataset $(CURRENT) --drift-detection --baseline-dataset $(BASELINE)

build: lint test ## Build the project (lint + test)
	@echo "Build successful! ✅"

dev: ## Run the loan approval API locally
	@echo "Starting Loan Approval API on http://localhost:8000"
	@echo "API docs available at http://localhost:8000/docs"
	$(POETRY) run uvicorn agents.loan_approval.api:app --reload --host 0.0.0.0 --port 8000

dev-agent: ## Run specific agent API (use AGENT_NAME=<name>)
	@echo "Starting $(AGENT_NAME) API..."
	$(POETRY) run uvicorn agents.$(AGENT_NAME).api:app --reload --host 0.0.0.0 --port 8000

deploy-test: ## Deploy to test environment
	@echo "Deploying to test environment..."
	cd infrastructure && make deploy ENV=test

deploy-acceptance: ## Deploy to acceptance environment
	@echo "Deploying to acceptance environment..."
	cd infrastructure && make deploy ENV=acceptance

deploy-prod: ## Deploy to production environment
	@echo "Deploying to production environment..."
	cd infrastructure && make deploy ENV=prod

deploy: ## Deploy to environment (use ENV=test|acceptance|prod)
	@echo "Deploying to $(ENV) environment..."
	cd infrastructure && make deploy ENV=$(ENV)

undeploy: ## Undeploy from environment (use ENV=test|acceptance|prod)
	@echo "Undeploying from $(ENV) environment..."
	cd infrastructure && make undeploy ENV=$(ENV)

performance-test: ## Run performance tests for agent
	@echo "Running performance tests for $(AGENT_NAME)..."
	$(POETRY) run pytest tests/performance/test_$(AGENT_NAME)_performance.py -v

security-scan: ## Run security scans
	@echo "Running security scans..."
	$(POETRY) run pip install bandit --quiet 2>/dev/null || true
	$(POETRY) run bandit -r agents/ shared/ -f json -o security-report.json || true
	@echo "Security scan complete. Report: security-report.json"

ci-install: check-poetry ## Install dependencies for CI/CD pipeline
	@echo "Installing dependencies for CI..."
	$(POETRY) install --no-interaction --no-root
	$(POETRY) install --no-interaction
	@echo "CI dependencies installed ✅"

ci-lint: ## Run all lint checks for CI/CD
	@echo "Running CI lint checks..."
	$(POETRY) run ruff check agents/ shared/ tests/
	$(POETRY) run black --check agents/ shared/ tests/
	$(POETRY) run mypy agents/ shared/ --ignore-missing-imports || true
	@echo "Lint checks complete ✅"

ci-test: ## Run tests for CI/CD with coverage
	@echo "Running CI tests with coverage..."
	$(POETRY) run pytest tests/ -v --cov=agents --cov=shared --cov-report=xml --cov-report=term
	@echo "Tests complete ✅"

ci-security: ## Run security scan for CI/CD
	@echo "Running CI security scan..."
	$(POETRY) run pip install bandit --quiet
	$(POETRY) run bandit -r agents/ shared/ -f json -o bandit-report.json || true
	@echo "Security scan complete ✅"

ci-build: ## Build package for CI/CD
	@echo "Building package..."
	$(POETRY) build
	@echo "Package built ✅"

ci-deploy-test: ## Deploy to test environment (CI/CD)
	@echo "Deploying to test environment via CI/CD..."
	cd infrastructure && make deploy ENV=test

ci-deploy-acceptance: ## Deploy to acceptance environment (CI/CD)
	@echo "Deploying to acceptance environment via CI/CD..."
	cd infrastructure && make deploy ENV=acceptance

ci-deploy-prod: ## Deploy to production environment (CI/CD)
	@echo "Deploying to production environment via CI/CD..."
	cd infrastructure && make deploy ENV=prod

ci-all: ci-install ci-lint ci-test ci-security ci-build ## Run all CI checks locally

clean: ## Clean build artifacts and caches
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf dist/ build/ htmlcov/ .coverage
	@echo "Cleanup complete! ✨"

docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t ai-agents:$(AGENT_NAME) -f agents/$(AGENT_NAME)/Dockerfile .

docker-run: ## Run Docker container locally
	@echo "Running Docker container..."
	docker run -p 8000:8000 --env-file .env ai-agents:$(AGENT_NAME)

docs: ## Generate documentation
	@echo "Generating documentation..."
	@echo "Documentation generation not yet implemented"

create-agent: ## Create a new agent from template (use AGENT_NAME=<name>)
	@echo "Creating new agent: $(AGENT_NAME)"
	@bash scripts/create_agent.sh $(AGENT_NAME)

.PHONY: all
all: clean install lint test build ## Run all checks
	@echo "All checks passed! ✅"
