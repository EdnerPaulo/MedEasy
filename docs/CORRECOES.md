# O que foi corrigido

## Impediam o projeto de rodar
| Antes | Agora |
|---|---|
| `api/triagem.py` era uma cópia dos schemas, sem `router`; `main.py` falhava ao importar | `api/triagem.py` contém o roteador; a cópia dos schemas foi removida |
| `POST /triagens` e `GET /triagens/{id}` não existiam | Criados, usando o modelo e o serviço de classificação |
| `endpoints.py` com `/buscar-cpf` nunca era incluído | Rota movida para `api/triagem.py` e registrada em `/api/v1/triagens/buscar-cpf` |
| O modelo `TriagemModel` não era importado, então a tabela nunca era criada | Importado no `main.py`; tabelas criadas no `lifespan` |
| `date` não é serializável no campo JSON do banco | `model_dump(mode="json")` |
| Backend devolvia `"Vermelho"`, frontend comparava com `'VERMELHO'` | Tudo em MAIÚSCULAS, com cor para AZUL; sem "AMARELO" como padrão |

## Outras correções
- `database.py` agora usa `DATABASE_URL`; testes usam banco em memória.
- `services/_init__.py` renomeado para `__init__.py`.
- `if saturacao:` ignorava o valor 0; agora usa `is not None`.
- Queixa com sinais de alerta (dor no peito, falta de ar etc.) eleva o risco.
- CPF validado pelos dígitos verificadores; telefone normalizado.
- Consulta de CPF simulada deixou de devolver a mesma pessoa para qualquer CPF;
  campos do formulário agora são editáveis.
- Formulário com sinais vitais, erros na tela (sem `alert`), textos em pt-BR e
  aviso de projeto acadêmico. "Protocolo de Manchester" trocado por
  "classificação simplificada".
- `VITE_API_URL` em vez de URL fixa; `index.html` em pt-BR.
- Docker: `.dockerignore` dentro de `backend/`, usuário sem privilégios,
  volume para o banco, CORS configurado e serviço do frontend.
- Git: `.npm_cache` e `node_modules` ignorados; `.gitattributes` para quebras de linha.
- Removidos: `App.css` e assets do template do Vite (não usados);
  `httpx2` / `httpcore2` do `requirements-dev.txt` (o `httpx` já está no requirements).

## Não resolvido (de propósito)
- Autenticação e perfis de acesso.
- Painel da equipe com fila ordenada por risco.
- Provedor real de consulta de CPF.
