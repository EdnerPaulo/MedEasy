"""Endpoint de verificação de disponibilidade da API."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings

router = APIRouter(tags=["infra"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict:
    """Indica que a API está no ar. Não expõe configurações sensíveis."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
