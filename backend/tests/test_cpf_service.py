"""Testes unitários do serviço de CPF."""
from datetime import date

from app.services.cpf_service import (
    calcular_idade,
    consultar_cpf_simulado,
    normalizar_cpf,
    validar_cpf,
)


def test_normalizar_remove_pontuacao():
    assert normalizar_cpf("529.982.247-25") == "52998224725"


def test_cpf_valido_com_e_sem_mascara():
    assert validar_cpf("52998224725")
    assert validar_cpf("529.982.247-25")


def test_cpf_com_digito_verificador_errado():
    assert not validar_cpf("52998224724")


def test_cpf_com_todos_digitos_iguais_e_invalido():
    assert not validar_cpf("11111111111")


def test_cpf_com_tamanho_errado():
    assert not validar_cpf("123")
    assert not validar_cpf("")


def test_calcular_idade_antes_e_depois_do_aniversario():
    nasc = date(1990, 6, 15)
    assert calcular_idade(nasc, hoje=date(2026, 6, 14)) == 35
    assert calcular_idade(nasc, hoje=date(2026, 6, 15)) == 36


def test_consulta_simulada_encontra_e_nao_encontra():
    dados = consultar_cpf_simulado("529.982.247-25")
    assert dados["nome"] == "Maria Eduarda da Silva"
    assert dados["idade"] >= 0
    assert consultar_cpf_simulado("39053344705") is None
