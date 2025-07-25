import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PromptLoader:
    """Utility class for loading prompt templates from files."""
    
    def __init__(self, prompts_dir: str = "prompts"):
        """Initialize with prompts directory path."""
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))  # Go up from src/utils/ to project root
        self.prompts_dir = os.path.join(project_root, prompts_dir)
        
        if not os.path.exists(self.prompts_dir):
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
    
    def load_prompt(self, prompt_name: str) -> Optional[str]:
        """Load a prompt from a .prompt file."""
        try:
            prompt_file = os.path.join(self.prompts_dir, f"{prompt_name}.prompt")
            
            if not os.path.exists(prompt_file):
                logger.error(f"Prompt file not found: {prompt_file}")
                return None
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            logger.debug(f"Loaded prompt: {prompt_name}")
            return content
            
        except Exception as e:
            logger.error(f"Error loading prompt {prompt_name}: {str(e)}")
            return None
    
    def get_available_prompts(self) -> list[str]:
        """Get list of available prompt files."""
        try:
            if not os.path.exists(self.prompts_dir):
                return []
            
            prompt_files = [
                f[:-7]  # Remove .prompt extension
                for f in os.listdir(self.prompts_dir)
                if f.endswith('.prompt')
            ]
            return sorted(prompt_files)
            
        except Exception as e:
            logger.error(f"Error listing prompts: {str(e)}")
            return []


# Global prompt loader instance
prompt_loader = PromptLoader()
