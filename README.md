# MedEasy — Pré-atendimento para prontos-socorros (MVP acadêmico)

Projeto acadêmico (ENIAC — Empreendedorismo, ADS + RH).
**Status: Etapa 1 — esqueleto da API.** Somente dados fictícios. Não é um
sistema clínico e não deve ser usado com dados reais de pacientes.

## O que já existe
- API FastAPI com `GET /health`
- Configuração por variáveis de ambiente (`.env`)
- Testes automatizados básicos (pytest)

Ainda **não** existem: banco de dados, formulário, painel, login, QR Code, PWA, NLP, FHIR.

## Requisitos (Windows)
- Python 3.11 ou superior (https://www.python.org/downloads/) — marque "Add python.exe to PATH"
- Git (opcional, recomendado)

## Instalação (PowerShell)
```powershell
cd medeasy\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
copy ..\.env.example .env
```
Se o PowerShell bloquear a ativação do ambiente virtual, execute uma vez:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Executar a API
```powershell
uvicorn app.main:app --reload
```
- Health: http://127.0.0.1:8000/health
- Documentação interativa (fora de produção): http://127.0.0.1:8000/docs

## Executar os testes
```powershell
pytest -v
```

## Estrutura
```
medeasy/
├── .env.example        # modelo de configuração (sem segredos)
├── .gitignore
├── README.md
├── docs/               # documentação (próximas etapas)
└── backend/
    ├── app/
    │   ├── main.py     # criação da aplicação
    │   ├── config.py   # variáveis de ambiente
    │   └── api/
    │       └── health.py
    ├── tests/
    │   └── test_health.py
    ├── pytest.ini
    ├── requirements.txt
    └── requirements-dev.txt
```

## Segurança
- `.env` está no `.gitignore`; nunca faça commit de senhas ou chaves.
- Documentação interativa é desativada com `ENVIRONMENT=production`.
- Usar apenas dados fictícios até que exista avaliação de segurança e LGPD.
