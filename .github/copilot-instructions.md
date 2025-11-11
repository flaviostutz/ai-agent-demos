# Copilot Instructions

## Tooling
  - Always use commands from makefiles when available
  - Use Makefiles as the entry point for commands for CI/CD, running agents, tests, linting, setup, etc. Add commands to Makefiles as needed, but only commands that would be reused more often.
  - Python tooling is done via "uv"
  - Javasript tooling is done via "pnpm"

## Quality
  - Create unit tests for new features and bug fixes, and ensure all tests pass
  - Run "make all" everytime you make changes to ensure lint, test and build is working fine. Fix any issues.
  - Always run the commands or features you are creating or modifying to ensure they work as expected and fix any issues

## Stack
  - For LLM, agents and ML related code, use Python
  - For frontend development, use JavaScript/TypeScript with ReactJS and Vite

## Conventions
  - Use .test in file name for tests, instead of .spec
