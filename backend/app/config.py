"""Configuração da aplicação, lida de variáveis de ambiente / arquivo .env.

Nenhum segredo é definido aqui: valores sensíveis (ex.: senha do banco)
vêm apenas do ambiente.
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
    app_version: str = "0.2.0"
    environment: str = "development"  # development | test | production
    debug: bool = False
    cors_origins: list[str] = []
    # SQLite local por padrão (MVP acadêmico). Pode ser trocado por PostgreSQL.
    database_url: str = "sqlite:///./medeasy.db"

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
