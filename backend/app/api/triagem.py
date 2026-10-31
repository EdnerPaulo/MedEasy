"""Endpoints HTTP para o recurso de triagem com suporte a banco de dados e classificação."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.triagem import TriagemModel
from app.schemas.triagem import TriagemCreate, TriagemResponse
from app.services.triagem_service import calcular_classificacao_risco

router = APIRouter(prefix="/triagens", tags=["triagem"])


@router.post("", response_model=TriagemResponse, status_code=status.HTTP_201_CREATED)
def criar_triagem(payload: TriagemCreate, db: Session = Depends(get_db)):
    """Cria, calcula a classificação de risco e persiste a triagem no banco SQLite."""
    risco_classificado = calcular_classificacao_risco(payload)

    db_triagem = TriagemModel(
        paciente=payload.paciente.model_dump(mode="json"),
        queixa_principal=payload.queixa_principal,
        tempo_sintomas=payload.tempo_sintomas,
        intensidade_dor=payload.intensidade_dor,
        historico=payload.historico.model_dump(mode="json") if payload.historico else None,
        sinais_vitais=payload.sinais_vitais.model_dump(mode="json") if payload.sinais_vitais else None,
        status="classificado",
        classificacao_risco=risco_classificado,
    )
    
    db.add(db_triagem)
    db.commit()
    db.refresh(db_triagem)
    return db_triagem


@router.get("/{triagem_id}", response_model=TriagemResponse)
def obter_triagem(triagem_id: int, db: Session = Depends(get_db)):
    """Busca uma triagem gravada na base de dados pelo seu ID."""
    triagem = db.query(TriagemModel).filter(TriagemModel.id == triagem_id).first()
    if not triagem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Triagem não encontrada"
        )
    return triagem