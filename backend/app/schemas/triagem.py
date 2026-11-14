"""Schemas Pydantic para validação e serialização de dados de triagem."""
import re
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.services.cpf_service import normalizar_cpf, validar_cpf


class PacienteBase(BaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150, json_schema_extra={"example": "Maria Silva"})
    cpf: str = Field(..., min_length=11, max_length=14, json_schema_extra={"example": "52998224725"})
    data_nascimento: date = Field(..., json_schema_extra={"example": "1990-05-15"})
    telefone: str = Field(..., min_length=10, max_length=20, json_schema_extra={"example": "11999998888"})
    email: Optional[EmailStr] = Field(None, json_schema_extra={"example": "maria.silva@email.com"})

    @field_validator("cpf")
    @classmethod
    def _cpf_valido(cls, value: str) -> str:
        if not validar_cpf(value):
            raise ValueError("CPF inválido.")
        return normalizar_cpf(value)  # guarda só os 11 dígitos

    @field_validator("telefone")
    @classmethod
    def _telefone_valido(cls, value: str) -> str:
        digitos = re.sub(r"\D", "", value)
        if len(digitos) not in (10, 11):
            raise ValueError("Telefone deve ter 10 ou 11 dígitos (com DDD).")
        return digitos

    @field_validator("data_nascimento")
    @classmethod
    def _nascimento_no_passado(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Data de nascimento não pode estar no futuro.")
        return value


class HistoricoSaude(BaseModel):
    alergias: Optional[str] = Field(None, json_schema_extra={"example": "Aspirina, Penicilina"})
    doencas_preexistentes: Optional[str] = Field(None, json_schema_extra={"example": "Hipertensão, Diabetes Tipo 2"})
    medicacoes_em_uso: Optional[str] = Field(None, json_schema_extra={"example": "Losartana 50mg"})


class SinaisVitais(BaseModel):
    pressao_arterial: Optional[str] = Field(
        None, pattern=r"^\d{2,3}/\d{2,3}$", json_schema_extra={"example": "120/80"}
    )
    frequencia_cardiaca: Optional[int] = Field(None, ge=30, le=250, description="BPM", json_schema_extra={"example": 75})
    temperatura: Optional[float] = Field(None, ge=30.0, le=45.0, description="°C", json_schema_extra={"example": 36.5})
    saturacao_oxigenio: Optional[int] = Field(None, ge=0, le=100, description="SpO2 %", json_schema_extra={"example": 98})


class TriagemCreate(BaseModel):
    """Schema para o POST (criação da pré-triagem pelo paciente/recepção)."""

    paciente: PacienteBase
    queixa_principal: str = Field(..., min_length=5, max_length=1000, json_schema_extra={"example": "Dor forte no peito e falta de ar"})
    tempo_sintomas: str = Field(..., min_length=1, max_length=255, json_schema_extra={"example": "Há aproximadamente 2 horas"})
    intensidade_dor: int = Field(..., ge=0, le=10, description="Escala de dor de 0 a 10", json_schema_extra={"example": 8})
    historico: Optional[HistoricoSaude] = Field(default_factory=HistoricoSaude)
    sinais_vitais: Optional[SinaisVitais] = Field(default_factory=SinaisVitais)


class TriagemResponse(TriagemCreate):
    """Schema retornado pela API após a criação ou consulta."""

    id: int = Field(..., json_schema_extra={"example": 1})
    status: str = Field(default="aguardando_classificacao", json_schema_extra={"example": "classificada"})
    classificacao_risco: Optional[str] = Field(None, json_schema_extra={"example": "AMARELO"})
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Schemas de consulta e enriquecimento por CPF ---

class ConsultaCPFRequest(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=14, json_schema_extra={"example": "529.982.247-25"})


class ConsultaCPFResponse(BaseModel):
    nome: str = Field(..., json_schema_extra={"example": "Maria Eduarda da Silva"})
    data_nascimento: str = Field(..., json_schema_extra={"example": "1992-05-14"})
    idade: int = Field(..., json_schema_extra={"example": 34})
