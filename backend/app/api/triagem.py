"""Rotas de triagem: consulta de CPF, criação e consulta de pré-triagens."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.triagem import TriagemModel
from app.schemas.triagem import (
    ConsultaCPFRequest,
    ConsultaCPFResponse,
    TriagemCreate,
    TriagemResponse,
)
from app.services.cpf_service import consultar_cpf_simulado, validar_cpf
from app.services.triagem_service import calcular_classificacao_risco

router = APIRouter(prefix="/triagens", tags=["triagens"])


@router.post("/buscar-cpf", response_model=ConsultaCPFResponse)
def buscar_dados_cpf(payload: ConsultaCPFRequest):
    """Consulta SIMULADA de nome e data de nascimento a partir do CPF."""
    if not validar_cpf(payload.cpf):
        raise HTTPException(status_code=400, detail="CPF inválido.")

    dados = consultar_cpf_simulado(payload.cpf)
    if dados is None:
        raise HTTPException(
            status_code=404,
            detail="CPF não encontrado na base simulada. Preencha os dados manualmente.",
        )
    return dados


@router.post("", response_model=TriagemResponse, status_code=201)
def criar_triagem(payload: TriagemCreate, db: Session = Depends(get_db)):
    """Registra a pré-triagem e já devolve a classificação de risco."""
    registro = TriagemModel(
        # mode="json" converte date -> texto, senão o JSON do banco falha
        paciente=payload.paciente.model_dump(mode="json"),
        queixa_principal=payload.queixa_principal,
        tempo_sintomas=payload.tempo_sintomas,
        intensidade_dor=payload.intensidade_dor,
        historico=payload.historico.model_dump(mode="json") if payload.historico else None,
        sinais_vitais=payload.sinais_vitais.model_dump(mode="json") if payload.sinais_vitais else None,
        classificacao_risco=calcular_classificacao_risco(payload),
        status="classificada",
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@router.get("/{triagem_id}", response_model=TriagemResponse)
def obter_triagem(triagem_id: int, db: Session = Depends(get_db)):
    """Busca uma triagem pelo ID.

    NOTA DE SEGURANÇA: ainda sem autenticação. Antes de qualquer uso real é
    obrigatório proteger esta rota (login/perfil), pois expõe dados de saúde.
    """
    registro = db.get(TriagemModel, triagem_id)
    if registro is None:
        raise HTTPException(status_code=404, detail="Triagem não encontrada.")
    return registro
