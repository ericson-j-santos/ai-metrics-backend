from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'AI Metrics Backend'
    app_env: str = 'development'
    database_url: str = 'sqlite:///./ai_metrics.db'
    cors_origins: List[str] | str = ['http://localhost:5173', 'http://localhost:4173']
    log_level: str = 'INFO'
    admin_email: str = 'ericsonjosedossantos@tieri659.onmicrosoft.com'

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
