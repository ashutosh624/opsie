"""
Test script for evaluation runner - processes just a few threads for testing.
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval.evaluation_runner import EvaluationRunner


async def test_evaluation():
    """Test the evaluation with just a few threads."""
    max_threads = 1000  # Test with just 3 threads
    print(f"🧪 Testing Evaluation Runner with first {max_threads} threads...")

    # Configuration for testing
    input_csv_path = "eval/slack_threads.csv"

    provider = os.getenv("DEFAULT_AI_PROVIDER", "openai")  # Use default provider

    try:
        # Create and run evaluation
        runner = EvaluationRunner(input_csv_path)
        await runner.run_evaluation(provider=provider, max_threads=max_threads)

        print("✅ Test completed successfully!")

    except (ValueError, RuntimeError, OSError) as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_evaluation())
