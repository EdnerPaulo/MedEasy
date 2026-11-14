from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, triagem
from app.config import Settings, get_settings
from app.database import Base, engine
from app.models import triagem as _modelos  # noqa: F401  (registra as tabelas no Base)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Cria as tabelas se ainda não existirem (ao subir o servidor).
    Base.metadata.create_all(bind=engine)
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    docs_enabled = not settings.is_production
    app = FastAPI(
        title=f"{settings.app_name} API",
        version=settings.app_version,
        docs_url="/docs" if docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if docs_enabled else None,
        lifespan=lifespan,
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            allow_headers=["Authorization", "Content-Type"],
        )

    app.include_router(health.router)
    app.include_router(triagem.router, prefix="/api/v1")

    return app


app = create_app()
