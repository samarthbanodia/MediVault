"""
Configuration for Google ADK Agents
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AgentConfig:
    """Configuration class for all agents"""

    # Google API Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

    # Model Configuration
    DEFAULT_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-004')

    # Temperature Settings
    OCR_TEMPERATURE = 0.1  # Very low for accurate extraction
    NER_TEMPERATURE = 0.2  # Low for consistent entity extraction
    PRESCRIPTION_TEMPERATURE = 0.1  # Very low for accurate parsing
    ANOMALY_TEMPERATURE = 0.2  # Low for consistent detection
    NORMALIZER_TEMPERATURE = 0.1  # Very low for consistent structuring
    SEARCH_TEMPERATURE = 0.3  # Medium for flexible search
    ANALYSER_TEMPERATURE = 0.4  # Higher for natural responses

    # Token Limits
    MAX_OUTPUT_TOKENS = 8192

    # Vector Database Configuration
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './chroma_db')
    VECTOR_DB_COLLECTION = os.getenv('VECTOR_DB_COLLECTION', 'medical_records')

    # Search Configuration
    DEFAULT_TOP_K = 5
    HYBRID_SEARCH_WEIGHTS = {
        'semantic': 0.6,
        'keyword': 0.3,
        'recency': 0.1
    }

    # Processing Configuration
    ENABLE_BATCH_PROCESSING = True
    BATCH_SIZE = 10

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/agents.log')

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in .env file")

        return True

    @classmethod
    def get_agent_config(cls, agent_type: str) -> dict:
        """
        Get configuration for specific agent type

        Args:
            agent_type: Type of agent (ocr, ner, prescription, etc.)

        Returns:
            Configuration dictionary
        """
        base_config = {
            'api_key': cls.GOOGLE_API_KEY,
            'model': cls.DEFAULT_MODEL,
            'max_output_tokens': cls.MAX_OUTPUT_TOKENS
        }

        temperature_map = {
            'ocr': cls.OCR_TEMPERATURE,
            'ner': cls.NER_TEMPERATURE,
            'prescription': cls.PRESCRIPTION_TEMPERATURE,
            'anomaly': cls.ANOMALY_TEMPERATURE,
            'normalizer': cls.NORMALIZER_TEMPERATURE,
            'search': cls.SEARCH_TEMPERATURE,
            'analyser': cls.ANALYSER_TEMPERATURE
        }

        base_config['temperature'] = temperature_map.get(agent_type, 0.3)

        return base_config
