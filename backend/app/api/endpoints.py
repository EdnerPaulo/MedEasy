from datetime import date, datetime
from fastapi import APIRouter, HTTPException
from app.schemas.triagem import ConsultaCPFRequest, ConsultaCPFResponse

router = APIRouter()

def calcular_idade(data_nasc_str: str) -> int:
    data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
    hoje = date.today()
    return hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))

@router.post("/buscar-cpf", response_model=ConsultaCPFResponse)
async def buscar_dados_cpf(payload: ConsultaCPFRequest):
    cpf_limpo = payload.cpf.replace(".", "").replace("-", "")
    
    if len(cpf_limpo) != 11:
        raise HTTPException(status_code=400, detail="CPF deve conter 11 dígitos.")

    # Simulação da API de KYC (BigDataCorp / Infosimples)
    dados_mock = {
        "nome": "Maria Eduarda da Silva",
        "data_nascimento": "1992-05-14"
    }

    idade = calcular_idade(dados_mock["data_nascimento"])

    return {
        "nome": dados_mock["nome"],
        "data_nascimento": dados_mock["data_nascimento"],
        "idade": idade
    }