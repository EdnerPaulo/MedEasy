"""Serviço responsável pela lógica de classificação de risco.

ATENÇÃO: é uma classificação SIMPLIFICADA, de uso acadêmico. Ela se inspira
nas cores do Protocolo de Manchester, mas NÃO o implementa e NÃO substitui a
avaliação de um profissional de saúde.

Níveis (do menos para o mais grave):
    AZUL (não urgente) < VERDE (pouco urgente) < AMARELO (urgente)
    < LARANJA (muito urgente) < VERMELHO (emergência)

O resultado é sempre o nível MAIS GRAVE entre todas as regras acionadas.
"""
import unicodedata

from app.schemas.triagem import TriagemCreate

NIVEIS = ["AZUL", "VERDE", "AMARELO", "LARANJA", "VERMELHO"]

# Sinais de alerta na queixa: elevam o risco para, no mínimo, LARANJA.
SINAIS_DE_ALERTA = (
    "dor no peito",
    "dor toracica",
    "falta de ar",
    "dificuldade para respirar",
    "dificuldade de respirar",
    "convuls",
    "desmai",
    "inconsciente",
    "sangramento intenso",
    "hemorragia",
    "rosto torto",
    "fala arrastada",
    "overdose",
)


def _sem_acentos(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def calcular_classificacao_risco(payload: TriagemCreate) -> str:
    """Avalia os dados da triagem e devolve AZUL/VERDE/AMARELO/LARANJA/VERMELHO."""
    nivel = 0  # índice em NIVEIS
    dor = payload.intensidade_dor
    sinais = payload.sinais_vitais

    # --- Intensidade da dor ---
    if dor >= 9:
        nivel = max(nivel, 4)
    elif dor >= 7:
        nivel = max(nivel, 3)
    elif dor >= 4:
        nivel = max(nivel, 2)
    elif dor >= 1:
        nivel = max(nivel, 1)

    # --- Sinais vitais (atenção: 0 é um valor válido, por isso 'is not None') ---
    if sinais is not None:
        if sinais.saturacao_oxigenio is not None and sinais.saturacao_oxigenio < 92:
            nivel = max(nivel, 4)

        if sinais.temperatura is not None:
            if sinais.temperatura >= 39.0:
                nivel = max(nivel, 3)
            elif sinais.temperatura >= 37.8:
                nivel = max(nivel, 2)

        if sinais.frequencia_cardiaca is not None:
            if sinais.frequencia_cardiaca >= 130 or sinais.frequencia_cardiaca <= 40:
                nivel = max(nivel, 3)

    # --- Sinais de alerta descritos na queixa ---
    queixa = _sem_acentos(payload.queixa_principal)
    if any(sinal in queixa for sinal in SINAIS_DE_ALERTA):
        nivel = max(nivel, 3)

    return NIVEIS[nivel]
