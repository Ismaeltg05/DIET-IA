# COPILOT.md — Project guide for DIET-IA (corrected)

Authors: Ismael Torres González, Francisco J. Salmerón Puig

Purpose
-------
This file is an operational guide for contributors working on the DIET-IA repository. Keep it concise and aligned with the actual codebase: do not add commands, ports, routes or paths that are not present in the repository.

Repository map
--------------

| Area | Path | Notes |
|---|---|---|
| Node backend | Backend/ | Express API (auth, recipes, proxy to AI). |
| AI backend | Backend/ai/ | FastAPI service: recommendations, user preferences, indexado, healthcheck. |
| Frontend apps | Frontend-APP/ | `Diet-ia-pruebas` is the active Expo app; `Diet-ia-Funcional` is an alternate variant. |
| Docker and proxy | docker-compose.yaml, nginx.conf | Orquestación local y proxy inverso. |
| Models and datasets | models/, Backend/datasets/ | Artefactos de modelos y conjuntos de datos usados por el backend AI. |
| Utility scripts | python/, pruebas/, api.py | Scripts de preprocesado, entrenamiento y utilidades. |

What each service does (summary)
--------------------------------

- `Backend/src/server.js` — inicia el API Node y monta rutas principales (`/auth`, `/api/recipes`, y el puente a AI en `/api/ai`).
- `Backend/ai/main.py` — expone el API AI con endpoints como `/api/ai/recommend` y `/api/ai/health` (ver código para la lista completa).
- Frontend services (`Frontend-APP/Diet-ia-pruebas/services`) consumen las APIs construyendo la `API_URL` adecuada.
- `api.py` es un script auxiliar/legacy (Flask) que carga modelos locales desde `models/` y puede usarse para pruebas ad-hoc.

Frontend screens (ubicación)
---------------------------

- `Frontend-APP/Diet-ia-pruebas/app/index.tsx` — entrypoint de Expo.
- `Frontend-APP/Diet-ia-pruebas/app/(auth)/login.jsx`, `register.jsx` — autenticación.
- `Frontend-APP/Diet-ia-pruebas/app/recipes/index.jsx` — listado de recetas.
- `Frontend-APP/Diet-ia-pruebas/app/recipes/ai.jsx` — flujo de recomendación AI.

Integration caveat (proxy)
-------------------------

There is a known compatibility hotspot: `Backend/src/routes/ai.js` forwards calls to the AI service using an internal URL that may be different from the FastAPI prefix. Always verify the proxy target and the FastAPI route names when modifying either service.

Runtime map
-----------

- In the compose setup, Nginx is the public entry point. Typical mappings:
	- `http://localhost` (80) → Nginx
	- Nginx proxies `/api/*` to the AI backend at `backend:8000` and routes `/auth/*` & `/api/recipes/*` to `backend-node:3000`.
- The AI service listens on port 8000 inside Docker (uvicorn) and on the same port when run locally.

Scripts and entrypoints
----------------------

- Node backend (`Backend/package.json`):
	- `npm run dev` — nodemon / development.
	- `npm start` — production start.
- Frontend (`Frontend-APP/Diet-ia-pruebas/package.json`):
	- `npm start` — `expo start`.
	- `npm run web`, `npm run android`, `npm run ios` — platform targets.
- AI backend (Docker):
	- `python3 -m uvicorn ai.main:app --host 0.0.0.0 --port 8000` (same command to run locally after installing requirements).

Local development order
-----------------------

Prefer `docker compose` when you need the whole stack:

```bash
docker compose up --build
```

If you run services manually, recommended order:
1. `mongo`
2. `kafka` (if used), `zookeeper` (if used)
3. `hbase` (if used)
4. `spark-master` / `spark-worker` (if used)
5. `backend` (FastAPI)
6. `backend-node` (Node/Express)
7. Frontend (Expo)

Environment variables (where to check)
-------------------------------------

- `Backend/ai/main.py` reads: `KAFKA_BOOTSTRAP_SERVERS`, `HBASE_HOST`, `HBASE_PORT`, `MONGO_URI`, `SPARK_MASTER`, `AI_MODEL_PATH`, `OPENAI_API_KEY`.
- `Backend/src/server.js` reads: `PORT`, `MONGO_URI` / DB settings and `NODE_ENV` (via dotenv).
- `Frontend-APP/Diet-ia-pruebas/services/api.js` reads: `EXPO_PUBLIC_API_URL` and falls back to the Expo host or `localhost:3000` for web.
- `docker-compose.yaml` sets some values (`NODE_ENV`, `PYTHONUNBUFFERED`, `PORT` mappings). Prefer `.env` for sensitive overrides in local development.

API and route conventions (quick reference)
-----------------------------------------

These are the route roots used across the repo; always verify the exact path in the implementation before relying on them in code or docs:

- Node: `/auth/login`, `/auth/register`, `/api/recipes`, (proxy) `/api/ai/recommend`.
- AI (FastAPI): `/api/ai/recommend`, `/api/ai/rate-recipe`, `/api/ai/user-preferences/{user_id}`, `/api/ai/ingredients-stats`, `/api/ai/health`.

Error handling
--------------

Frontend should handle both Node and FastAPI error shapes — read `error`, `detail` and `message` fields when present.

Data and artifact rules
-----------------------

- Raw datasets: `Backend/datasets/`.
- Trained models / tokenizers: `models/` (do not rename without updating loaders).
- Large binaries should live outside Git (use storage or registry) or be tracked via LFS if required.

Verification and troubleshooting
------------------------------

- After `docker compose up`, check the AI health via the proxied route: `http://localhost/api/ai/health`.
- If you see a `502` from Nginx, check `docker compose ps`, then `docker compose logs backend` and `backend-node` for errors.
- If frontend cannot reach APIs, inspect `EXPO_PUBLIC_API_URL` (frontend) and `nginx.conf` (proxy rules).

Files to check first when debugging
----------------------------------

- `Backend/src/server.js` — server wiring and mounted routes.
- `Backend/src/routes/ai.js` — Node → AI proxy implementation.
- `Backend/ai/main.py` — FastAPI endpoints and startup logic.
- `Frontend-APP/Diet-ia-pruebas/services/api.js` — base URL resolution.
- `docker-compose.yaml`, `nginx.conf` — runtime mappings.

Notes for future edits
---------------------

- Always edit these docs to reflect concrete code changes in the same commit.
- Do not assert ports, scripts, or routes that are not present in the repo.
- If you modify the AI API or the Node proxy, add a short compatibility note here describing the change and the required update on the other side.

