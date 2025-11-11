.PHONY: help setup install sync clean lint lint-fix test test-integration test-performance run build deploy undeploy all ci check-uv frontend-install frontend-dev frontend-build frontend-clean frontend-test frontend-test-ui run-all

# Default target
.DEFAULT_GOAL := help

# UV command - check if uv is installed
UV := $(shell command -v uv 2> /dev/null)

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m # No Color

check-uv: ## Check if UV is installed
ifndef UV
	@echo "$(RED)ERROR: UV is not installed!$(NC)"
	@echo "$(YELLOW)Install UV with: curl -LsSf https://astral.sh/uv/install.sh | sh$(NC)"
	@echo "$(YELLOW)Or with pip: pip install uv$(NC)"
	@exit 1
endif
	@echo "$(GREEN)UV is installed at: $(UV)$(NC)"

help: ## Show this help message
	@echo "$(BLUE)AI Agents Monorepo - Available targets:$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup & Installation:$(NC)"
	@grep -E '^(setup|install|sync|clean):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@grep -E '^(lint|lint-fix|test|test-integration|test-performance):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Running Services:$(NC)"
	@grep -E '^(run|run-mlflow|run-all):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Frontend:$(NC)"
	@grep -E '^frontend-.*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Deployment:$(NC)"
	@grep -E '^(build|deploy|undeploy):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Other:$(NC)"
	@grep -E '^(all|ci|set-openai-key|set-azure-openai-key):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Agent-specific targets:$(NC)"
	@echo "  Run 'make -C agents/<agent-name> <target>' for agent-specific operations"

setup: check-uv ## Initial project setup (install UV and dependencies)
	@echo "$(BLUE)Setting up project with UV...$(NC)"
	uv venv --python $(shell which python3)
	@echo "$(GREEN)Virtual environment created with UV.$(NC)"
	@echo "$(YELLOW)Activate it with: source .venv/bin/activate$(NC)"
	@if [ -n "$$UV_INDEX_URL" ]; then \
		echo "$(YELLOW)Using custom index: $$UV_INDEX_URL$(NC)"; \
	fi
	@echo "$(BLUE)Installing dependencies...$(NC)"
	uv pip install --native-tls -e ".[dev,test,docs]"
	@echo "$(GREEN)Setup complete!$(NC)"
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)Next steps:$(NC)"
	@echo "  1. Activate virtual environment: $(YELLOW)source .venv/bin/activate$(NC)"
	@echo "  2. Configure .env file: $(YELLOW)cp .env.example .env && nano .env$(NC)"
	@echo "  3. Store API key in macOS Keychain (choose one):"
	@echo "     OpenAI: $(YELLOW)make set-openai-key$(NC)"
	@echo "     Azure OpenAI: $(YELLOW)make set-azure-openai-key$(NC)"
	@echo "  4. Run the agent: $(YELLOW)make run$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"

install: check-uv ## Install project dependencies with UV
	@echo "$(BLUE)Installing dependencies with UV...$(NC)"
	@if [ -n "$$UV_INDEX_URL" ]; then \
		echo "$(YELLOW)Using custom index: $$UV_INDEX_URL$(NC)"; \
	fi
	uv pip install --native-tls -e ".[dev,test,docs]"
	@echo "$(GREEN)Dependencies installed!$(NC)"

sync: check-uv ## Sync dependencies (ensures exact versions)
	@echo "$(BLUE)Syncing dependencies with UV...$(NC)"
	uv pip sync --native-tls
	@echo "$(GREEN)Dependencies synced!$(NC)"

set-openai-key: ## Store OpenAI API key in macOS Keychain (secure)
	@echo "$(BLUE)Storing OpenAI API key in macOS Keychain...$(NC)"
	@echo "$(YELLOW)You will be prompted to enter your OpenAI API key.$(NC)"
	@security add-generic-password -s "ai-agent-demos" -a "openai-api-key" -w
	@echo "$(GREEN)✓ API key stored securely in macOS Keychain$(NC)"
	@echo "$(YELLOW)The 'make run' command will automatically use it if OPENAI_API_KEY is not set$(NC)"

set-azure-openai-key: ## Store Azure OpenAI API key in macOS Keychain (secure)
	@echo "$(BLUE)Storing Azure OpenAI API key in macOS Keychain...$(NC)"
	@echo "$(YELLOW)You will be prompted to enter your Azure OpenAI API key.$(NC)"
	@security add-generic-password -s "ai-agent-demos" -a "azure-openai-api-key" -w
	@echo "$(GREEN)✓ Azure OpenAI API key stored securely in macOS Keychain$(NC)"
	@echo "$(YELLOW)The 'make run' command will automatically use it if AZURE_OPENAI_API_KEY is not set$(NC)"

get-openai-key: ## Retrieve OpenAI API key from macOS Keychain
	@echo "$(BLUE)Retrieving OpenAI API key from macOS Keychain...$(NC)"
	@security find-generic-password -s "ai-agent-demos" -a "openai-api-key" -w 2>/dev/null || echo "$(RED)No key found in Keychain$(NC)"

get-azure-openai-key: ## Retrieve Azure OpenAI API key from macOS Keychain
	@echo "$(BLUE)Retrieving Azure OpenAI API key from macOS Keychain...$(NC)"
	@security find-generic-password -s "ai-agent-demos" -a "azure-openai-api-key" -w 2>/dev/null || echo "$(RED)No key found in Keychain$(NC)"

delete-openai-key: ## Delete OpenAI API key from macOS Keychain
	@echo "$(BLUE)Deleting OpenAI API key from macOS Keychain...$(NC)"
	@security delete-generic-password -s "ai-agent-demos" -a "openai-api-key" 2>/dev/null && echo "$(GREEN)✓ Key deleted$(NC)" || echo "$(RED)No key found to delete$(NC)"

delete-azure-openai-key: ## Delete Azure OpenAI API key from macOS Keychain
	@echo "$(BLUE)Deleting Azure OpenAI API key from macOS Keychain...$(NC)"
	@security delete-generic-password -s "ai-agent-demos" -a "azure-openai-api-key" 2>/dev/null && echo "$(GREEN)✓ Key deleted$(NC)" || echo "$(RED)No key found to delete$(NC)"

clean: ## Clean build artifacts and cache files
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	rm -rf build/ dist/ 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

lint: ## Run linters (ruff check, format check, and type check)
	@echo "$(BLUE)Running linters...$(NC)"
	@echo "$(YELLOW)Running ruff check...$(NC)"
	uv run ruff check agents/ shared/
	@echo "$(YELLOW)Running ruff format check...$(NC)"
	uv run ruff format --check agents/ shared/
	@echo "$(YELLOW)Running type checks...$(NC)"
	uv run mypy agents/ shared/
	@echo "$(GREEN)Linting complete!$(NC)"

lint-fix: ## Auto-fix linting issues (ruff check and format)
	@echo "$(BLUE)Auto-fixing linting issues...$(NC)"
	@echo "$(YELLOW)Running ruff --fix...$(NC)"
	uv run ruff check --fix agents/ shared/
	@echo "$(YELLOW)Running ruff format...$(NC)"
	uv run ruff format agents/ shared/
	@echo "$(GREEN)Linting fixes applied!$(NC)"

test: ## Run all unit tests
	@echo "$(BLUE)Running tests...$(NC)"
	uv run pytest -v -m "not integration and not performance"
	@echo "$(GREEN)Tests complete!$(NC)"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	uv run pytest -v -m integration
	@echo "$(GREEN)Integration tests complete!$(NC)"

test-performance: ## Run performance tests
	@echo "$(BLUE)Running performance tests...$(NC)"
	uv run pytest -v -m performance --no-cov
	@echo "$(GREEN)Performance tests complete!$(NC)"

run: check-uv ## Run the loan approval agent locally (with LLM debug logging enabled)
	@echo "$(BLUE)Starting loan approval agent locally...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Warning: .env file not found. Creating from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(YELLOW)Please configure your API key in .env or store in macOS Keychain$(NC)"; \
		echo "$(RED)Stopping - please configure API key before running$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Environment loaded from .env$(NC)"
	@echo "$(GREEN)LLM debug logging enabled for local development$(NC)"
	@echo "$(YELLOW)API will be available at: http://localhost:8000$(NC)"
	@echo "$(YELLOW)API docs at: http://localhost:8000/docs$(NC)"
	@echo "$(YELLOW)MLflow UI: cd agents/loan_approval/src && mlflow ui --port 5000$(NC)"
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		export OPENAI_API_KEY=$$(security find-generic-password -s "ai-agent-demos" -a "openai-api-key" -w 2>/dev/null || echo ""); \
		if [ -n "$$OPENAI_API_KEY" ]; then \
			echo "$(GREEN)Using OpenAI API key from macOS Keychain$(NC)"; \
		fi; \
	fi && \
	if [ -z "$$AZURE_OPENAI_API_KEY" ]; then \
		export AZURE_OPENAI_API_KEY=$$(security find-generic-password -s "ai-agent-demos" -a "azure-openai-api-key" -w 2>/dev/null || echo ""); \
		if [ -n "$$AZURE_OPENAI_API_KEY" ]; then \
			echo "$(GREEN)Using Azure OpenAI API key from macOS Keychain$(NC)"; \
		fi; \
	fi && \
	cd agents/loan_approval/src && uv run python api.py

run-mlflow: ## Start MLflow UI to view LLM logs and metrics
	@echo "$(BLUE)Starting MLflow UI...$(NC)"
	@echo "$(YELLOW)MLflow UI will be available at: http://localhost:5000$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@cd agents/loan_approval/src && mlflow ui --port 5000

build: ## Build all agents
	@echo "$(BLUE)Building all agents...$(NC)"
	@for agent in agents/*/; do \
		if [ -f "$$agent/Makefile" ]; then \
			echo "$(YELLOW)Building $$agent...$(NC)"; \
			$(MAKE) -C "$$agent" build || exit 1; \
		fi \
	done
	@echo "$(GREEN)All agents built!$(NC)"

deploy: ## Deploy all agents
	@echo "$(BLUE)Deploying all agents...$(NC)"
	@for agent in agents/*/; do \
		if [ -f "$$agent/Makefile" ]; then \
			echo "$(YELLOW)Deploying $$agent...$(NC)"; \
			$(MAKE) -C "$$agent" deploy || exit 1; \
		fi \
	done
	@echo "$(GREEN)All agents deployed!$(NC)"

undeploy: ## Undeploy all agents
	@echo "$(BLUE)Undeploying all agents...$(NC)"
	@for agent in agents/*/; do \
		if [ -f "$$agent/Makefile" ]; then \
			echo "$(YELLOW)Undeploying $$agent...$(NC)"; \
			$(MAKE) -C "$$agent" undeploy || exit 1; \
		fi \
	done
	@echo "$(GREEN)All agents undeployed!$(NC)"

all: build lint test
	@echo "$(GREEN)All checks passed!$(NC)"

ci: clean install all ## Run CI pipeline locally
	@echo "$(GREEN)CI pipeline complete!$(NC)"

# Frontend targets

frontend-install: ## Install frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	@if [ ! -d "frontend/node_modules" ]; then \
		cd frontend && COREPACK_ENABLE_STRICT=0 pnpm install --no-frozen-lockfile; \
		echo "$(GREEN)Frontend dependencies installed!$(NC)"; \
	else \
		echo "$(YELLOW)Frontend dependencies already installed. Run 'make frontend-clean' to reinstall.$(NC)"; \
	fi

frontend-dev: ## Start frontend development server
	@echo "$(BLUE)Starting frontend development server...$(NC)"
	@echo "$(YELLOW)Frontend will be available at: http://localhost:3000$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@cd frontend && COREPACK_ENABLE_STRICT=0 pnpm run dev

frontend-build: ## Build frontend for production
	@echo "$(BLUE)Building frontend for production...$(NC)"
	@cd frontend && COREPACK_ENABLE_STRICT=0 pnpm run build
	@echo "$(GREEN)Frontend build complete! Output in frontend/dist/$(NC)"

frontend-preview: ## Preview production build
	@echo "$(BLUE)Starting production preview server...$(NC)"
	@echo "$(YELLOW)Preview will be available at: http://localhost:4173$(NC)"
	@cd frontend && COREPACK_ENABLE_STRICT=0 pnpm run preview

frontend-clean: ## Clean frontend build artifacts and dependencies
	@echo "$(BLUE)Cleaning frontend...$(NC)"
	@cd frontend && rm -rf node_modules dist
	@echo "$(GREEN)Frontend cleaned!$(NC)"

frontend-test: ## Run Playwright tests
	@echo "$(BLUE)Running Playwright tests...$(NC)"
	@echo "$(YELLOW)Note: Dev server must be running on port 3000$(NC)"
	@echo "$(YELLOW)Run 'make frontend-dev' in another terminal if not started$(NC)"
	@cd frontend && SKIP_WEBSERVER=1 COREPACK_ENABLE_STRICT=0 pnpm run test
	@echo "$(GREEN)Frontend tests complete!$(NC)"

frontend-test-ui: ## Run Playwright tests in UI mode
	@echo "$(BLUE)Starting Playwright UI mode...$(NC)"
	@echo "$(YELLOW)Note: Dev server must be running on port 3000$(NC)"
	@cd frontend && SKIP_WEBSERVER=1 COREPACK_ENABLE_STRICT=0 pnpm run test:ui

run-all: ## Start both backend API and frontend together
	@chmod +x start.sh
	@./start.sh
