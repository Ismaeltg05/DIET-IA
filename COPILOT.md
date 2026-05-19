# COPILOT.md - Project Guide for DIET-IA

Author: Ismael Torres González

This file is the working guide for the DIET-IA repository. Keep it aligned with the actual codebase and avoid inventing commands, ports, routes, or folders that do not exist.

## Repository map

| Area | Path | Notes |
|---|---|---|
| Node backend | Backend/ | Express API with auth, recipes, and MongoDB models |
| AI backend | Backend/ai/ | FastAPI service for recommendations, user preferences, HBase, Kafka, and Spark jobs |
| Frontend apps | Frontend-APP/ | Diet-ia-pruebas is the active Expo app; Diet-ia-Funcional is the other variant |
| Docker and proxy | docker-compose.yaml, nginx.conf | Compose starts the full stack and Nginx routes traffic |
| Models and datasets | models/, datasets/, dataset/ | Trained artifacts and source data |
| Utility scripts | python/, pruebas/, colab/, api.py | Training, evaluation, notebooks, and a legacy standalone Flask API |

## What each service does

- Backend/src/server.js starts the Node API and mounts /auth, /api/recipes, and /api/ai.
- Backend/ai/main.py exposes the AI API with /api/ai/recommend, /api/ai/rate-recipe, /api/ai/user-preferences/{user_id}, /api/ai/ingredients-stats, and /api/ai/health.
- frontend services under Frontend-APP/Diet-ia-pruebas/services consume those APIs through buildApiUrl.
- api.py is a separate Flask script that loads local model artifacts from models/ and datasets/.

Frontend-APP/Diet-ia-pruebas screens

- app/index.tsx is the Expo entrypoint.
- app/(auth)/login.jsx and app/(auth)/register.jsx handle authentication.
- app/recipes/index.jsx lists recipes and navigates to the AI recommender.
- app/recipes/ai.jsx is the main AI flow: reads stored user id, fetches AI health, loads user preferences, saves preferences, requests recommendations, and sends recipe ratings.

Known integration caveat

- Backend/src/routes/ai.js currently forwards /api/ai/recommend to http://localhost:8000/recommend.
- Backend/ai/main.py exposes /api/ai/recommend, not /recommend.
- Treat that bridge as a compatibility hotspot and keep it synchronized with the Python service when making changes.

## Runtime map

- http://localhost:3000 goes through Nginx in the compose setup.
- Nginx proxies /api/* to the Python AI backend at backend:8000.
- Nginx proxies /auth/* and /api/recipes/* to the Node backend at backend-node:3000.
- The Node backend also proxies /api/ai/recommend to the AI service on http://localhost:8000/recommend.
- The AI service itself listens on port 8000 inside Docker and with uvicorn locally.

## Real scripts and entrypoints

Backend/package.json

- npm run dev starts nodemon src/server.js.
- npm start runs node src/server.js.

Frontend-APP/Diet-ia-pruebas/package.json

- npm start runs expo start.
- npm run web runs expo start --web.
- npm run android and npm run ios use Expo platform launchers.

Backend/ai

- docker-compose starts the AI service with python3 -m uvicorn ai.main:app --host 0.0.0.0 --port 8000.
- For local runs, use the same uvicorn command after installing Backend/ai/requirements.txt.

## Local development order

1. Prefer Docker Compose when you need the whole stack.

```bash
docker compose up --build
```

2. If you need to run services manually, start them in this order: MongoDB, Kafka, HBase, Spark, AI backend, Node backend, frontend.

3. For the Expo app, run the active project from Frontend-APP/Diet-ia-pruebas, not from the older variant unless you are comparing behavior.

## Environment variables that matter

- Backend/ai/main.py reads KAFKA_BOOTSTRAP_SERVERS, HBASE_HOST, HBASE_PORT, MONGO_URI, and SPARK_MASTER.
- Backend/src/server.js reads PORT and DB settings through dotenv.
- Frontend-APP/Diet-ia-pruebas/services/api.js reads EXPO_PUBLIC_API_URL and falls back to the Expo host or localhost:3000 on web.
- docker-compose.yaml also sets NODE_ENV and PYTHONUNBUFFERED for the backend containers.

## API and route conventions

- Use the existing Node routes: /auth/login, /auth/register, /api/recipes, /api/ai/recommend.
- Use the existing AI routes: /api/ai/recommend, /api/ai/batch-process, /api/ai/rate-recipe, /api/ai/user-preferences/{user_id}, /api/ai/ingredients-stats, /api/ai/health.
- Frontend error handling should read error, detail, and message because Node and FastAPI responses differ.
- Keep route handlers thin and push business logic into the owning module.
- When you touch the AI bridge in Node, verify both the proxy target and the FastAPI prefix before merging.

## Data and artifact rules

- Keep raw data in datasets/ and dataset/ unless the code is updated together.
- Keep trained model artifacts in models/ and do not move them without updating the loaders that reference them.
- Large binary artifacts should not be casually duplicated or renamed because the loaders use explicit paths.

## Development conventions

- Node code lives under Backend/src/ and is organized by routes, controllers, models, and config.
- Python AI code lives under Backend/ai/ and should stay safe for Docker healthchecks and reverse proxy routing.
- Prefer minimal controller logic and move business rules into the owning module or helper.
- Do not add new public ports unless docker-compose.yaml and nginx.conf are updated together.

## Verification and troubleshooting

- For the full stack, verify http://localhost:3000/api/ai/health after compose starts.
- If http://localhost:3000 returns 502, check the backend container health and confirm the AI service is listening on port 8000.
- If the frontend cannot reach the API, check EXPO_PUBLIC_API_URL and the logic in Frontend-APP/Diet-ia-pruebas/services/api.js.
- Run npm run lint in Frontend-APP/Diet-ia-pruebas when touching UI or service code.
- Run npm run dev in Backend/ only when you want the Node API without Docker.

## Files worth checking first

- Backend/src/server.js for server wiring and mounted routes.
- Backend/src/routes/ai.js for the Node-to-AI proxy call.
- Backend/ai/main.py for the FastAPI endpoints and health logic.
- Frontend-APP/Diet-ia-pruebas/services/api.js for base URL resolution.
- Frontend-APP/Diet-ia-pruebas/services/auth.js and services/ai.js for API usage.
- Frontend-APP/Diet-ia-pruebas/app/recipes/index.jsx and app/recipes/ai.jsx for the recipe browsing and recommendation flows.
- docker-compose.yaml and nginx.conf for runtime port mapping.

## Notes for future edits

- Do not replace real repo paths with examples from another machine or another project.
- Do not document commands that are not present in the relevant package.json or service entrypoint.
- If a script, port, route, or proxy changes, update this file in the same change.
