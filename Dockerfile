FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# 1) Edita el Dockerfile del API
cd ~/proyectos/multinicho/platform

cat > Dockerfile <<'DOCKER'
FROM python:3.11-slim

# Necesario para instalar dependencias VCS (git+https://...)
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# 🔒 Fuerza la instalación del paquete de agentes
RUN pip install --no-cache-dir git+https://github.com/toni22vidal-ux/agents.git@main

COPY . .

EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
