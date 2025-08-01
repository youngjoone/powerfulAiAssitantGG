"""
Configuration management for the Dual AI Assistant
"""

import os
from typing import Optional

class Config:
    """Configuration class for managing environment variables and settings"""
    
    # API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Model Configuration
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Request Configuration
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "ai_assistant.log")
    
    @classmethod
    def validate_configuration(cls) -> bool:
        """
        Validate that required configuration is present
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_vars = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("GEMINI_API_KEY", cls.GEMINI_API_KEY)
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """Get OpenAI specific configuration"""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL,
            "max_tokens": cls.MAX_TOKENS,
            "temperature": cls.TEMPERATURE
        }
    
    @classmethod
    def get_gemini_config(cls) -> dict:
        """Get Gemini specific configuration"""
        return {
            "api_key": cls.GEMINI_API_KEY,
            "model": cls.GEMINI_MODEL
        }
    
    @classmethod
    def print_configuration(cls) -> None:
        """Print current configuration (without sensitive data)"""
        print("=== Dual AI Assistant Configuration ===")
        print(f"OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"Gemini Model: {cls.GEMINI_MODEL}")
        print(f"Max Tokens: {cls.MAX_TOKENS}")
        print(f"Temperature: {cls.TEMPERATURE}")
        print(f"Request Timeout: {cls.REQUEST_TIMEOUT}s")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print(f"Log File: {cls.LOG_FILE}")
        print(f"OpenAI API Key: {'✓ Set' if cls.OPENAI_API_KEY else '✗ Not Set'}")
        print(f"Gemini API Key: {'✓ Set' if cls.GEMINI_API_KEY else '✗ Not Set'}")
        print("=" * 40)
