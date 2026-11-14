# MedEasy — Pré-atendimento para prontos-socorros (MVP acadêmico)

Projeto acadêmico (ENIAC — Empreendedorismo, ADS + RH).
**Somente dados fictícios.** Não é um sistema clínico e não deve ser usado com
dados reais de pacientes. A classificação de risco é **simplificada**: usa as
cores do Protocolo de Manchester como inspiração, mas não o implementa e não
substitui a avaliação de um profissional de saúde.

## O que já existe

- **API FastAPI** com SQLite e SQLAlchemy
  - `GET  /health`
  - `POST /api/v1/triagens/buscar-cpf` — consulta **simulada** de nome e nascimento
  - `POST /api/v1/triagens` — registra a pré-triagem e devolve a classificação
  - `GET  /api/v1/triagens/{id}` — consulta uma triagem
- Validação de CPF (dígitos verificadores), telefone e sinais vitais
- Classificação de risco: `AZUL`, `VERDE`, `AMARELO`, `LARANJA`, `VERMELHO`
  (dor, saturação, temperatura, frequência cardíaca e sinais de alerta na queixa)
- **Frontend React** (Vite + Tailwind) com formulário de pré-triagem
- Testes automatizados (pytest) com banco em memória
- Docker Compose (API + frontend)

Ainda **não** existem: login, painel da equipe, QR Code, PWA, NLP, FHIR.

## CPFs de teste (base simulada)

| CPF               | Paciente               |
|-------------------|------------------------|
| `529.982.247-25`  | Maria Eduarda da Silva |
| `111.444.777-35`  | João Pedro Santos      |

Qualquer outro CPF válido retorna "não encontrado" e o formulário pode ser
preenchido manualmente.

## Requisitos (Windows)

- Python 3.11 ou superior — marque "Add python.exe to PATH"
- Node.js 22 (LTS) ou superior
- Git (opcional, recomendado)

## Backend (PowerShell)

```powershell
cd MedEasy\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
copy ..\.env.example .env
uvicorn app.main:app --reload
```

- Health: http://127.0.0.1:8000/health
- Documentação interativa (fora de produção): http://127.0.0.1:8000/docs

Se o PowerShell bloquear a ativação do ambiente virtual, execute uma vez:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Frontend (outro terminal)

```powershell
cd MedEasy\frontend
npm install
npm run dev
```

Abra http://localhost:5173. A API é lida de `VITE_API_URL`
(padrão `http://127.0.0.1:8000`; veja `frontend/.env.example`).

## Testes

```powershell
cd MedEasy\backend
pytest -v
```

## Docker

```powershell
docker compose up --build
```

API em http://localhost:8000 e frontend em http://localhost:5173.
O banco SQLite fica no volume `medeasy_data`.

## Estrutura

```
MedEasy/
├── .env.example            # modelo de configuração (sem segredos)
├── .gitignore
├── .gitattributes
├── docker-compose.yml
├── README.md
├── docs/
│   └── CORRECOES.md        # o que foi corrigido em relação à versão anterior
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt / requirements-dev.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── main.py         # criação da aplicação
│   │   ├── config.py       # variáveis de ambiente
│   │   ├── database.py     # engine e sessão
│   │   ├── api/            # health.py, triagem.py (rotas)
│   │   ├── models/         # triagem.py (tabela)
│   │   ├── schemas/        # triagem.py (validação)
│   │   └── services/       # triagem_service.py, cpf_service.py
│   └── tests/
└── frontend/
    └── src/components/PreTriagem.jsx
```

## Segurança e LGPD

- `.env` está no `.gitignore`; nunca faça commit de senhas ou chaves.
- Documentação interativa é desativada com `ENVIRONMENT=production`.
- **A rota `GET /triagens/{id}` ainda não tem autenticação** e expõe dados de
  saúde. Proteja-a (login e perfis) antes de qualquer uso fora de demonstração.
- Dados de saúde são dados pessoais sensíveis (LGPD, art. 11). Use apenas dados
  fictícios até existir avaliação de segurança e base legal.
