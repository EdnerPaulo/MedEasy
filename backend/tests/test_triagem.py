"""Testes dos endpoints de triagem (banco em memória, via fixture 'client')."""
import copy

PAYLOAD_VALIDO = {
    "paciente": {
        "nome_completo": "Maria Silva",
        "cpf": "52998224725",
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


def test_criar_triagem_sucesso(client):
    resp = client.post("/api/v1/triagens", json=PAYLOAD_VALIDO)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["paciente"]["nome_completo"] == "Maria Silva"
    assert data["paciente"]["cpf"] == "52998224725"
    assert data["queixa_principal"] == "Dor forte no peito e falta de ar"
    assert data["classificacao_risco"] == "LARANJA"
    assert data["status"] == "classificada"


def test_criar_triagem_aceita_cpf_e_telefone_com_mascara(client):
    payload = copy.deepcopy(PAYLOAD_VALIDO)
    payload["paciente"]["cpf"] = "529.982.247-25"
    payload["paciente"]["telefone"] = "(11) 99999-8888"
    resp = client.post("/api/v1/triagens", json=payload)
    assert resp.status_code == 201
    assert resp.json()["paciente"]["cpf"] == "52998224725"
    assert resp.json()["paciente"]["telefone"] == "11999998888"


def test_criar_triagem_sem_sinais_vitais_nem_historico(client):
    payload = {
        "paciente": {
            "nome_completo": "João Santos",
            "cpf": "11144477735",
            "data_nascimento": "1985-10-20",
            "telefone": "11988887777",
        },
        "queixa_principal": "Febre e dores no corpo",
        "tempo_sintomas": "Há 1 dia",
        "intensidade_dor": 5,
    }
    resp = client.post("/api/v1/triagens", json=payload)
    assert resp.status_code == 201
    assert resp.json()["classificacao_risco"] == "AMARELO"


def test_criar_triagem_dados_invalidos(client):
    resp = client.post("/api/v1/triagens", json={"paciente": {"nome_completo": "A"}})
    assert resp.status_code == 422


def test_criar_triagem_cpf_invalido(client):
    payload = copy.deepcopy(PAYLOAD_VALIDO)
    payload["paciente"]["cpf"] = "12345678901"
    assert client.post("/api/v1/triagens", json=payload).status_code == 422


def test_criar_triagem_dor_fora_da_faixa(client):
    payload = copy.deepcopy(PAYLOAD_VALIDO)
    payload["intensidade_dor"] = 11
    assert client.post("/api/v1/triagens", json=payload).status_code == 422


def test_obter_triagem_por_id(client):
    criada = client.post("/api/v1/triagens", json=PAYLOAD_VALIDO).json()
    resp = client.get(f"/api/v1/triagens/{criada['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == criada["id"]
    assert resp.json()["paciente"]["nome_completo"] == "Maria Silva"


def test_obter_triagem_inexistente(client):
    assert client.get("/api/v1/triagens/9999").status_code == 404


def test_buscar_cpf_encontrado(client):
    resp = client.post("/api/v1/triagens/buscar-cpf", json={"cpf": "529.982.247-25"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["nome"] == "Maria Eduarda da Silva"
    assert body["data_nascimento"] == "1992-05-14"
    assert isinstance(body["idade"], int)


def test_buscar_cpf_valido_mas_fora_da_base(client):
    resp = client.post("/api/v1/triagens/buscar-cpf", json={"cpf": "39053344705"})
    assert resp.status_code == 404


def test_buscar_cpf_com_digito_invalido(client):
    resp = client.post("/api/v1/triagens/buscar-cpf", json={"cpf": "12345678901"})
    assert resp.status_code == 400
