.PHONY: install dev build preview clean help test test-ui test-debug

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make dev         - Start development server"
	@echo "  make build       - Build for production"
	@echo "  make preview     - Preview production build"
	@echo "  make test        - Run Playwright tests"
	@echo "  make test-ui     - Run Playwright tests in UI mode"
	@echo "  make test-debug  - Run Playwright tests in debug mode"
	@echo "  make clean       - Clean build artifacts and dependencies"

install:
	COREPACK_ENABLE_STRICT=0 pnpm install --no-frozen-lockfile

dev:
	COREPACK_ENABLE_STRICT=0 pnpm run dev

build:
	COREPACK_ENABLE_STRICT=0 pnpm run build

preview:
	COREPACK_ENABLE_STRICT=0 pnpm run preview

test:
	@echo "Running Playwright tests..."
	@echo "Make sure the dev server is running on port 3000"
	@SKIP_WEBSERVER=1 COREPACK_ENABLE_STRICT=0 pnpm run test

test-ui:
	@echo "Starting Playwright UI mode..."
	@SKIP_WEBSERVER=1 COREPACK_ENABLE_STRICT=0 pnpm run test:ui

test-debug:
	@echo "Starting Playwright debug mode..."
	@SKIP_WEBSERVER=1 COREPACK_ENABLE_STRICT=0 pnpm run test:debug

clean:
	rm -rf node_modules dist
	@echo "Cleaned build artifacts and dependencies"
