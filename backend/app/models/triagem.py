"""Modelo de banco de dados para a entidade Triagem."""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, JSON
from app.database import Base


class TriagemModel(Base):
    """Mapeamento da tabela de triagens no banco de dados."""

    __tablename__ = "triagens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Dados do Paciente salvos como estrutura JSON
    paciente = Column(JSON, nullable=False)

    # Dados da avaliação médica
    queixa_principal = Column(String(1000), nullable=False)
    tempo_sintomas = Column(String(255), nullable=False)
    intensidade_dor = Column(Integer, nullable=False)

    # Informações complementares salvas como JSON
    historico = Column(JSON, nullable=True)
    sinais_vitais = Column(JSON, nullable=True)

    # Controle de estado e data de criação
    status = Column(String(50), default="aguardando_classificacao")
    classificacao_risco = Column(String(50), nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))