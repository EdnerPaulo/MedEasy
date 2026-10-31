"""Testes unitários para a lógica de classificação de risco da triagem."""
import pytest
from app.schemas.triagem import TriagemCreate
from app.services.triagem_service import calcular_classificacao_risco


@pytest.fixture
def paciente_padrao():
    """Fixture com os dados em dicionário do paciente."""
    return {
        "nome_completo": "Carlos Eduardo",
        "cpf": "12345678901",
        "data_nascimento": "1980-01-01",
        "telefone": "11977776666",
    }


def test_classificacao_emergencia_dor_alta(paciente_padrao):
    """Dor intensidade >= 9 deve retornar Vermelho (Emergência)."""
    payload = TriagemCreate(
        paciente=paciente_padrao,
        queixa_principal="Dor torácica insuportável",
        tempo_sintomas="30 min",
        intensidade_dor=9,
    )
    resultado = calcular_classificacao_risco(payload)
    assert resultado == "Vermelho"


def test_classificacao_emergencia_saturacao_baixa(paciente_padrao):
    """Saturação de oxigênio < 92% deve retornar Vermelho (Emergência)."""
    payload = TriagemCreate(
        paciente=paciente_padrao,
        queixa_principal="Falta de ar grave",
        tempo_sintomas="1 hora",
        intensidade_dor=5,
        sinais_vitais={"saturacao_oxigenio": 90},
    )
    resultado = calcular_classificacao_risco(payload)
    assert resultado == "Vermelho"


def test_classificacao_muito_urgente_temperatura_alta(paciente_padrao):
    """Febre alta (>= 39.0°C) deve retornar Laranja (Muito Urgente)."""
    payload = TriagemCreate(
        paciente=paciente_padrao,
        queixa_principal="Febre muito alta",
        tempo_sintomas="5 horas",
        intensidade_dor=3,
        sinais_vitais={"temperatura": 39.5},
    )
    resultado = calcular_classificacao_risco(payload)
    assert resultado == "Laranja"


def test_classificacao_urgente_dor_moderada(paciente_padrao):
    """Dor intensidade 5 deve retornar Amarelo (Urgente)."""
    payload = TriagemCreate(
        paciente=paciente_padrao,
        queixa_principal="Dor abdominal moderada",
        tempo_sintomas="1 dia",
        intensidade_dor=5,
    )
    resultado = calcular_classificacao_risco(payload)
    assert resultado == "Amarelo"


def test_classificacao_nao_urgente(paciente_padrao):
    """Dor 0 e sem alterações vitais deve retornar Azul (Não Urgente)."""
    payload = TriagemCreate(
        paciente=paciente_padrao,
        queixa_principal="Troca de receita médica",
        tempo_sintomas="N/A",
        intensidade_dor=0,
    )
    resultado = calcular_classificacao_risco(payload)
    assert resultado == "Azul"