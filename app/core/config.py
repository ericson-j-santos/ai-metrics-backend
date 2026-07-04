from functools import lru_cache
from typing import List, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'AI Metrics Backend'
    app_env: Literal['development', 'test', 'homologation', 'staging', 'production'] = 'development'
    app_version: str = '1.0.0'

    database_url: str = 'sqlite:///./ai_metrics.db'
    database_pool_size: int = Field(default=5, ge=1, le=50)
    database_max_overflow: int = Field(default=10, ge=0, le=100)
    database_pool_recycle_seconds: int = Field(default=1800, ge=60, le=86400)

    redis_url: str = 'redis://localhost:6379/0'
    cors_origins: List[str] | str = ['http://localhost:5173', 'http://localhost:4173']
    log_level: str = 'INFO'
    admin_email: str = 'ericsonjosedossantos@tieri659.onmicrosoft.com'

    enable_openapi: bool = True
    enable_request_logging: bool = True
    require_https: bool = False

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value

    @model_validator(mode='after')
    def validate_production_baseline(self):
        if self.app_env == 'production':
            if self.database_url.startswith('sqlite'):
                raise ValueError('DATABASE_URL não pode usar SQLite em production.')
            if '*' in self.cors_origins:
                raise ValueError('CORS_ORIGINS não pode conter wildcard em production.')
            if self.log_level.upper() == 'DEBUG':
                raise ValueError('LOG_LEVEL=DEBUG não é permitido em production.')
            if self.enable_openapi:
                raise ValueError('ENABLE_OPENAPI deve ser false em production.')
            if not self.require_https:
                raise ValueError('REQUIRE_HTTPS deve ser true em production.')
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
