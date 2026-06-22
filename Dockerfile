# ── Build Stage ──────────────────────────────────────────────
FROM python:3.11-slim

# Evita criação de arquivos .pyc e garante log em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema necessárias para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python primeiro (aproveita cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Cria o diretório de dados persistentes (para mídia, etc.)
RUN mkdir -p /app/data

# Porta exposta
EXPOSE 9020

ENV PORT=9020
ENV TZ=America/Sao_Paulo

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:9020", "--timeout", "120", "app:app"]
