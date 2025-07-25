#!/bin/bash

# AI Agent Slack Bot Setup Script

echo "🤖 Setting up AI Agent Slack Bot..."

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from .env.example"
    echo "⚠️  Please edit .env file with your API keys and Slack tokens"
else
    echo "✅ .env file already exists"
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys and Slack tokens"
echo "2. Create a Slack app and get tokens (see README.md)"
echo "3. Run: python main.py"
echo ""
echo "📚 Available commands:"
echo "  python main.py          - Start the bot"
echo "  pytest tests/           - Run tests"
echo "  black src/              - Format code"
echo "  flake8 src/             - Lint code"
