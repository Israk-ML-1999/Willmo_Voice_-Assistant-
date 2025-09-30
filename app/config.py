import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # ── App Configuration 
    APP_NAME: str = "Voice Assistant ChatBot API"
    APP_DESCRIPTION: str = "A voice assistant with To-do, Job finding, and General chat capabilities"
    APP_VERSION: str = "1.0.0"
    
    # ── OpenAI Configuration 
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = "https://api.openai.com/v1"  # Base URL without any path
    CHAT_MODEL: str = "gpt-3.5-turbo"
    WHISPER_MODEL: str = "whisper-1"
    WHISPER_RESPONSE_FORMAT: str = "text"  # Can be 'text', 'json', 'srt', 'verbose_json', or 'vtt'
    
    # ── Model Configuration 
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    MAX_HISTORY_MESSAGES: int = 5
    
    # ── Audio Configuration 
    
    TEMP_DIR: str = "temp"
    AUDIO_RESPONSE_PATH: str = "audio_response_path"
    # Whisper configuration
    WHISPER_LANGUAGE_DETECT: bool = True  # Enable language detection
    WHISPER_TASK: str = "transcribe"  # Can be 'transcribe' or 'translate'
    
    # Validation
    def __post_init__(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")

# Create settings instance
settings = Settings()