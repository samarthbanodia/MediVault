"""
Base Agent class for Google ADK agents
Provides common functionality for all MediSense agents
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all MediSense agents using Google Gemini
    """

    def __init__(
        self,
        name: str,
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.2,
        max_output_tokens: int = 8192,
        api_key: Optional[str] = None
    ):
        """
        Initialize base agent

        Args:
            name: Agent name
            model: Gemini model to use
            temperature: Temperature for generation (0.0-1.0)
            max_output_tokens: Maximum tokens in response
            api_key: Google API key (defaults to env var)
        """
        self.name = name
        self.model_name = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

        # Configure Gemini API
        api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")

        genai.configure(api_key=api_key)

        # Initialize model with safety settings
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens,
                "response_mime_type": "application/json"
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        logger.info(f"Initialized {self.name} with model {self.model_name}")

    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent
        Must be overridden by subclasses
        """
        raise NotImplementedError("Subclasses must implement get_system_prompt()")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results
        Must be overridden by subclasses

        Args:
            input_data: Input data dictionary

        Returns:
            Result dictionary with processed data
        """
        raise NotImplementedError("Subclasses must implement process()")

    def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate response from Gemini model

        Args:
            prompt: User prompt
            context: Optional context dictionary

        Returns:
            Parsed JSON response
        """
        try:
            # Build full prompt with system instructions
            system_prompt = self.get_system_prompt()

            # Add context if provided
            if context:
                context_str = json.dumps(context, indent=2)
                full_prompt = f"{system_prompt}\n\n### Context:\n{context_str}\n\n### Task:\n{prompt}"
            else:
                full_prompt = f"{system_prompt}\n\n### Task:\n{prompt}"

            # Generate response
            response = self.model.generate_content(full_prompt)

            # Parse JSON response
            try:
                result = json.loads(response.text)
                result['_metadata'] = {
                    'agent': self.name,
                    'model': self.model_name,
                    'timestamp': datetime.utcnow().isoformat(),
                    'temperature': self.temperature
                }
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return {
                    'success': False,
                    'error': 'Invalid JSON response from model',
                    'raw_response': response.text
                }

        except Exception as e:
            logger.error(f"Error generating response in {self.name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def validate_input(self, input_data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate input data has required fields

        Args:
            input_data: Input data dictionary
            required_fields: List of required field names

        Returns:
            True if valid, raises ValueError otherwise
        """
        missing_fields = [field for field in required_fields if field not in input_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        return True

    def log_execution(self, input_data: Dict[str, Any], output_data: Dict[str, Any]):
        """
        Log agent execution for monitoring

        Args:
            input_data: Input provided to agent
            output_data: Output generated by agent
        """
        logger.info(f"Agent: {self.name}")
        logger.debug(f"Input: {json.dumps(input_data, indent=2)}")
        logger.debug(f"Output: {json.dumps(output_data, indent=2)}")
