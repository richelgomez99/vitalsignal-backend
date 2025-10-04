"""Configuration management for VitalSignal API"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    
    # ClickHouse Database
    clickhouse_host: str
    clickhouse_port: int = 8443
    clickhouse_user: str = "default"
    clickhouse_password: str
    clickhouse_database: str = "default"
    clickhouse_secure: bool = True
    
    # External APIs
    structify_api_key: str
    phenoml_auth_basic: str
    deepl_api_key: str
    freepik_api_key: str
    sendgrid_api_key: str
    sendgrid_from_email: str
    
    # Airia Integration (optional)
    airia_webhook_secret: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
