"""
Evaluation Runner for AI Agent
Processes threads from CSV file through the AI agent and stores results.
"""

import asyncio
import csv
import logging
import os
import sys
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.ai_agent import AIAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvaluationRunner:
    """Runs evaluation on threads from CSV file using AI agent."""

    def __init__(self, input_csv_path: str, output_csv_path: Optional[str] = None):
        """
        Initialize evaluation runner.

        Args:
            input_csv_path: Path to input CSV file with threads
            output_csv_path: Path to output CSV file (optional, defaults to timestamped file)
        """
        self.input_csv_path = input_csv_path

        if output_csv_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_csv_path = f"eval/evaluation_results_{timestamp}.csv"
        else:
            self.output_csv_path = output_csv_path

        self.ai_agent = None
        self.processed_count = 0
        self.error_count = 0

    async def initialize_agent(self, provider: Optional[str] = None) -> None:
        """Initialize the AI agent with specified provider."""
        try:
            self.ai_agent = AIAgent(default_provider=provider)
            logger.info("AI Agent initialized with provider: %s", self.ai_agent.default_provider)
        except Exception as e:
            logger.error("Failed to initialize AI agent: %s", str(e))
            raise

    def read_input_csv(self) -> List[Dict[str, str]]:
        """
        Read threads from input CSV file.

        Returns:
            List of dictionaries with thread data
        """
        threads = []

        try:
            with open(self.input_csv_path, 'r', encoding='utf-8') as file:
                # Use csv.Sniffer to detect delimiter
                # sample = file.read(1024)
                file.seek(0)
                # sniffer = csv.Sniffer()
                delimiter = ','

                reader = csv.DictReader(file, delimiter=delimiter)

                for i, row in enumerate(reader):
                    if 'Thread' in row and row['Thread'].strip():
                        threads.append({
                            'index': i + 1,
                            'thread': row['Thread'].strip(),
                            'existing_category': row.get('Predicted category', '').strip(),
                            'existing_response': row.get('AI Response', '').strip(),
                            'remarks': row.get('Remarks', '').strip()
                        })

            logger.info("Successfully read %d threads from %s", len(threads), self.input_csv_path)
            return threads

        except (IOError, csv.Error) as e:
            logger.error("Error reading input CSV: %s", str(e))
            raise

    async def process_single_thread(self, thread_data: Dict[str, str]) -> Tuple[str, str]:
        """
        Process a single thread through the AI agent.

        Args:
            thread_data: Dictionary containing thread information

        Returns:
            Tuple of (predicted_category, ai_response)
        """
        try:
            thread_content = thread_data['thread']
            user_id = f"eval_user_{thread_data['index']}"

            # Create minimal thread context (empty list for single message evaluation)
            thread_context = []

            # Process the thread message
            ai_response = await self.ai_agent.process_thread_message(
                user_id=user_id,
                message=thread_content,
                thread_context=thread_context
            )

            # Extract the category from the latest categorization
            # We need to access the categorizer to get the last category
            # For now, we'll extract it from logs or implement a way to get it
            predicted_category = await self._get_last_categorization(thread_content, thread_context)

            logger.info("Thread %d: Category='%s', Response length=%d",
                       thread_data['index'], predicted_category, len(ai_response))

            return predicted_category, ai_response

        except (ValueError, RuntimeError, OSError) as e:
            logger.error("Error processing thread %d: %s", thread_data['index'], str(e))
            return "ERROR", f"Error processing thread: {str(e)}"

    async def _get_last_categorization(self, message: str, thread_context: List[Dict[str, Any]]) -> str:
        """
        Get the category for a message using the request categorizer.

        Args:
            message: The message content
            thread_context: Thread context

        Returns:
            The predicted category as string
        """
        try:
            from src.utils.request_categorizer import RequestCategorizer

            if self.ai_agent is None or self.ai_agent.current_model is None:
                logger.error("AI agent or model not initialized")
                return "unknown"

            category = await RequestCategorizer.categorize_request_async(
                message, thread_context, self.ai_agent.current_model
            )
            return category.value

        except (ValueError, RuntimeError, AttributeError) as e:
            logger.error("Error getting categorization: %s", str(e))
            return "unknown"

    def write_output_csv(self, results: List[Dict[str, Any]]) -> None:
        """
        Write results to output CSV file.

        Args:
            results: List of result dictionaries
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.output_csv_path), exist_ok=True)

            with open(self.output_csv_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = [
                    'Thread',
                    'Predicted category',
                    'AI Response',
                    'Remarks',
                    'Processing Status',
                    'Timestamp'
                ]

                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                for result in results:
                    writer.writerow(result)

            logger.info("Results written to %s", self.output_csv_path)

        except (IOError, csv.Error) as e:
            logger.error("Error writing output CSV: %s", str(e))
            raise

    async def run_evaluation(self, provider: Optional[str] = None, max_threads: Optional[int] = None) -> None:
        """
        Run the complete evaluation process.

        Args:
            provider: AI provider to use (optional)
            max_threads: Maximum number of threads to process (optional, for testing)
        """
        logger.info("Starting evaluation...")

        # Initialize AI agent
        await self.initialize_agent(provider)

        # Read input threads
        threads = self.read_input_csv()

        if max_threads:
            threads = threads[:max_threads]
            logger.info("Limited to first %d threads for testing", max_threads)

        # Process threads
        results = []

        for i, thread_data in enumerate(threads, 1):
            logger.info("Processing thread %d/%d", i, len(threads))

            try:
                predicted_category, ai_response = await self.process_single_thread(thread_data)

                result = {
                    'Thread': thread_data['thread'],
                    'Predicted category': predicted_category,
                    'AI Response': ai_response,
                    'Remarks': thread_data['remarks'],
                    'Processing Status': 'SUCCESS',
                    'Timestamp': datetime.now().isoformat()
                }

                self.processed_count += 1

            except (ValueError, RuntimeError, OSError) as e:
                logger.error("Failed to process thread %d: %s", i, str(e))

                result = {
                    'Thread': thread_data['thread'],
                    'Predicted category': 'ERROR',
                    'AI Response': f"Processing failed: {str(e)}",
                    'Remarks': thread_data['remarks'],
                    'Processing Status': 'ERROR',
                    'Timestamp': datetime.now().isoformat()
                }

                self.error_count += 1

            results.append(result)

            # Add small delay to avoid rate limiting
            await asyncio.sleep(1)

        # Write results
        self.write_output_csv(results)

        # Print summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print evaluation summary."""
        total_threads = self.processed_count + self.error_count

        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Total threads processed: {total_threads}")
        print(f"Successful: {self.processed_count}")
        print(f"Errors: {self.error_count}")
        print(f"Success rate: {(self.processed_count/total_threads)*100:.1f}%" if total_threads > 0 else "N/A")
        print(f"Results saved to: {self.output_csv_path}")
        print("="*60)


async def main():
    """Main function to run evaluation."""

    # Configuration
    input_csv_path = "eval/slack_threads.csv"
    provider = None  # Use default provider from config
    max_threads = None  # Process all threads (set to small number for testing)

    # For testing, you can limit to first few threads:
    # max_threads = 5

    try:
        # Create and run evaluation
        runner = EvaluationRunner(input_csv_path)
        await runner.run_evaluation(provider=provider, max_threads=max_threads)

    except (ValueError, RuntimeError, OSError) as e:
        logger.error("Evaluation failed: %s", str(e))
        print(f"\nEvaluation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
