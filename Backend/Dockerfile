FROM python:3.11-slim

# Autor: Ismael Torres González y Francisco J. Salmerón Puig
# Comentador: Ismael Torres González y Francisco J. Salmerón Puig

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements primero para aprovechar cache de capas de Docker
COPY ai/requirements.txt ./ai/requirements.txt

# Instala dependencias Python listadas en ai/requirements.txt
RUN pip install --no-cache-dir -r ./ai/requirements.txt

# Copia el código fuente del servicio AI al contenedor
COPY ai/ ./ai/

# Comprobación de salud expuesta por FastAPI en /api/ai/health
HEALTHCHECK --interval=15s --timeout=10s --retries=5 --start-period=10s \
    CMD curl -f http://localhost:8000/api/ai/health || exit 1

# Puerto expuesto por el servicio FastAPI (uvicorn)
EXPOSE 8000

# Comando por defecto: arrancar uvicorn para servir la API AI
CMD ["python3", "-m", "uvicorn", "ai.main:app", "--host", "0.0.0.0", "--port", "8000"]