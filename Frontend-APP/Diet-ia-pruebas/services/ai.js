/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import { buildApiUrl } from './api';

const parseResponseJson = async (response) => {
  try {
    return await response.json();
  } catch {
    return {};
  }
};

const getApiErrorMessage = (data, fallbackMessage) => {
  return data.error || data.detail || data.message || fallbackMessage;
};

// Función genérica de petición al backend.
// - path: ruta relativa del endpoint.
// - method: método HTTP (GET, POST, etc.).
// - body: payload JSON opcional.
// - fallbackErrorMessage: mensaje por defecto si la API no proporciona uno.
const request = async ({ path, method = 'GET', body, fallbackErrorMessage }) => {
  const response = await fetch(buildApiUrl(path), {
    method,
    headers: {
      'Content-Type': 'application/json'
    },
    body: body ? JSON.stringify(body) : undefined
  });

  const data = await parseResponseJson(response);

  if (!response.ok) {
    throw new Error(getApiErrorMessage(data, fallbackErrorMessage));
  }

  // Retorna la respuesta JSON del endpoint cuando el estado HTTP es OK.
  return data;
};

// GET /
// Comprueba que el backend principal está disponible.
export const getApiRootStatus = async () => {
  return request({
    path: '/',
    fallbackErrorMessage: 'No se pudo consultar el estado del backend'
  });
};

// POST /api/ai/recommend
// Solicita al backend de IA una recomendación de receta basada en ingredientes.
export const recommendRecipe = async ({ ingredients, userId = 'guest' }) => {
  return request({
    path: '/api/ai/recommend',
    method: 'POST',
    body: {
      ingredients,
      user_id: userId
    },
    fallbackErrorMessage: 'No se pudo obtener recomendacion'
  });
};

// POST /api/ai/batch-process
// Inicia un procesamiento batch del servicio IA si está disponible.
export const startBatchProcess = async () => {
  return request({
    path: '/api/ai/batch-process',
    method: 'POST',
    fallbackErrorMessage: 'No se pudo iniciar el procesamiento batch'
  });
};

// POST /api/ai/rate-recipe
// Envía una valoración de receta asociada a un usuario.
export const rateRecipe = async ({ userId, recipeId, rating }) => {
  return request({
    path: `/api/recipes/${encodeURIComponent(recipeId)}/ratings`,
    method: 'POST',
    body: {
      userId,
      rating
    },
    fallbackErrorMessage: 'No se pudo enviar la valoracion'
  });
};

// GET /api/recipes/{recipe_id}/ratings
// Recupera el resumen de valoraciones para una receta específica.
export const getRecipeRatingSummary = async ({ userId, recipeId }) => {
  return request({
    path: `/api/recipes/${encodeURIComponent(recipeId)}/ratings?userId=${encodeURIComponent(userId || 'guest')}`,
    fallbackErrorMessage: 'No se pudo consultar la valoración de la receta'
  });
};

// GET /api/ai/user-preferences/{user_id}
// Obtiene las preferencias dietéticas guardadas del usuario.
export const getUserPreferences = async (userId) => {
  return request({
    path: `/api/ai/user-preferences/${encodeURIComponent(userId)}`,
    fallbackErrorMessage: 'No se pudieron cargar las preferencias del usuario'
  });
};

// POST /api/ai/user-preferences/{user_id}
// Guarda las preferencias dietéticas del usuario en el backend.
export const saveUserPreferences = async (userId, preferences) => {
  return request({
    path: `/api/ai/user-preferences/${encodeURIComponent(userId)}`,
    method: 'POST',
    body: {
      preferences
    },
    fallbackErrorMessage: 'No se pudieron guardar las preferencias'
  });
};

// GET /api/ai/ingredients-stats
// Solicita estadísticas de ingredientes a la IA.
export const getIngredientsStats = async () => {
  return request({
    path: '/api/ai/ingredients-stats',
    fallbackErrorMessage: 'No se pudieron obtener las estadisticas de ingredientes'
  });
};

// GET /api/ai/health
// Comprueba el estado del servicio de IA.
export const getAiHealth = async () => {
  return request({
    path: '/api/ai/health',
    fallbackErrorMessage: 'No se pudo consultar el estado de salud del backend AI'
  });
};

// Observaciones:
// - `services/ai.js` centraliza llamadas al backend AI (FastAPI).
// - Las funciones lanzan `Error` cuando la respuesta no es OK; el caller
//   debe manejar las excepciones y mostrar mensajes al usuario.
