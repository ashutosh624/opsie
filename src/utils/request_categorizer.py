"""
Request categorization and routing system for Slack bot.
"""

import re
import json
from typing import Dict, Any, List
from enum import Enum
import logging
from ..models.base import AIMessage
from ..utils.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)


class RequestCategory(Enum):
    """Categories for incoming requests."""
    TECHNICAL_ISSUE = "technical_issue"
    FYI = "fyi"
    CUSTOMER_QUERY = "customer_query"
    ENGINEERING_QUERY = "engineering_query"
    FEATURE_REQUEST = "feature_request"
    FEATURE_ENABLEMENT = "feature_enablement"
    PR_REVIEW = "pr_review"
    UNKNOWN = "unknown"


class RequestCategorizer:
    """Categorizes and routes requests based on content and context."""
    
    # Keywords and patterns for categorization
    CATEGORY_PATTERNS = {
        RequestCategory.TECHNICAL_ISSUE: [
            r'\b(error|bug|issue|problem|fail|broken|crash|not working)\b',
            r'\b(stack trace|exception|timeout|500|404|502|503)\b',
            r'\b(debug|troubleshoot|investigate)\b',
            r'\b(reproduce|repro|steps)\b'
        ],
        RequestCategory.FYI: [
            r'\bfyi\b',
            r'\bfor your information\b',
            r'\bheads up\b',
            r'\bjira\b.*\b(ticket|issue)\b',
            r'\bupdate\b.*\bon\b',
            r'\bjust wanted to let you know\b'
        ],
        RequestCategory.CUSTOMER_QUERY: [
            r'\bcustomer\b.*\b(ask|question|query|request)\b',
            r'\bclient\b.*\b(ask|question|query|request)\b',
            r'\buser\b.*\b(ask|question|query|request)\b',
            r'\bhow\s+do\s+customers?\b',
            r'\bcan\s+customers?\b'
        ],
        RequestCategory.ENGINEERING_QUERY: [
            r'\binternal\b.*\b(team|query|question)\b',
            r'\bengineering\b.*\b(team|query|question)\b',
            r'\bconfluence\b',
            r'\bdf-owned\b',
            r'\bdf\s+owned\b',
            r'\bknowledge\s+transfer\b',
            r'\bkt\s+docs?\b'
        ],
        RequestCategory.FEATURE_REQUEST: [
            r'\bnew\s+feature\b',
            r'\bfeature\s+request\b',
            r'\bcustomer\b.*\b(want|need|request)\b.*\bfeature\b',
            r'\bcan\s+we\s+add\b',
            r'\bwould\s+it\s+be\s+possible\b',
            r'\benhancement\b'
        ],
        RequestCategory.FEATURE_ENABLEMENT: [
            r'\benable\b.*\bfeature\b',
            r'\bfeature\b.*\b(enable|activation|turn\s+on)\b',
            r'\bvalidate\b.*\bfeature\s+support\b',
            r'\bfeature\s+flag\b',
            r'\btoggle\b.*\bfeature\b'
        ],
        RequestCategory.PR_REVIEW: [
            r'\bpr\s+review\b',
            r'\bpull\s+request\b.*\breview\b',
            r'\bcode\s+review\b',
            r'\breview\b.*\bpr\b',
            r'\bmobile-pr-reviews\b'
        ]
    }
    
    # Routing information for each category
    ROUTING_INFO = {
        RequestCategory.TECHNICAL_ISSUE: {
            "action": "validate_and_triage",
            "route_to": "ops_debugging",
            "priority": "high",
            "required_info": [
                "Problem description",
                "Steps to reproduce", 
                "Expected vs actual behavior",
                "Environment details",
                "Error messages/logs"
            ]
        },
        RequestCategory.FYI: {
            "action": "acknowledge",
            "route_to": "ops_team",
            "priority": "low",
            "required_info": []
        },
        RequestCategory.CUSTOMER_QUERY: {
            "action": "route_to_product",
            "route_to": "df_product",
            "priority": "medium",
            "required_info": ["Customer context", "Specific query details"]
        },
        RequestCategory.ENGINEERING_QUERY: {
            "action": "respond_directly",
            "route_to": "df_ops",
            "priority": "medium",
            "required_info": ["Technical context", "Component details"]
        },
        RequestCategory.FEATURE_REQUEST: {
            "action": "verify_and_route",
            "route_to": "df_product", 
            "priority": "medium",
            "required_info": ["Customer demand details", "Feature description"]
        },
        RequestCategory.FEATURE_ENABLEMENT: {
            "action": "verify_and_route",
            "route_to": "df_product",
            "priority": "medium", 
            "required_info": ["Feature details", "Support validation"]
        },
        RequestCategory.PR_REVIEW: {
            "action": "redirect",
            "route_to": "mobile_pr_reviews",
            "priority": "low",
            "required_info": []
        }
    }
    
    @classmethod
    async def categorize_request_async(cls, text: str, thread_context: List[Dict[str, Any]] | None = None, ai_model=None) -> RequestCategory:
        """Async version of categorize_request for use in async contexts."""
        
        # First, get regex-based score
        regex_category = cls._categorize_with_regex(text, thread_context)
        
        # If we have an AI model, use LLM for enhanced categorization
        if ai_model:
            try:
                llm_category = await cls._categorize_with_llm_async(text, thread_context, ai_model)
                
                # Combine both approaches - if they agree, use that. If they disagree, prioritize LLM
                if llm_category != RequestCategory.UNKNOWN:
                    if regex_category == RequestCategory.UNKNOWN or llm_category == regex_category:
                        logger.info(f"LLM categorization: {llm_category.value} (regex: {regex_category.value})")
                        return llm_category
                    else:
                        # Both have opinions but disagree - log and use LLM
                        logger.info(f"Categorization mismatch - LLM: {llm_category.value}, Regex: {regex_category.value}. Using LLM.")
                        return llm_category
                        
            except Exception as e:
                logger.error(f"LLM categorization failed: {str(e)}, falling back to regex")
        
        # Fall back to regex-based categorization
        return regex_category

    @classmethod
    async def _categorize_with_llm_async(cls, text: str, thread_context: List[Dict[str, Any]] | None = None, ai_model=None) -> RequestCategory:
        """Async LLM-based categorization for more accurate results."""
        
        if not ai_model:
            return RequestCategory.UNKNOWN
            
        # Build the categorization prompt
        categorization_prompt = cls._build_categorization_prompt(text, thread_context)
        
        # Create messages for the AI model
        messages = [
            AIMessage(role="system", content=categorization_prompt),
            AIMessage(role="user", content=f"Categorize this request: {text}")
        ]
        
        try:
            # Generate response using our AI model interface
            response = await ai_model.generate_response(messages, max_tokens=1024)
            
            # Parse the response to extract category
            category_text = response.content.strip().lower()
            
            # Map LLM response to enum
            category_mapping = {
                "technical_issue": RequestCategory.TECHNICAL_ISSUE,
                "technical issue": RequestCategory.TECHNICAL_ISSUE,
                "fyi": RequestCategory.FYI,
                "customer_query": RequestCategory.CUSTOMER_QUERY,
                "customer query": RequestCategory.CUSTOMER_QUERY,
                "engineering_query": RequestCategory.ENGINEERING_QUERY,
                "engineering query": RequestCategory.ENGINEERING_QUERY,
                "feature_request": RequestCategory.FEATURE_REQUEST,
                "feature request": RequestCategory.FEATURE_REQUEST,
                "feature_enablement": RequestCategory.FEATURE_ENABLEMENT,
                "feature enablement": RequestCategory.FEATURE_ENABLEMENT,
                "pr_review": RequestCategory.PR_REVIEW,
                "pr review": RequestCategory.PR_REVIEW,
                "unknown": RequestCategory.UNKNOWN
            }
            
            # Try to extract category from response
            for key, category in category_mapping.items():
                if key in category_text:
                    return category
                    
            # If no direct match, try JSON parsing
            if "{" in category_text and "}" in category_text:
                try:
                    parsed = json.loads(category_text)
                    category_value = parsed.get("category", "").lower()
                    return category_mapping.get(category_value, RequestCategory.UNKNOWN)
                except json.JSONDecodeError:
                    pass
            
            logger.warning(f"Could not parse LLM categorization response: {category_text}")
            return RequestCategory.UNKNOWN
            
        except Exception as e:
            logger.error(f"LLM categorization error: {str(e)}")
            return RequestCategory.UNKNOWN

    @classmethod
    def categorize_request(cls, text: str, thread_context: List[Dict[str, Any]] | None = None, ai_model=None) -> RequestCategory:
        """Sync wrapper for categorize_request - uses only regex for simplicity.""" 
        return cls._categorize_with_regex(text, thread_context)

    @classmethod
    def _categorize_with_regex(cls, text: str, thread_context: List[Dict[str, Any]] | None = None) -> RequestCategory:
        """Original regex-based categorization logic."""
        text_lower = text.lower()
        
        # Check patterns for each category
        category_scores = {}
        
        for category, patterns in cls.CATEGORY_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                category_scores[category] = score
        
        # Also check thread context if available
        if thread_context:
            for msg in thread_context:
                msg_text = msg.get('text', '').lower()
                for category, patterns in cls.CATEGORY_PATTERNS.items():
                    for pattern in patterns:
                        matches = len(re.findall(pattern, msg_text, re.IGNORECASE))
                        category_scores[category] = category_scores.get(category, 0) + (matches * 0.5)
        
        # Return category with highest score, or UNKNOWN if no matches
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            return best_category
        
        return RequestCategory.UNKNOWN

    @classmethod
    def _categorize_with_llm(cls, text: str, thread_context: List[Dict[str, Any]] | None = None, ai_model=None) -> RequestCategory:
        """LLM-based categorization for more accurate results."""
        
        if not ai_model:
            return RequestCategory.UNKNOWN
            
        # Build the categorization prompt
        categorization_prompt = cls._build_categorization_prompt(text, thread_context)
        
        # Create messages for the AI model
        messages = [
            AIMessage(role="system", content=categorization_prompt),
            AIMessage(role="user", content=f"Categorize this request: {text}")
        ]
        
        try:
            # Generate response using our AI model interface
            import asyncio
            
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, but need to handle sync call
                # For now, skip LLM categorization in async context to avoid complexity
                logger.info("Skipping LLM categorization in async context")
                return RequestCategory.UNKNOWN
            except RuntimeError:
                # We're not in an async context, can proceed with sync call
                pass
            
            # Use a simplified approach for categorization
            simple_prompt = f"{categorization_prompt}\n\nRequest: {text}\n\nCategory:"
            
            # For Gemini model, use direct generate_content
            if hasattr(ai_model, 'model') and hasattr(ai_model.model, 'generate_content'):
                response = ai_model.model.generate_content(simple_prompt)
                category_text = response.text.strip().lower()
            else:
                # Fallback - return unknown for unsupported models
                logger.warning("AI model doesn't support direct categorization")
                return RequestCategory.UNKNOWN
            
            # Map LLM response to enum
            category_mapping = {
                "technical_issue": RequestCategory.TECHNICAL_ISSUE,
                "technical issue": RequestCategory.TECHNICAL_ISSUE,
                "fyi": RequestCategory.FYI,
                "customer_query": RequestCategory.CUSTOMER_QUERY,
                "customer query": RequestCategory.CUSTOMER_QUERY,
                "engineering_query": RequestCategory.ENGINEERING_QUERY,
                "engineering query": RequestCategory.ENGINEERING_QUERY,
                "feature_request": RequestCategory.FEATURE_REQUEST,
                "feature request": RequestCategory.FEATURE_REQUEST,
                "feature_enablement": RequestCategory.FEATURE_ENABLEMENT,
                "feature enablement": RequestCategory.FEATURE_ENABLEMENT,
                "pr_review": RequestCategory.PR_REVIEW,
                "pr review": RequestCategory.PR_REVIEW,
                "unknown": RequestCategory.UNKNOWN
            }
            
            # Try to extract category from response
            for key, category in category_mapping.items():
                if key in category_text:
                    return category
                    
            # If no direct match, try JSON parsing
            if "{" in category_text and "}" in category_text:
                try:
                    parsed = json.loads(category_text)
                    category_value = parsed.get("category", "").lower()
                    return category_mapping.get(category_value, RequestCategory.UNKNOWN)
                except json.JSONDecodeError:
                    pass
            
            logger.warning(f"Could not parse LLM categorization response: {category_text}")
            return RequestCategory.UNKNOWN
            
        except Exception as e:
            logger.error(f"LLM categorization error: {str(e)}")
            return RequestCategory.UNKNOWN

    @classmethod
    def _build_categorization_prompt(cls, text: str, thread_context: List[Dict[str, Any]] | None = None) -> str:
        """Build prompt for LLM categorization."""
        
        # Load base prompt from file
        base_prompt = prompt_loader.load_prompt("request_categorization")
        
        if not base_prompt:
            # Fallback prompt if file loading fails
            logger.warning("Failed to load request categorization prompt, using fallback")
            base_prompt = """You are an expert at categorizing customer engineering requests. 
            Categorize the following request as: TECHNICAL_ISSUE, FYI, CUSTOMER_QUERY, ENGINEERING_QUERY, 
            FEATURE_REQUEST, FEATURE_ENABLEMENT, PR_REVIEW, or UNKNOWN."""
        
        # Add thread context if available
        if thread_context:
            base_prompt += "\n\n**Thread Context:**\n"
            for i, msg in enumerate(thread_context[-3:], 1):  # Last 3 messages for context
                base_prompt += f"{i}. {msg.get('text', '')}\n"
        
        return base_prompt
    
    @classmethod
    def get_routing_info(cls, category: RequestCategory) -> Dict[str, Any]:
        """Get routing information for a category."""
        return cls.ROUTING_INFO.get(category, {
            "action": "acknowledge",
            "route_to": "ops_team",
            "priority": "medium",
            "required_info": []
        })
    
    @classmethod
    def generate_response(cls, category: RequestCategory, text: str, thread_context: List[Dict[str, Any]] | None = None) -> str:
        """Generate appropriate response based on category."""
        routing_info = cls.get_routing_info(category)
        
        if category == RequestCategory.TECHNICAL_ISSUE:
            return cls._generate_technical_issue_response(routing_info, text, thread_context)
        elif category == RequestCategory.FYI:
            return cls._generate_fyi_response(routing_info, text)
        elif category == RequestCategory.CUSTOMER_QUERY:
            return cls._generate_customer_query_response(routing_info, text)
        elif category == RequestCategory.ENGINEERING_QUERY:
            return cls._generate_engineering_query_response(routing_info, text)
        elif category == RequestCategory.FEATURE_REQUEST:
            return cls._generate_feature_request_response(routing_info, text)
        elif category == RequestCategory.FEATURE_ENABLEMENT:
            return cls._generate_feature_enablement_response(routing_info, text)
        elif category == RequestCategory.PR_REVIEW:
            return cls._generate_pr_review_response(routing_info, text)
        else:
            return cls._generate_unknown_response(text)
    
    @staticmethod
    def _generate_technical_issue_response(routing_info: Dict[str, Any], text: str, thread_context: List[Dict[str, Any]] | None = None) -> str:
        """Generate response for technical issues."""
        response = "🔧 **Technical Issue Detected**\n\n"
        response += "I'm triaging this technical issue and will validate the debugging information.\n\n"
        
        # Check for missing debugging info
        required_info = routing_info.get("required_info", [])
        missing_info = []
        
        text_lower = text.lower()
        if "reproduce" not in text_lower and "repro" not in text_lower:
            missing_info.append("Steps to reproduce")
        if "error" not in text_lower and "exception" not in text_lower:
            missing_info.append("Error messages/logs")
        if "environment" not in text_lower and "version" not in text_lower:
            missing_info.append("Environment details")
        
        if missing_info:
            response += "⚠️ **Missing Information:**\n"
            for info in missing_info:
                response += f"• {info}\n"
            response += "\nPlease provide the missing details for proper debugging. "
            response += "The complete debugging format is available in the channel description.\n\n"
        
        response += f"**Priority:** {routing_info.get('priority', 'medium').title()}\n"
        response += f"**Routing:** {routing_info.get('route_to', 'ops_debugging').replace('_', ' ').title()}\n"
        response += f"**Action:** {routing_info.get('action', 'validate_and_triage').replace('_', ' ').title()}"
        
        return response
    
    @staticmethod
    def _generate_fyi_response(routing_info: Dict[str, Any], text: str) -> str:
        """Generate response for FYI messages."""
        response = "📋 **FYI Acknowledged**\n\n"
        response += "Thank you for the update. I've noted this information.\n\n"
        
        if "jira" in text.lower():
            response += "I see this relates to a Jira ticket. I'll track any follow-up actions needed.\n\n"
        
        response += f"**Priority:** {routing_info.get('priority', 'low').title()}\n"
        response += f"**Routing:** {routing_info.get('route_to', 'ops_team').replace('_', ' ').title()}"
        
        return response
    
    @staticmethod
    def _generate_customer_query_response(routing_info: Dict[str, Any], text: str) -> str:
        """Generate response for customer queries."""
        response = "👥 **Customer Query Detected**\n\n"
        response += "This appears to be a customer-related query that needs Product team review.\n\n"
        response += "🔄 **Next Steps:**\n"
        response += "• Routing to DF Product team for review\n"
        response += "• Product team will provide the final customer response\n"
        response += "• I'll ensure proper context is maintained\n\n"
        
        response += f"**Priority:** {routing_info.get('priority', 'medium').title()}\n"
        response += f"**Routing:** {routing_info.get('route_to', 'df_product').replace('_', ' ').title()}"
        
        return response
    
    @staticmethod
    def _generate_engineering_query_response(routing_info: Dict[str, Any], text: str) -> str:
        """Generate response for engineering queries."""
        response = "⚙️ **Engineering Query**\n\n"
        response += "I'll handle this internal engineering query directly.\n\n"
        
        if "confluence" in text.lower():
            response += "I'll check our Confluence documentation for relevant context.\n"
        if "df-owned" in text.lower() or "df owned" in text.lower():
            response += "This relates to DF-owned components. I'll provide technical guidance.\n\n"
        
        response += f"**Priority:** {routing_info.get('priority', 'medium').title()}\n"
        response += f"**Routing:** {routing_info.get('route_to', 'df_ops').replace('_', ' ').title()}"
        
        return response
    
    @staticmethod
    def _generate_feature_request_response(routing_info: Dict[str, Any], text: str) -> str:
        """Generate response for feature requests."""
        response = "✨ **New Feature Request**\n\n"
        response += "I've identified this as a new feature request from customer demand.\n\n"
        response += "🔄 **Next Steps:**\n"
        response += "• Verifying feature availability in current roadmap\n"
        response += "• Routing to DF Product team for evaluation\n"
        response += "• Will provide feasibility assessment\n\n"
        
        response += f"**Priority:** {routing_info.get('priority', 'medium').title()}\n"
        response += f"**Routing:** {routing_info.get('route_to', 'df_product').replace('_', ' ').title()}"
        
        return response
    
    @staticmethod
    def _generate_feature_enablement_response(routing_info: Dict[str, Any], text: str) -> str:
        """Generate response for feature enablement."""
        response = "🔧 **Feature Enablement Request**\n\n"
        response += "I'll validate feature support and coordinate enablement.\n\n"
        response += "🔄 **Next Steps:**\n"
        response += "• Validating feature support for the environment\n"
        response += "• Coordinating with DF Product for enablement\n"
        response += "• Will provide enablement timeline\n\n"
        
        response += f"**Priority:** {routing_info.get('priority', 'medium').title()}\n"
        response += f"**Routing:** {routing_info.get('route_to', 'df_product').replace('_', ' ').title()}"
        
        return response
    
    @staticmethod
    def _generate_pr_review_response(routing_info: Dict[str, Any], text: str) -> str:
        """Generate response for PR review requests."""
        response = "🔀 **PR Review Request**\n\n"
        response += "Code review requests should be posted in the dedicated review channel.\n\n"
        response += "📍 **Please redirect to:** `#mobile-pr-reviews`\n\n"
        response += "This ensures your PR gets proper visibility and timely review from the team.\n\n"
        
        response += f"**Priority:** {routing_info.get('priority', 'low').title()}\n"
        response += f"**Routing:** {routing_info.get('route_to', 'mobile_pr_reviews').replace('_', ' ').title()}"
        
        return response
    
    @staticmethod
    def _generate_unknown_response(text: str) -> str:
        """Generate response for unknown category."""
        response = "🤔 **Request Classification**\n\n"
        response += "I'm analyzing your request to determine the best routing and action.\n\n"
        response += "If this is:\n"
        response += "• **Technical Issue** - Please provide debugging details\n"
        response += "• **Customer Query** - I'll route to Product team\n"
        response += "• **Feature Request** - I'll coordinate with Product\n"
        response += "• **Engineering Query** - I can help directly\n\n"
        response += "Please clarify the type of request if needed."
        
        return response
