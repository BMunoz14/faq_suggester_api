###############################################################################
#  Multi-stage build:                                                         #
#  1. builder -> instala dependencias en imagen liviana                       #
#  2. runtime -> copia venv y código; expone Uvicorn                          #
###############################################################################

FROM python:3.13-rc-slim AS builder
WORKDIR /app

# Dependencias del sistema (ChromaDB necesita gcc & libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

# Copiar metadatos del proyecto primero (mejor cache)
COPY pyproject.toml .
# Instalar Poetry core o usar pip con deps directas
RUN python -m pip install --upgrade pip \
 && python -m pip install "pip-tools>=7.4" \
 && pip-compile --output-file=requirements.txt pyproject.toml \
 && python -m pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# ═════════════════════════════════════════════════════════════════════════════
# Etapa de runtime – imagen ultra liviana con solo las libs ya compiladas
# ═════════════════════════════════════════════════════════════════════════════
FROM python:3.13-rc-slim AS runtime
WORKDIR /app

# Copiamos el site-packages ya construido
COPY --from=builder /usr/local /usr/local
# Copiamos solo la app (sin .git, docs, etc.)
COPY . .

ENV PYTHONUNBUFFERED=1
ENV UVICORN_CMD="uvicorn app.main:app --host 0.0.0.0 --port 8000"

EXPOSE 8000
CMD ["sh", "-c", "$UVICORN_CMD"]
