"""Testes automatizados para os endpoints de Triagem."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_criar_triagem_sucesso():
    """Testa a criação de uma nova triagem com dados válidos."""
    payload = {
        "paciente": {
            "nome_completo": "Maria Silva",
            "cpf": "12345678901",
            "data_nascimento": "1990-05-15",
            "telefone": "11999998888",
            "email": "maria.silva@email.com",
        },
        "queixa_principal": "Dor forte no peito e falta de ar",
        "tempo_sintomas": "Há aproximadamente 2 horas",
        "intensidade_dor": 8,
        "historico": {
            "alergias": "Aspirina, Penicilina",
            "doencas_preexistentes": "Hipertensão",
            "medicacoes_em_uso": "Losartana 50mg",
        },
        "sinais_vitais": {
            "pressao_arterial": "120/80",
            "frequencia_cardiaca": 75,
            "temperatura": 36.5,
            "saturacao_oxigenio": 98,
        },
    }

    response = client.post("/api/v1/triagens", json=payload)

    # Verifica se a triagem foi criada (HTTP 200 OK ou 201 Created)
    assert response.status_code in (200, 201)

    data = response.json()
    assert "id" in data
    assert data["paciente"]["nome_completo"] == "Maria Silva"
    assert data["queixa_principal"] == "Dor forte no peito e falta de ar"


def test_criar_triagem_dados_invalidos():
    """Testa a validação de erro ao tentar enviar dados incompletos ou inválidos."""
    payload_invalido = {
        "paciente": {
            "nome_completo": "A",  # Nome muito curto (espera min_length=3)
        }
    }

    response = client.post("/api/v1/triagens", json=payload_invalido)

    # Deve retornar Erro 422 Unprocessable Entity (Falha de Validação do Pydantic)
    assert response.status_code == 422


def test_obter_triagem_por_id():
    """Testa a busca de uma triagem específica pelo seu ID."""
    # 1. Primeiro cria uma triagem para garantir que existe um ID
    payload = {
        "paciente": {
            "nome_completo": "João Santos",
            "cpf": "98765432100",
            "data_nascimento": "1985-10-20",
            "telefone": "11988887777",
        },
        "queixa_principal": "Febre alta e dores no corpo",
        "tempo_sintomas": "Há 1 dia",
        "intensidade_dor": 5,
    }

    post_response = client.post("/api/v1/triagens", json=payload)
    assert post_response.status_code in (200, 201)
    triagem_id = post_response.json()["id"]

    # 2. Faz a busca GET utilizando o ID gerado
    get_response = client.get(f"/api/v1/triagens/{triagem_id}")

    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == triagem_id
    assert data["paciente"]["nome_completo"] == "João Santos"