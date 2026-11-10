"""Schemas Pydantic para validação e serialização de dados de triagem."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PacienteBase(BaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=150, json_schema_extra={"example": "Maria Silva"})
    cpf: str = Field(..., min_length=11, max_length=14, json_schema_extra={"example": "12345678901"})
    data_nascimento: date = Field(..., json_schema_extra={"example": "1990-05-15"})
    telefone: str = Field(..., min_length=10, max_length=15, json_schema_extra={"example": "11999998888"})
    email: Optional[EmailStr] = Field(None, json_schema_extra={"example": "maria.silva@email.com"})


class HistoricoSaude(BaseModel):
    alergias: Optional[str] = Field(None, json_schema_extra={"example": "Aspirina, Penicilina"})
    doencas_preexistentes: Optional[str] = Field(None, json_schema_extra={"example": "Hipertensão, Diabetes Tipo 2"})
    medicacoes_em_uso: Optional[str] = Field(None, json_schema_extra={"example": "Losartana 50mg"})


class SinaisVitais(BaseModel):
    pressao_arterial: Optional[str] = Field(None, json_schema_extra={"example": "120/80"})
    frequencia_cardiaca: Optional[int] = Field(None, ge=30, le=250, description="BPM", json_schema_extra={"example": 75})
    temperatura: Optional[float] = Field(None, ge=30.0, le=45.0, description="°C", json_schema_extra={"example": 36.5})
    saturacao_oxigenio: Optional[int] = Field(None, ge=0, le=100, description="SpO2 %", json_schema_extra={"example": 98})


class TriagemCreate(BaseModel):
    """Schema para o POST (criação da pré-triagem pelo paciente/recepção)."""
    paciente: PacienteBase
    queixa_principal: str = Field(..., min_length=5, max_length=1000, json_schema_extra={"example": "Dor forte no peito e falta de ar"})
    tempo_sintomas: str = Field(..., json_schema_extra={"example": "Há aproximadamente 2 horas"})
    intensidade_dor: int = Field(..., ge=0, le=10, description="Escala de dor de 0 a 10", json_schema_extra={"example": 8})
    historico: Optional[HistoricoSaude] = Field(default_factory=HistoricoSaude)
    sinais_vitais: Optional[SinaisVitais] = Field(default_factory=SinaisVitais)


class TriagemResponse(TriagemCreate):
    """Schema retornado pela API após a criação ou consulta."""
    id: int = Field(..., json_schema_extra={"example": 1})
    status: str = Field(default="aguardando_classificacao", json_schema_extra={"example": "aguardando_classificacao"})
    classificacao_risco: Optional[str] = Field(None, json_schema_extra={"example": "AMARELO"})
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Schemas de Consulta e Enriquecimento por CPF ---

class ConsultaCPFRequest(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=14, json_schema_extra={"example": "12345678901"})


class ConsultaCPFResponse(BaseModel):
    nome: str = Field(..., json_schema_extra={"example": "Maria Eduarda da Silva"})
    data_nascimento: str = Field(..., json_schema_extra={"example": "1992-05-14"})
    idade: int = Field(..., json_schema_extra={"example": 34})
    