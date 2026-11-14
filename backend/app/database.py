"""Configuração da conexão com o banco de dados via SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

_database_url = get_settings().database_url

# 'check_same_thread' só existe (e só é necessário) no SQLite.
_connect_args = (
    {"check_same_thread": False} if _database_url.startswith("sqlite") else {}
)

engine = create_engine(_database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependência do FastAPI: uma sessão de banco por requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
