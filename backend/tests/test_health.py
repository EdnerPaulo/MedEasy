from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app, create_app

client = TestClient(app)


def test_health_retorna_200_e_status_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health_contem_campos_esperados():
    body = client.get("/health").json()
    for campo in ("status", "service", "version", "environment", "timestamp"):
        assert campo in body


def test_health_nao_expoe_configuracoes_sensiveis():
    texto = client.get("/health").text.lower()
    assert "database" not in texto
    assert "password" not in texto
    assert "senha" not in texto


def test_rota_inexistente_retorna_404():
    assert client.get("/nao-existe").status_code == 404


def test_documentacao_desativada_em_producao():
    prod = TestClient(create_app(Settings(environment="production")))
    assert prod.get("/docs").status_code == 404
    assert prod.get("/openapi.json").status_code == 404
    # O health continua disponível em produção
    assert prod.get("/health").status_code == 200


def test_cors_origins_aceita_texto_separado_por_virgula():
    cfg = Settings(cors_origins="http://a.com, http://b.com")
    assert cfg.cors_origins == ["http://a.com", "http://b.com"]
