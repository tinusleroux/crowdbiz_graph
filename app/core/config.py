#!/usr/bin/env python3
"""
Configuration management for CrowdBiz Graph
Centralizes all configuration settings and environment variables
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    url: str
    api_key: str
    personal_access_token: Optional[str] = None
    password: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        # Try to use the PostgreSQL URL first, fallback to Supabase URL
        db_url = (
            os.getenv('SUPABASE_DB_URL') or 
            os.getenv('DATABASE_URL') or 
            os.getenv('SUPABASE_URL', '')
        )
        
        return cls(
            url=db_url,
            api_key=os.getenv('SUPABASE_API_KEY', ''),
            personal_access_token=os.getenv('SUPABASE_PERSONAL_ACCESS_TOKEN'),
            password=os.getenv('SUPABASE_DATABASE_PASSWORD')
        )
    
    def validate(self) -> bool:
        """Validate required configuration"""
        return bool(self.url and self.api_key)

@dataclass 
class AIConfig:
    """AI service configuration"""
    openai_key: Optional[str] = None
    gemini_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'AIConfig':
        return cls(
            openai_key=os.getenv('OPENAI_KEY') or os.getenv('OPENAI_API_KEY'),
            gemini_key=os.getenv('GEMINI_KEY') or os.getenv('GEMINI_API_KEY')
        )
    
    def has_openai(self) -> bool:
        return bool(self.openai_key)
    
    def has_gemini(self) -> bool:
        return bool(self.gemini_key)

@dataclass
class ImportConfig:
    """Data import configuration"""
    default_source_license: str = "public"
    batch_size: int = 100
    max_retries: int = 3
    delay_between_requests: float = 1.0
    
    # File paths
    teams_csv_path: str = "sources/teams.csv"
    imports_dir: str = "imports/"
    
    @classmethod
    def from_env(cls) -> 'ImportConfig':
        return cls(
            default_source_license=os.getenv('DEFAULT_SOURCE_LICENSE', 'public'),
            batch_size=int(os.getenv('IMPORT_BATCH_SIZE', '100')),
            max_retries=int(os.getenv('IMPORT_MAX_RETRIES', '3')),
            delay_between_requests=float(os.getenv('IMPORT_DELAY', '1.0'))
        )

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        return cls(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            format=os.getenv('LOG_FORMAT', "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

@dataclass
class AppConfig:
    """Main application configuration"""
    database: DatabaseConfig
    ai: AIConfig
    imports: ImportConfig
    logging: LoggingConfig
    
    # Application settings
    app_name: str = "CrowdBiz Graph"
    version: str = "1.0.0"
    debug: bool = False
    
    @classmethod
    def load(cls) -> 'AppConfig':
        """Load configuration from environment"""
        return cls(
            database=DatabaseConfig.from_env(),
            ai=AIConfig.from_env(),
            imports=ImportConfig.from_env(),
            logging=LoggingConfig.from_env(),
            debug=os.getenv('DEBUG', 'false').lower() == 'true'
        )
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate all configuration"""
        errors = []
        
        if not self.database.validate():
            errors.append("Database configuration incomplete - missing URL or API key")
        
        if not (self.ai.has_openai() or self.ai.has_gemini()):
            errors.append("No AI service configured - need OpenAI or Gemini API key")
        
        return len(errors) == 0, errors

# Global configuration instance
config = AppConfig.load()

def get_config() -> AppConfig:
    """Get the global configuration instance"""
    return config

def validate_config() -> bool:
    """Validate configuration and print status"""
    is_valid, errors = config.validate()
    
    if is_valid:
        print("✅ Configuration validation passed")
    else:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
    
    return is_valid

def print_config_summary():
    """Print a summary of current configuration"""
    print(f"🔧 {config.app_name} v{config.version} Configuration:")
    print(f"  Database: {'✅' if config.database.validate() else '❌'} {config.database.url[:30]}...")
    print(f"  OpenAI: {'✅' if config.ai.has_openai() else '❌'}")
    print(f"  Gemini: {'✅' if config.ai.has_gemini() else '❌'}")
    print(f"  Debug Mode: {config.debug}")
    print(f"  Batch Size: {config.imports.batch_size}")

if __name__ == "__main__":
    print_config_summary()
    validate_config()
