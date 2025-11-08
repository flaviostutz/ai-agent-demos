.PHONY: help setup install sync clean lint lint-fix test test-integration test-performance run build deploy undeploy all ci check-uv

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
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
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
	@echo "  2. Set OpenAI API key (recommended): $(YELLOW)make set-openai-key$(NC)"
	@echo "  3. Or configure .env file: $(YELLOW)cp .env.example .env && nano .env$(NC)"
	@echo "  4. Run the agent: $(YELLOW)make run$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"

install: check-uv ## Install project dependencies with UV
	@echo "$(BLUE)Installing dependencies with UV...$(NC)"
	@if [ -n "$$UV_INDEX_URL" ]; then \
		echo "$(YELLOW)Using custom index: $$UV_INDEX_URL$(NC)"; \
	fi
	uv pip install --native-tls -e ".[dev,test,docs]"
	@echo "$(GREEN)Dependencies installed!$(NC)"
	@echo "$(YELLOW)Tip: Use 'make set-openai-key' to securely store your OpenAI API key in macOS Keychain$(NC)"

sync: check-uv ## Sync dependencies (ensures exact versions)
	@echo "$(BLUE)Syncing dependencies with UV...$(NC)"
	uv pip sync --native-tls
	@echo "$(GREEN)Dependencies synced!$(NC)"

set-openai-key: check-uv ## Set OpenAI API key in macOS Keychain (secure)
	@echo "$(BLUE)Setting OpenAI API key in macOS Keychain...$(NC)"
	@echo "$(YELLOW)You will be prompted to enter your OpenAI API key.$(NC)"
	@echo "$(YELLOW)The key will be stored securely in macOS Keychain.$(NC)"
	@uv run python3 -c "import keyring; import getpass; key = getpass.getpass('Enter your OpenAI API key: '); keyring.set_password('ai-agent-demos', 'openai-api-key', key); print('\n✓ API key stored securely in macOS Keychain')"
	@echo "$(GREEN)Done! The application will now retrieve the key from Keychain.$(NC)"

get-openai-key: check-uv ## Retrieve OpenAI API key from macOS Keychain
	@echo "$(BLUE)Retrieving OpenAI API key from macOS Keychain...$(NC)"
	@uv run python3 ./keychain_helper.py get openai-api-key

delete-openai-key: check-uv ## Delete OpenAI API key from macOS Keychain
	@echo "$(BLUE)Deleting OpenAI API key from macOS Keychain...$(NC)"
	@uv run python3 ./keychain_helper.py delete openai-api-key
	@echo "$(GREEN)Done!$(NC)"

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
	uv run pytest -v -m performance
	@echo "$(GREEN)Performance tests complete!$(NC)"

run: check-uv ## Run the loan approval agent locally
	@echo "$(BLUE)Starting loan approval agent locally...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Warning: .env file not found. Creating from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(YELLOW)Please configure your API key using one of these methods:$(NC)"; \
		echo "$(GREEN)  1. (Recommended) Store in Keychain: make set-openai-key$(NC)"; \
		echo "$(GREEN)  2. (Alternative) Edit .env file with OPENAI_API_KEY$(NC)"; \
		echo "$(RED)Stopping - please configure API key before running$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Environment loaded from .env$(NC)"
	@echo "$(YELLOW)API key will be loaded from Keychain (if available) or .env$(NC)"
	@echo "$(YELLOW)API will be available at: http://localhost:8000$(NC)"
	@echo "$(YELLOW)API docs at: http://localhost:8000/docs$(NC)"
	cd agents/loan_approval/src && uv run python api.py

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
