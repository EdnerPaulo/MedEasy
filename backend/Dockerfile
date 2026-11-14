# Imagem base oficial do Python
FROM python:3.11-slim

WORKDIR /app

# Evita arquivos .pyc e garante logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Dependências do Python (camada em cache enquanto o requirements não mudar)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Usuário sem privilégios + pasta de dados (SQLite) com permissão de escrita
RUN useradd --create-home --uid 1000 app \
    && mkdir /data \
    && chown app:app /data

COPY . .

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
