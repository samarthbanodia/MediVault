"""
MediSense Configuration Management
Centralized configuration using environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables"""

    # Base paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))

    # Embeddings Configuration
    EMBEDDINGS_MODEL = os.getenv(
        'EMBEDDINGS_MODEL',
        'paraphrase-multilingual-mpnet-base-v2'
    )

    # Vector Database Configuration
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './chroma_db')
    VECTOR_DB_COLLECTION = os.getenv('VECTOR_DB_COLLECTION', 'medical_records')

    # OCR Configuration
    OCR_GPU = os.getenv('OCR_GPU', 'false').lower() == 'true'
    OCR_LANGUAGES = os.getenv('OCR_LANGUAGES', 'en,hi').split(',')

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/medisense.log')

    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

    # Redis Configuration (for caching)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRY_HOURS = int(os.getenv('JWT_EXPIRY_HOURS', '24'))

    # File Upload Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '16'))
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'}

    # Supabase Storage
    STORAGE_BUCKET_NAME = os.getenv('STORAGE_BUCKET_NAME', 'medical-records')

    @classmethod
    def validate(cls):
        """Validate critical configuration values"""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY not set in environment")

        if cls.OPENAI_API_KEY and cls.OPENAI_API_KEY == 'your-openai-api-key-here':
            errors.append("OPENAI_API_KEY is using template value - please update with real API key")

        if not cls.SUPABASE_URL:
            errors.append("SUPABASE_URL not set in environment")

        if not cls.SUPABASE_ANON_KEY:
            errors.append("SUPABASE_ANON_KEY not set in environment")

        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return True

    @classmethod
    def setup_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.DATA_DIR.mkdir(exist_ok=True)
        Path(cls.VECTOR_DB_PATH).mkdir(exist_ok=True)


# Auto-setup directories on import
Config.setup_directories()
