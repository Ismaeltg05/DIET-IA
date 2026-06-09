FROM node:20

# Python
RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app

# Copiar package.json y instalar dependencias Node
COPY package*.json ./
RUN npm install

# Copiar requirements.txt de la carpeta ai
COPY ai/requirements.txt ./ai/
RUN pip3 install --break-system-packages -r ./ai/requirements.txt

# Copiar TODO el código del backend incluyendo modelos entrenados
COPY . .

# Verificar que los archivos críticos existen
RUN echo "Verificando estructura de archivos..." && \
    ls -la ai/ && \
    test -f ai/main.py || echo "⚠️  main.py no encontrado" && \
    test -f ai/recipe_ai.py || echo "⚠️  recipe_ai.py no encontrado" && \
    test -d models || echo "⚠️  carpeta models no encontrada" && \
    echo "✅ Estructura verificada"

EXPOSE 3000
EXPOSE 8000

# Mostrar información sobre el modelo al iniciar
CMD echo "🚀 Iniciando backend..." && \
    echo "📁 Contenido de /app:" && \
    ls -la /app && \
    echo "📁 Contenido de /app/models:" && \
    ls -la /app/models 2>/dev/null || echo "Modelos no encontrados en /app/models" && \
    python3 -m uvicorn ai.main:app --host 0.0.0.0 --port 8000