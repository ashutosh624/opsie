<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AI Agent Slack Bot - Copilot Instructions

This is an AI agent Slack bot project with interchangeable AI model providers. The project follows a modular architecture with the following key principles:

## Architecture Guidelines

1. **Modular AI Providers**: All AI model implementations must inherit from `AIModelInterface` in `src/models/base.py`
2. **Factory Pattern**: Use `ModelFactory` to create AI model instances
3. **Async Programming**: Use async/await for all I/O operations
4. **Configuration Management**: Use the `Config` class for environment variables and settings
5. **Type Hints**: Always include proper type hints for function parameters and return values
6. **Error Handling**: Implement proper exception handling with logging

## Code Style

- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Add docstrings to all classes and public methods
- Use structured logging with appropriate log levels
- Prefer composition over inheritance where possible

## Key Components

- `src/models/base.py`: Abstract interface for AI models
- `src/providers/`: AI model provider implementations (OpenAI, Anthropic, Local)
- `src/agent/ai_agent.py`: Main AI agent logic with conversation management
- `src/slack/slack_bot.py`: Slack bot integration using Bolt for Python
- `src/api/routes.py`: FastAPI REST endpoints
- `src/config.py`: Configuration management

## Testing

- Write unit tests for all new functionality
- Mock external API calls in tests
- Test error conditions and edge cases
- Use pytest for testing framework

## New Provider Implementation

When adding new AI providers:
1. Create a new file in `src/providers/`
2. Implement the `AIModelInterface`
3. Register the provider in `ModelFactory`
4. Update configuration to support the new provider
5. Add appropriate error handling and logging
