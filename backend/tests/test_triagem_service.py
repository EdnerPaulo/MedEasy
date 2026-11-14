"""Testes unitários para a lógica de classificação de risco da triagem."""
import pytest

from app.schemas.triagem import TriagemCreate
from app.services.triagem_service import calcular_classificacao_risco


@pytest.fixture
def paciente_padrao():
    return {
        "nome_completo": "Carlos Eduardo",
        "cpf": "52998224725",
        "data_nascimento": "1980-01-01",
        "telefone": "11977776666",
    }


def _triagem(paciente, queixa="Mal-estar leve", dor=0, **extra):
    return TriagemCreate(
        paciente=paciente,
        queixa_principal=queixa,
        tempo_sintomas="1 hora",
        intensidade_dor=dor,
        **extra,
    )


def test_emergencia_dor_alta(paciente_padrao):
    assert calcular_classificacao_risco(_triagem(paciente_padrao, dor=9)) == "VERMELHO"


def test_emergencia_saturacao_baixa(paciente_padrao):
    t = _triagem(paciente_padrao, dor=5, sinais_vitais={"saturacao_oxigenio": 90})
    assert calcular_classificacao_risco(t) == "VERMELHO"


def test_saturacao_zero_nao_e_ignorada(paciente_padrao):
    """Regressão: SpO2 = 0 era tratado como 'sem dado' (valor falso)."""
    t = _triagem(paciente_padrao, dor=0, sinais_vitais={"saturacao_oxigenio": 0})
    assert calcular_classificacao_risco(t) == "VERMELHO"


def test_saturacao_92_nao_e_emergencia(paciente_padrao):
    t = _triagem(paciente_padrao, dor=0, sinais_vitais={"saturacao_oxigenio": 92})
    assert calcular_classificacao_risco(t) == "AZUL"


def test_muito_urgente_dor_7(paciente_padrao):
    assert calcular_classificacao_risco(_triagem(paciente_padrao, dor=7)) == "LARANJA"


def test_muito_urgente_dor_8(paciente_padrao):
    assert calcular_classificacao_risco(_triagem(paciente_padrao, dor=8)) == "LARANJA"


def test_muito_urgente_febre_alta(paciente_padrao):
    t = _triagem(paciente_padrao, queixa="Febre muito alta", dor=3, sinais_vitais={"temperatura": 39.5})
    assert calcular_classificacao_risco(t) == "LARANJA"


def test_muito_urgente_frequencia_cardiaca_extrema(paciente_padrao):
    t = _triagem(paciente_padrao, dor=0, sinais_vitais={"frequencia_cardiaca": 140})
    assert calcular_classificacao_risco(t) == "LARANJA"


def test_sinal_de_alerta_na_queixa_com_acento(paciente_padrao):
    t = _triagem(paciente_padrao, queixa="Dor torácica e suor frio", dor=3)
    assert calcular_classificacao_risco(t) == "LARANJA"


def test_sinal_de_alerta_dor_no_peito_dor_baixa(paciente_padrao):
    t = _triagem(paciente_padrao, queixa="Sinto dor no peito há pouco", dor=2)
    assert calcular_classificacao_risco(t) == "LARANJA"


def test_urgente_dor_moderada(paciente_padrao):
    t = _triagem(paciente_padrao, queixa="Dor abdominal moderada", dor=5)
    assert calcular_classificacao_risco(t) == "AMARELO"


def test_urgente_dor_4_limite(paciente_padrao):
    assert calcular_classificacao_risco(_triagem(paciente_padrao, dor=4)) == "AMARELO"


def test_urgente_temperatura_37_8(paciente_padrao):
    t = _triagem(paciente_padrao, dor=0, sinais_vitais={"temperatura": 37.8})
    assert calcular_classificacao_risco(t) == "AMARELO"


def test_pouco_urgente(paciente_padrao):
    assert calcular_classificacao_risco(_triagem(paciente_padrao, dor=3)) == "VERDE"
    assert calcular_classificacao_risco(_triagem(paciente_padrao, dor=1)) == "VERDE"


def test_nao_urgente(paciente_padrao):
    t = _triagem(paciente_padrao, queixa="Troca de receita médica", dor=0)
    assert calcular_classificacao_risco(t) == "AZUL"


def test_vale_o_nivel_mais_grave(paciente_padrao):
    t = _triagem(
        paciente_padrao, dor=2,
        sinais_vitais={"temperatura": 39.5, "saturacao_oxigenio": 88},
    )
    assert calcular_classificacao_risco(t) == "VERMELHO"
