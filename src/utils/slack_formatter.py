"""
Slack message formatting utilities.
"""

import re
from typing import Dict, Any, List, Optional


class SlackFormatter:
    """Utility class for formatting messages for Slack."""
    
    @staticmethod
    def format_response(text: str) -> str:
        """Convert markdown-style text to Slack mrkdwn format."""
        # Convert **bold** to *bold*
        text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
        
        # Convert __italic__ to _italic_
        text = re.sub(r'__(.*?)__', r'_\1_', text)
        
        # Convert `code` to `code` (already correct for Slack)
        # No change needed for inline code
        
        # Convert ```code block``` to ```code block``` (already correct)
        # No change needed for code blocks
        
        # Convert # Headers to *Headers*
        text = re.sub(r'^#{1,6}\s*(.*?)$', r'*\1*', text, flags=re.MULTILINE)
        
        # Convert - list items to • list items
        text = re.sub(r'^[\-\*]\s+', '• ', text, flags=re.MULTILINE)
        
        # Convert numbered lists to better format
        text = re.sub(r'^\d+\.\s+', '• ', text, flags=re.MULTILINE)
        
        return text
    
    @staticmethod
    def create_blocks(text: str, title: Optional[str] = None) -> List[Dict[str, Any]]:
        """Create Slack Block Kit blocks for rich formatting."""
        blocks = []
        
        # Add title if provided
        if title:
            blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            })
        
        # Split text into sections for better formatting
        sections = text.split('\n\n')
        
        for section in sections:
            if section.strip():
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": SlackFormatter.format_response(section.strip())
                    }
                })
        
        return blocks
    
    @staticmethod
    def create_model_list_blocks(available_providers: List[str], current_model: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create specialized blocks for model listing."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 Available AI Models"
                }
            },
            {
                "type": "section",
                "fields": []
            }
        ]
        
        # Add provider fields
        for provider in available_providers:
            emoji = "✅" if provider == current_model["provider"] else "⚪"
            blocks[1]["fields"].append({
                "type": "mrkdwn",
                "text": f"{emoji} *{provider.title()}*"
            })
        
        # Add current model info
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Current Model:* {current_model['provider']} - `{current_model['model']}`"
            }
        })
        
        # Add commands section
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Commands:*\n• `switch to <provider>` - Switch AI model\n• `clear` - Clear conversation history\n• `health` - Check model health\n• `models` - Show this list"
            }
        })
        
        return blocks
    
    @staticmethod
    def create_error_block(error_message: str) -> List[Dict[str, Any]]:
        """Create an error message block."""
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"❌ *Error:* {error_message}"
                }
            }
        ]
    
    @staticmethod
    def create_success_block(message: str) -> List[Dict[str, Any]]:
        """Create a success message block."""
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ {message}"
                }
            }
        ]
    
    @staticmethod
    def truncate_for_slack(text: str, max_length: int = 3000) -> str:
        """Truncate text to fit within Slack's message limits."""
        if len(text) <= max_length:
            return text
        
        # Try to truncate at a natural break
        truncated = text[:max_length]
        last_newline = truncated.rfind('\n')
        
        if last_newline > max_length * 0.8:  # If we can find a newline in the last 20%
            truncated = truncated[:last_newline]
        
        return truncated + "\n\n... (message truncated)"
    
    @staticmethod
    def format_code_block(code: str, language: str = "") -> str:
        """Format code block for Slack."""
        return f"```{language}\n{code}\n```"
    
    @staticmethod
    def escape_slack_formatting(text: str) -> str:
        """Escape special Slack formatting characters."""
        # Escape Slack special characters
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
