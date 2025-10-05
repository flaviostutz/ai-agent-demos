#!/bin/bash
# Quick start script for AI Agent platform

set -e

echo "🚀 AI Agent Platform - Quick Start"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python 3.11+ required. You have: $python_version"
    exit 1
fi
echo "✅ Python $python_version"

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo ""
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi
echo "✅ Poetry installed"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
poetry install --no-interaction

# Setup pre-commit hooks
echo ""
echo "🔧 Setting up pre-commit hooks..."
poetry run pre-commit install

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys"
fi

# Generate loan documents
echo ""
echo "📄 Generating loan approval documents..."
poetry run python scripts/generate_loan_docs.py

# Load documents to vector store
echo ""
echo "🔍 Loading documents to vector store..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set. Skipping vector store setup."
    echo "   Set your OpenAI key and run: make load-docs"
else
    poetry run python scripts/load_documents.py
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys (OPENAI_API_KEY, etc.)"
echo "2. Run: export OPENAI_API_KEY='your-key-here'"
echo "3. If not done yet, run: make load-docs"
echo "4. Start the agent: make dev"
echo "5. Visit http://localhost:8000/docs"
echo ""
echo "Commands:"
echo "  make dev              - Run agent locally"
echo "  make test             - Run tests"
echo "  make lint             - Check code quality"
echo "  make create-agent     - Create new agent"
echo "  make help             - Show all commands"
echo ""
echo "Happy coding! 🎉"
