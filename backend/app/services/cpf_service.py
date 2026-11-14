"""Utilidades de CPF: normalização, validação e consulta SIMULADA.

A consulta usa uma base fictícia em memória. Em produção seria trocada por
um provedor de KYC (ex.: BigDataCorp / Infosimples), respeitando a LGPD.
"""
import re
from datetime import date, datetime
from typing import Optional

# Base fictícia: CPFs de teste (válidos pelo dígito verificador).
_BASE_SIMULADA = {
    "52998224725": {"nome": "Maria Eduarda da Silva", "data_nascimento": "1992-05-14"},
    "11144477735": {"nome": "João Pedro Santos", "data_nascimento": "1985-10-20"},
}


def normalizar_cpf(cpf: str) -> str:
    """Remove tudo que não for dígito."""
    return re.sub(r"\D", "", cpf or "")


def validar_cpf(cpf: str) -> bool:
    """Valida tamanho e dígitos verificadores do CPF."""
    digitos = normalizar_cpf(cpf)
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        return False
    for posicao in (9, 10):
        soma = sum(int(digitos[i]) * (posicao + 1 - i) for i in range(posicao))
        verificador = (soma * 10 % 11) % 10
        if verificador != int(digitos[posicao]):
            return False
    return True


def calcular_idade(data_nascimento: date, hoje: Optional[date] = None) -> int:
    hoje = hoje or date.today()
    return (
        hoje.year
        - data_nascimento.year
        - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
    )


def consultar_cpf_simulado(cpf: str) -> Optional[dict]:
    """Retorna nome, data de nascimento e idade, ou None se não estiver na base."""
    registro = _BASE_SIMULADA.get(normalizar_cpf(cpf))
    if registro is None:
        return None
    nascimento = datetime.strptime(registro["data_nascimento"], "%Y-%m-%d").date()
    return {**registro, "idade": calcular_idade(nascimento)}
