"""Serviço responsável pela lógica de classificação de risco médica."""
from app.schemas.triagem import TriagemCreate


def calcular_classificacao_risco(payload: TriagemCreate) -> str:
    """
    Avalia os dados da triagem e classifica o risco:
    - Vermelho (Emergência)
    - Laranja (Muito Urgente)
    - Amarelo (Urgente)
    - Verde (Pouco Urgente)
    - Azul (Não Urgente)
    """
    # 1. Regras de Emergência (Vermelho)
    if payload.intensidade_dor >= 9:
        return "Vermelho"

    if payload.sinais_vitais and payload.sinais_vitais.saturacao_oxigenio:
        if payload.sinais_vitais.saturacao_oxigenio < 92:
            return "Vermelho"

    # 2. Regras de Muita Urgência (Laranja)
    if payload.intensidade_dor >= 7:
        return "Laranja"

    if payload.sinais_vitais and payload.sinais_vitais.temperatura:
        if payload.sinais_vitais.temperatura >= 39.0:
            return "Laranja"

    # 3. Regras de Urgência (Amarelo)
    if payload.intensidade_dor >= 4:
        return "Amarelo"

    if payload.sinais_vitais and payload.sinais_vitais.temperatura:
        if payload.sinais_vitais.temperatura >= 37.8:
            return "Amarelo"

    # 4. Regras de Pouco Urgente (Verde)
    if payload.intensidade_dor >= 1:
        return "Verde"

    # 5. Padrão: Não Urgente (Azul)
    return "Azul"