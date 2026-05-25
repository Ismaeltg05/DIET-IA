# Instrucciones del proyecto DIET-IA

## 1. Visión general
Este proyecto contiene:
- Backend AI: `Backend/ai/main.py` y `Backend/ai/recipe_ai.py`.
- Backend Node: `Backend/src` para autenticación, recetas y valoraciones.
- Frontend Expo/React Native: `Frontend-APP/Diet-ia-pruebas`.
- Contenedores Docker para base de datos, mensajería, HBase, Spark y proxy Nginx.
- Scripts de entrenamiento en `python/train_recommender.py` y `python/ner_Salmeron.py`.

## 2. Requisitos previos
- Docker y Docker Compose instalados.
- Node.js y npm.
- Python 3.11 o superior.
- En Windows, usar PowerShell o WSL preferiblemente.

## 3. Entrenamiento de los modelos de IA

### 3.1 Modelo recomendador semántico
1. Ir a la raíz del proyecto:

```bash
cd C:\Users\Salmeron\Desktop\Diet-AI\DIET-IA
```

2. Crear y activar un entorno virtual:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# o
source .venv/bin/activate  # Linux/Mac
```

3. Instalar dependencias Python:

```bash
pip install --upgrade pip
pip install -r Backend/ai/requirements.txt
pip install joblib scikit-learn matplotlib sentence-transformers torch seqeval
```

4. Ejecutar el entrenamiento del recomendador:

```bash
python python/train_recommender.py
```

5. Artefactos generados:
- `models/best_nn_model.pkl`
- `models/best_nn_metadata.pkl`
- `models/embedder/`
- `datasets/df_recetas_processed.csv`
- `models/history_YYYYMMDD_HHMMSS.csv`
- `models/history_plot_YYYYMMDD_HHMMSS.png`

Este script carga `datasets/RAW_recipes.csv` y guarda el mejor modelo KNN y sus metadatos.

### 3.2 Modelo NER de ingredientes
1. Asegúrate de tener los archivos `datasets/train.json` y `datasets/val.json`.
2. Si no se tienen hay que ejecutar el archivo  `generatetraindata.py`
3. Ejecutar el entrenamiento NER:

```bash
python python/ner_Salmeron.py
```

3. Artefactos generados:
- `models/ner/` con el modelo BERT entrenado.

4. Ejecutar en GPU si está disponible:

```bash
set FORCE_CUDA=1
python python/ner_Salmeron.py
```

> Si no tienes los splits de entrenamiento, puedes generar datos sintéticos con `python/python/generatetraindata.py`.

## 4. Probar los modelos AI localmente sin Docker

### 4.1 Levantar FastAPI AI manualmente
1. Desde la raíz del proyecto:

```bash
cd C:\Users\Salmeron\Desktop\Diet-AI\DIET-IA\Backend
python -m uvicorn ai.main:app --host 0.0.0.0 --port 8000
```

2. Verificar estado:

```bash
curl http://localhost:8000/api/ai/health
```

### 4.2 Endpoints principales
- `GET http://localhost:8000/api/ai/health`
- `POST http://localhost:8000/api/ai/recommend`
- `POST http://localhost:8000/api/ai/rate-recipe`
- `GET http://localhost:8000/api/ai/user-preferences/{user_id}`
- `POST http://localhost:8000/api/ai/user-preferences/{user_id}`

Ejemplo de recomendación:

```bash
curl -X POST http://localhost:8000/api/ai/recommend \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["tomato", "olive oil"], "user_id": "guest"}'
```

## 5. Levantar el backend completo con Docker

### 5.1 Arrancar todos los servicios
Desde la raíz del proyecto:

```bash
cd C:\Users\Salmeron\Desktop\Diet-AI\DIET-IA
docker compose up --build
```

Este comando levanta:
- `mongo` (MongoDB)
- `zookeeper` y `kafka` (mensajería)
- `hbase` (preferencias)
- `spark-master` y `spark-worker` (Spark)
- `backend` (FastAPI AI)
- `backend-node` (API Node auth/recipes)
- `nginx` (proxy/reverse proxy)

### 5.2 Rutas de acceso
- `http://localhost/api/recipes`
- `http://localhost/api/ai/health`
- `http://localhost/docs`

Si `localhost:80` ya está ocupado, también puedes usar:
- `http://localhost:3000`

### 5.3 Detener los contenedores

```bash
docker compose down
```

Para eliminar volúmenes de datos:

```bash
docker compose down -v
```

## 6. Levantar el frontend localmente

### 6.1 Instalar dependencias del frontend

```bash
cd C:\Users\Salmeron\Desktop\Diet-AI\DIET-IA\Frontend-APP\Diet-ia-pruebas
npm install
```

### 6.2 Ejecutar Expo

```bash
npx expo start
```
### 6.3 Uso
- Abre la URL que muestra Expo DevTools.
- Usa Expo Go en tu móvil o el emulador.

> El frontend no está dockerizado en este repositorio, por lo que se ejecuta localmente con Expo.

## 7. Levantar el backend Node localmente (opcional)

### 7.1 Instalar dependencias Node

```bash
cd C:\Users\Salmeron\Desktop\Diet-AI\DIET-IA\Backend
npm install
```

### 7.2 Ejecutar en modo desarrollo

```bash
npm run dev
```

### 7.3 Probar la API Node
- `http://localhost:3000/api/recipes`
- `http://localhost:3000/auth/login`

> Si ejecutas este backend localmente, necesitarás MongoDB disponible. Puedes usar `docker compose up mongo` para levantar solo la base de datos.

## 8. Notas finales
- El servicio AI principal está en `Backend/ai/main.py`.
- El motor de similitud está en `Backend/ai/recipe_ai.py`.
- La configuración de proxy está en `nginx.conf`.
- Para una prueba completa en local, arranca Docker y luego ejecuta el frontend con Expo.
