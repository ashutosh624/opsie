import asyncio
import logging
import sys
from typing import Optional

from src.slack.slack_bot import SlackBot
from src.api.routes import app
from src.config import config
import uvicorn

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)


async def run_slack_bot():
    """Run the Slack bot."""
    try:
        logger.info("Starting Slack bot...")
        slack_bot = SlackBot()
        await slack_bot.start()
    except Exception as e:
        logger.error(f"Failed to start Slack bot: {str(e)}")
        raise


def run_api_server():
    """Run the FastAPI server."""
    logger.info(f"Starting API server on {config.host}:{config.port}")
    uvicorn.run(
        "main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level=config.log_level.lower()
    )


async def main():
    """Main entry point."""
    logger.info("Starting AI Agent Slack Bot...")

    # Validate configuration
    if not config.validate_required_config():
        logger.error("Configuration validation failed. Please check your .env file.")
        sys.exit(1)

    # Print current configuration (without sensitive data)
    logger.info(f"Default AI Provider: {config.default_ai_provider}")
    logger.info(f"Server: {config.host}:{config.port}")
    logger.info(f"Debug Mode: {config.debug}")

    # Choose run mode based on configuration
    mode = input("Run mode - (1) Slack bot only, (2) API server only, (3) Both [default: 3]: ").strip()

    if mode == "1":
        await run_slack_bot()
    elif mode == "2":
        run_api_server()
    else:
        # Run both Slack bot and API server
        logger.info("Starting both Slack bot and API server...")

        # Create tasks for both services
        slack_task = asyncio.create_task(run_slack_bot())

        # Run API server in a separate thread since uvicorn.run is blocking
        import threading
        api_thread = threading.Thread(target=run_api_server)
        api_thread.daemon = True
        api_thread.start()

        # Wait for Slack bot
        await slack_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
