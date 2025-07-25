# AI Agent Slack Bot

A modular AI agent Slack bot with interchangeable AI model providers. This bot supports OpenAI, Anthropic, and local Hugging Face models, allowing you to switch between different AI providers seamlessly.

## Features

- 🤖 **Multiple AI Providers**: Support for OpenAI, Anthropic, Google Gemini, and local Hugging Face models
- 🔄 **Hot-swappable Models**: Switch between AI providers without restarting
- 💬 **Slack Integration**: Full Slack bot functionality with mentions and direct messages
- 🧵 **Thread Support**: Intelligent thread replies with full context awareness
- 🌐 **REST API**: FastAPI-based API for external integrations
- 📊 **Health Monitoring**: Built-in health checks for AI models
- 🗂️ **Conversation Management**: Per-user conversation history tracking
- ⚙️ **Configuration-driven**: Easy setup through environment variables

## Architecture

```
src/
├── models/           # Abstract AI model interfaces
├── providers/        # AI provider implementations
├── agent/           # Core AI agent logic
├── slack/           # Slack bot implementation
├── api/             # FastAPI REST endpoints
└── config.py        # Configuration management
```

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <your-repo>
   cd ops_agent
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and Slack tokens
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

## Configuration

Create a `.env` file based on `.env.example`:

### Slack Configuration
```env
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
SLACK_APP_TOKEN=xapp-your-app-token-here
```

### AI Provider Configuration
```env
DEFAULT_AI_PROVIDER=openai  # openai, anthropic, gemini, local

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro

# Local Models
LOCAL_MODEL_PATH=microsoft/DialoGPT-medium
LOCAL_MODEL_TYPE=huggingface
```

## Slack Bot Commands

- `hello` - Greet the bot
- `models` - List available AI models and commands
- `switch to <provider>` - Switch to a different AI provider (openai, anthropic, gemini, local)
- `clear` - Clear conversation history
- `health` - Check current model health
- `@bot <message>` - Chat with the bot (mentions)
- Direct messages work automatically
- **Thread Replies** - The bot automatically participates in threads when mentioned or when replying to bot messages

### Thread Support Features

The bot intelligently handles Slack threads:

- **Full Context Awareness**: Reads the entire thread history before responding
- **Smart Thread Detection**: Automatically detects when to participate in threads
- **Contextual Responses**: Uses thread context to provide relevant answers
- **Thread Continuity**: Maintains conversation flow within threads
- **Individual History**: Still maintains per-user conversation history outside of threads

## REST API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /chat` - Send message to AI agent
- `GET /models` - List available models
- `POST /models/switch/{provider}` - Switch AI provider
- `DELETE /conversations/{user_id}` - Clear user conversation

### Example API Usage

```bash
# Chat with the AI agent
curl -X POST "http://localhost:3000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "user_id": "user123",
    "provider": "openai"
  }'

# Switch AI provider
curl -X POST "http://localhost:3000/models/switch/anthropic"

# Get available models
curl "http://localhost:3000/models"
```

## Development

### Adding New AI Providers

1. Create a new provider class in `src/providers/`:

```python
from ..models.base import AIModelInterface, AIMessage, AIResponse

class NewProviderModel(AIModelInterface):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Initialize your provider
    
    async def generate_response(self, messages: List[AIMessage], **kwargs) -> AIResponse:
        # Implement response generation
        pass
    
    async def health_check(self) -> bool:
        # Implement health check
        pass
    
    @property
    def model_name(self) -> str:
        return "your-model-name"
    
    @property
    def provider(self) -> str:
        return "new-provider"
```

2. Register in `ModelFactory` (`src/providers/__init__.py`):

```python
from .new_provider import NewProviderModel

class ModelFactory:
    _providers = {
        # ... existing providers
        "new-provider": NewProviderModel,
    }
```

3. Update configuration in `src/config.py` to support new provider settings.

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Environment Variables for Production

- Set `DEBUG=False`
- Use proper logging configuration
- Configure appropriate `HOST` and `PORT`
- Ensure all required API keys are set

## Slack App Setup

1. Create a new Slack app at https://api.slack.com/apps
2. Enable Socket Mode and generate an App Token
3. Add Bot Token Scopes:
   - `app_mentions:read`
   - `chat:write`
   - `channels:history` (for thread context)
   - `groups:history` (for private channel threads)
   - `im:history`
   - `im:read`
   - `im:write`
4. Install the app to your workspace
5. Copy the tokens to your `.env` file

## API Keys Setup

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add it to your `.env` file as `OPENAI_API_KEY`

### Anthropic
1. Go to https://console.anthropic.com/
2. Create an API key
3. Add it to your `.env` file as `ANTHROPIC_API_KEY`

### Google Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root directory
2. **Slack Connection**: Verify your tokens and internet connection
3. **AI Provider Errors**: Check API keys and model availability
4. **Memory Issues**: Local models require significant RAM (8GB+ recommended)

### Logging

Logs are written to both console and `app.log`. Set `LOG_LEVEL` in `.env` to control verbosity:
- `DEBUG` - Detailed information
- `INFO` - General information (default)
- `WARNING` - Warning messages only
- `ERROR` - Error messages only

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code passes linting and type checking
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
