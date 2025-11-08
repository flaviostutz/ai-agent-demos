.PHONY: help install clean lint test test-integration performance-test run-local build deploy undeploy

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m

# Configuration
AGENT_NAME := loan-approval
ENV ?= development
PYTHON := python3

help: ## Show this help message
	@echo "$(BLUE)Loan Approval Agent - Available targets:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install agent dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -e ../../[dev,test]
	@echo "$(GREEN)Dependencies installed!$(NC)"

clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .coverage htmlcov/ 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	@echo "$(YELLOW)Running ruff...$(NC)"
	cd ../.. && ruff check agents/loan-approval/
	@echo "$(YELLOW)Running black check...$(NC)"
	cd ../.. && black --check agents/loan-approval/
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	cd ../.. && black agents/loan-approval/
	@echo "$(GREEN)Code formatted!$(NC)"

type-check: ## Run type checking
	@echo "$(BLUE)Running type checks...$(NC)"
	cd ../.. && mypy agents/loan-approval/src/
	@echo "$(GREEN)Type checking complete!$(NC)"

test: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	cd ../.. && pytest agents/loan-approval/tests/ -v -m "not integration and not performance"
	@echo "$(GREEN)Tests complete!$(NC)"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	cd ../.. && pytest agents/loan-approval/tests/ -v -m integration
	@echo "$(GREEN)Integration tests complete!$(NC)"

performance-test: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	cd ../.. && pytest agents/loan-approval/tests/test_performance.py -v -m performance
	@echo "$(GREEN)Performance tests complete!$(NC)"

run-local: ## Run agent locally
	@echo "$(BLUE)Starting agent locally...$(NC)"
	@echo "$(YELLOW)Make sure to set environment variables in .env file$(NC)"
	cd src && $(PYTHON) api.py

build: ## Build agent
	@echo "$(BLUE)Building agent...$(NC)"
	@echo "Agent: $(AGENT_NAME)"
	@echo "Environment: $(ENV)"
	# Add build steps here (e.g., Docker build)
	@echo "$(GREEN)Build complete!$(NC)"

deploy: ## Deploy agent to environment
	@echo "$(BLUE)Deploying agent...$(NC)"
	@echo "Agent: $(AGENT_NAME)"
	@echo "Environment: $(ENV)"
	# Add deployment steps here
	@if [ "$(ENV)" = "production" ]; then \
		echo "$(RED)Deploying to PRODUCTION$(NC)"; \
		read -p "Are you sure? (yes/no) " confirm; \
		if [ "$$confirm" != "yes" ]; then \
			echo "$(YELLOW)Deployment cancelled$(NC)"; \
			exit 1; \
		fi; \
	fi
	@echo "$(GREEN)Deployment complete!$(NC)"

undeploy: ## Remove deployment
	@echo "$(BLUE)Undeploying agent...$(NC)"
	@echo "Agent: $(AGENT_NAME)"
	@echo "Environment: $(ENV)"
	# Add undeploy steps here
	@echo "$(GREEN)Undeploy complete!$(NC)"

check: lint type-check test ## Run all quality checks
	@echo "$(GREEN)All checks passed!$(NC)"

validate-dataset: ## Validate ground truth dataset
	@echo "$(BLUE)Validating ground truth dataset...$(NC)"
	cd src && $(PYTHON) -c "from datasets.validator import validate_dataset; validate_dataset('../datasets/ground_truth.json')"
	@echo "$(GREEN)Dataset validation complete!$(NC)"