"""Template loader utility for response templates."""

import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ResponseTemplateLoader:
    """Loads and manages response templates from files."""
    
    def __init__(self, templates_directory: Optional[str] = None):
        """Initialize template loader.
        
        Args:
            templates_directory: Path to templates directory. If None, uses default.
        """
        if templates_directory:
            self.templates_dir = Path(templates_directory)
        else:
            # Default to response_templates in project root
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent  # Go up from src/utils/
            self.templates_dir = project_root / "response_templates"
        
        self._template_cache: Dict[str, str] = {}
    
    def load_template(self, template_name: str) -> Optional[str]:
        """Load a template by name.
        
        Args:
            template_name: Name of the template file (without .txt extension)
            
        Returns:
            Template content as string, or None if not found
        """
        # Check cache first
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        template_file = self.templates_dir / f"{template_name}.txt"
        
        try:
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                # Cache the template
                self._template_cache[template_name] = content
                return content
            else:
                logger.warning(f"Template file not found: {template_file}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {str(e)}")
            return None
    
    def format_template(self, template_name: str, **kwargs) -> Optional[str]:
        """Load and format a template with variables.
        
        Args:
            template_name: Name of the template file
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted template content, or None if template not found
        """
        template = self.load_template(template_name)
        if not template:
            return None
        
        try:
            # Handle conditional sections
            formatted = self._process_conditional_content(template, **kwargs)
            
            # Format with provided variables
            return formatted.format(**kwargs)
            
        except KeyError as e:
            logger.error(f"Missing template variable {e} for template {template_name}")
            return template  # Return unformatted template as fallback
        except Exception as e:
            logger.error(f"Error formatting template {template_name}: {str(e)}")
            return template  # Return unformatted template as fallback
    
    def _process_conditional_content(self, template: str, **kwargs) -> str:
        """Process conditional content in templates.
        
        Args:
            template: Template content
            **kwargs: Variables for evaluation
            
        Returns:
            Template with conditional content processed
        """
        # Handle missing_info_list for technical_issue template
        if "missing_info_list" in template:
            missing_info = kwargs.get("missing_info", [])
            if missing_info:
                info_list = "\n".join([f"• {info}" for info in missing_info])
                kwargs["missing_info_list"] = info_list
            else:
                # Remove the missing info section entirely
                lines = template.split('\n')
                filtered_lines = []
                skip_missing_info = False
                
                for line in lines:
                    if "Missing Information" in line:
                        skip_missing_info = True
                        continue
                    elif skip_missing_info and line.strip() == "":
                        skip_missing_info = False
                        continue
                    elif skip_missing_info and line.startswith("Please provide"):
                        continue
                    elif not skip_missing_info:
                        filtered_lines.append(line)
                
                template = '\n'.join(filtered_lines)
                kwargs["missing_info_list"] = ""
        
        # Handle confluence_note for engineering_query template
        if "confluence_note" in template:
            text = kwargs.get("text", "").lower()
            if "confluence" in text:
                kwargs["confluence_note"] = "I'll check our Confluence documentation for relevant context."
            else:
                kwargs["confluence_note"] = ""
        
        # Handle df_owned_note for engineering_query template
        if "df_owned_note" in template:
            text = kwargs.get("text", "").lower()
            if "df-owned" in text or "df owned" in text:
                kwargs["df_owned_note"] = "This relates to DF-owned components. I'll provide technical guidance."
            else:
                kwargs["df_owned_note"] = ""
        
        # Handle jira_note for fyi template
        if "jira_note" in template:
            text = kwargs.get("text", "").lower()
            if "jira" in text:
                kwargs["jira_note"] = "I see this relates to a Jira ticket. I'll track any follow-up actions needed."
            else:
                kwargs["jira_note"] = ""
        
        return template
    
    def list_available_templates(self) -> list:
        """List all available template files.
        
        Returns:
            List of template names (without .txt extension)
        """
        try:
            if not self.templates_dir.exists():
                return []
            
            return [
                f.stem for f in self.templates_dir.glob("*.txt")
                if f.is_file()
            ]
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            return []
    
    def clear_cache(self):
        """Clear the template cache."""
        self._template_cache.clear()


# Global template loader instance
template_loader = ResponseTemplateLoader()
