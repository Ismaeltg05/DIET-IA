DIET-IA — Documentación Detallada

Autor: Ismael Torres González y Francisco J. Salmerón Puig
=================================


Resumen
-------
Proyecto desarrollado por el IES Zaidín Vergeles que ofrece un asistente de recomendación de recetas basado en técnicas de IA y Big Data. Permite buscar y adaptar recetas según ingredientes disponibles, alergias, preferencias y objetivos nutricionales.

Autores:
- Francisco José Salmerón Puig
- Ismael Torres González

Contenido de este README
------------------------
- Resumen del proyecto y objetivos (copiado y ampliado desde el README original)
- Tecnologías usadas y para qué se utilizan
- Estructura del repositorio y explicación de los componentes clave
- Descripción detallada del código y de los endpoints principales
- Cómo ejecutar el proyecto (desarrollo y producción)
- Notas sobre datos y modelos
- Siguientes pasos recomendados

Tecnologías y propósito
-----------------------
- Python: lógica del backend AI, preprocesado y modelos (FastAPI, scripts de IA).
- FastAPI: servidor HTTP principal para servicios de IA (`/api/ai/*`) — rápido y fácil de documentar.
- sentence-transformers / Transformers: embeddings para similitud entre ingredientes/recetas (en `Backend/ai/recipe_ai.py`).
- Pandas / NumPy: carga y procesamiento de datasets de recetas.
- MongoDB: almacenamiento persistente de recetas y usuarios (contenedor `mongo`).
- Apache Spark: procesamiento a escala de datasets grandes (batch jobs opcionales).
- HBase: (opcional) almacenamiento de preferencias por usuario usado en la lógica del backend.
- Kafka: cola para métricas/ratings asíncronas.
- Node.js / Express (backend-node): endpoints para auth y gestión de recetas (ruteo hacia DB y al backend de IA desde frontend web/mobile).
- React Native + Expo: aplicación móvil / web multiplataforma (carpeta `Frontend-APP/*`).
- Tailwind CSS / Nativewind: estilos rápidos en frontend.
- Docker & docker-compose: orquestación de contenedores para reproducibilidad (servicios: backend, backend-node, nginx, mongo, kafka, hbase, spark, etc.).
- Nginx: reverse proxy y CORS handling (archivo `nginx.conf`).
- Power BI / Matplotlib: visualización y reporting (opcional fuera del repo).

Estructura del repositorio
--------------------------
Principales carpetas y su propósito:

- `Backend/` — Código del backend (Python + Node):
  - `Backend/ai/` — FastAPI + lógica de IA
    - `main.py` — Entrypoint FastAPI con endpoints `/api/ai/*` y arranque del modelo.
    - `recipe_ai.py` — Implementación del motor de similitud (`RecipeSimilarityAI`): carga dataset, embedder, cálculo de similitud y formateo de payload.
  - `Backend/src/` — Node.js server (auth, recipes, rutas que proxy a AI si procede).

- `Frontend-APP/` — Aplicación React Native (dos variantes: `Diet-ia-Funcional` y `Diet-ia-pruebas`):
  - `app/recipes/ai.jsx` — UI para pedir recomendación a la IA y mostrar receta recomendada.
  - `services/api.js` — lógica para construir `API_URL` en función de entorno y plataforma (web vs mobile).
  - `services/auth.js` — helpers de autenticación (login/register) que usan `buildApiUrl()`.

- `models/` — Modelos locales y artefactos (embeddings, safetensors, tokenizers).
- `datasets/` — CSV/JSON de recetas y splits `train.json`, `test.json`.
- `docker-compose.yaml` — Orquestación de servicios para desarrollo/pruebas.
- `nginx.conf` — Proxy reverso que enruta `/api/` hacia los backend apropiados y gestiona CORS.

Explicación del código clave
----------------------------
A continuación se detallan los archivos más importantes y su funcionamiento.

Backend — `Backend/ai/main.py`
- Inicia una app FastAPI que expone endpoints:
  - `GET /` — healthcheck básico.
  - `POST /api/ai/recommend` — recibe JSON con `{ ingredients: [..], user_id?: 'guest' }`, pide al `RecipeSimilarityAI` la mejor receta y devuelve un objeto con metadatos (incluyendo `SimilarityScore` y `SimilarityPercent`).
- En `startup_event` configura conexiones (Kafka) y lanza la inicialización del modelo de forma asíncrona para no bloquear el arranque.
- Usa HBase para cargar preferencias del usuario cuando están disponibles.

Backend AI — `Backend/ai/recipe_ai.py`
- `RecipeSimilarityAI`:
  - Carga datasets CSV (busca `datasets/RAW_recipes.csv`).
  - Normaliza columnas (títulos, ingredientes, instrucciones).
  - Crea o carga un embedder de `sentence-transformers` y computa embeddings normalizados para las recetas.
  - `recommend_best_recipe(ingredients)` genera embedding para la consulta, calcula producto punto (similaridad coseno si las embeddings están normalizadas) y selecciona el top-k. Devuelve un payload enriquecido con:
    - `IngredientsList`, `Tags`, `Steps`, `SimilarityScore` (valor en 0..1), `SimilarityPercent` (0..100), `contains_lactose`, `contains_gluten`, `is_vegetarian`, `is_vegan`.
  - Helpers para parsing de texto: normalización, división en pasos, extracción de tags.

Node API — `Backend/src/server.js` y rutas
- `server.js` arranca un servidor Node para manejar endpoints `/auth`, `/api/recipes` y actuar como gateway entre frontend y el backend AI (a veces reenvía peticiones a `http://localhost:8000` del servicio Python).
- Rutas en `Backend/src/routes/ai.js` hacen `fetch` hacia el backend AI cuando es necesario.

Frontend — `Frontend-APP/Diet-ia-pruebas`
- `services/api.js`:
  - Resuelve `API_URL` consultando `process.env.EXPO_PUBLIC_API_URL` y los indicadores de Expo para identificar el host cuando la app corre en dispositivo/emulador.
  - `buildApiUrl(path)` concatena el host base con el path y garantiza el puerto `3000` para el servicio Node cuando sea necesario.
- `app/recipes/ai.jsx`:
  - Formulario donde el usuario escribe ingredientes.
  - `handleRecommend` envía POST a `/api/ai/recommend` con `{ ingredients, user_id }` y muestra la receta recomendada.
  - Renderiza los campos devueltos por el backend: título, similitud, ingredientes, categorías y pasos (ahora también normaliza y muestra `SimilarityPercent`).
- `app/recipes/index.jsx`:
  - Lista de recetas (llama a `/api/recipes` para obtener listado).

Docker & despliegue local
-------------------------
- `docker-compose.yaml` define servicios: `mongo`, `zookeeper`, `hbase`, `kafka`, `spark-master`/`worker`, `backend` (FastAPI), `backend-node` (Node server), `nginx` (reverse proxy).
- Nginx enruta `/api/` a `backend` o `backend-node` según la ruta (ver `nginx.conf`).
- Para desarrollo local:

  1. Levantar contenedores:
     ```powershell
     docker compose up -d
     ```

  2. Ver logs (ejemplo):
     ```powershell
     docker compose logs backend --tail 200
     docker compose ps
     ```

  3. Si usas Expo (frontend):
     ```bash
     cd Frontend-APP/Diet-ia-pruebas
     npx expo start
     ```

Endpoints principales
--------------------
- `POST /api/ai/recommend` (FastAPI): petición con ingredientes, devuelve receta recomendada con `SimilarityScore` y `SimilarityPercent`.
- `GET /api/ai/health` (FastAPI): healthcheck del servicio AI.
- `GET /api/recipes` (Node): lista de recetas.
- `POST /auth/register` y `POST /auth/login` (Node): registro e inicio de sesión.

Datos y modelos
----------------
- `datasets/RAW_recipes.csv` — dataset principal para indexar y generar embeddings.
- `models/embedder/` — artefactos del modelo de embeddings cuando se usan modelos locales (safetensors, tokenizers). Si no están presentes, el sistema usa un modelo por defecto (`all-MiniLM-L6-v2`).

Explicación de la similitud (cómo se calcula)
---------------------------------------------
- Las recetas y la consulta de ingredientes se transforman a embeddings vectoriales (por `sentence-transformers`).
- Si las embeddings se normalizan, la similitud puede calcularse como producto punto (equivalente al coseno).
- El score devuelto en `SimilarityScore` suele estar en 0..1; `SimilarityPercent` = score * 100 con 2 decimales.

Cómo contribuir y próximos pasos
-------------------------------
- Documentar y versionar los modelos (indicar la versión exacta del embedder usada para reproducibilidad).
- Añadir tests unitarios y de integración para endpoints críticos (`/api/ai/recommend`, `/auth/*`).
- Mejorar la UI con detalles de explicación (por qué se eligió la receta: ingredientes coincidentes, penalizaciones por alérgenos, etc.).
- Añadir pipelines ETL reproducibles para actualizar el dataset con n8n o scripts programados.

Archivo creado
--------------
He añadido este archivo adicional `README_DETAILED.md` con la documentación extendida. Si quieres que reemplace el `README.md` original por este contenido o que genere también una versión en formato reducido, lo hago ahora.

Referencias rápidas a archivos clave
-----------------------------------
- `Backend/ai/main.py` — [Backend/ai/main.py](Backend/ai/main.py#L1-L240)
- `Backend/ai/recipe_ai.py` — [Backend/ai/recipe_ai.py](Backend/ai/recipe_ai.py#L1-L380)
- `Frontend` API builder — [Frontend-APP/Diet-ia-pruebas/services/api.js](Frontend-APP/Diet-ia-pruebas/services/api.js#L1-L80)
- UI recomendador — [Frontend-APP/Diet-ia-pruebas/app/recipes/ai.jsx](Frontend-APP/Diet-ia-pruebas/app/recipes/ai.jsx#L1-L240)
- Orquestación — [docker-compose.yaml](docker-compose.yaml#L1-L220)
- Nginx config — [nginx.conf](nginx.conf#L1-L200)

---
¿Deseas que:  
- Reemplace `README.md` por este fichero detallado?  
- Genere también un `README_ES.md` más corto para despliegue público?  
Indica tu preferencia y lo hago enseguida.