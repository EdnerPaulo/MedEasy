"""Configuração da aplicação, lida de variáveis de ambiente / arquivo .env.

Nenhum segredo é definido aqui: valores sensíveis (ex.: DATABASE_URL)
vêm apenas do ambiente e não possuem valor padrão.
"""
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "MedEasy"
    app_version: str = "0.1.0"
    environment: str = "development"  # development | test | production
    debug: bool = False
    cors_origins: list[str] = []
    database_url: str | None = None  # usado em etapa futura

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value):
        # Aceita "a,b,c" (formato do .env) ou uma lista.
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
