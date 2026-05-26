/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

const express = require('express');
const router = express.Router();

const AI_SERVICE_BASE = 'http://localhost:8000';

const proxyRequest = async ({ req, res, path, method = 'GET', body }) => {
  try {
    const targetUrl = `${AI_SERVICE_BASE}${path}`;
    const response = await fetch(targetUrl, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: body ? JSON.stringify(body) : undefined
    });

    const data = await response.json().catch(() => ({}));
    return res.status(response.status).json(data);
  } catch (error) {
    return res.status(502).json({ error: 'AI service unavailable', detail: error.message });
  }
};

router.post('/recommend', async (req, res) => {
  return proxyRequest({
    req,
    res,
    path: '/api/ai/recommend',
    method: 'POST',
    body: req.body
  });
});

router.post('/batch-process', async (req, res) => {
  return proxyRequest({
    req,
    res,
    path: '/api/ai/batch-process',
    method: 'POST',
    body: req.body
  });
});

router.post('/rate-recipe', async (req, res) => {
  return proxyRequest({
    req,
    res,
    path: '/api/ai/rate-recipe',
    method: 'POST',
    body: req.body
  });
});

router.get('/ingredients-stats', async (req, res) => {
  return proxyRequest({
    req,
    res,
    path: '/api/ai/ingredients-stats',
    method: 'GET'
  });
});

router.get('/health', async (req, res) => {
  return proxyRequest({
    req,
    res,
    path: '/api/ai/health',
    method: 'GET'
  });
});

router.get('/user-preferences/:user_id', async (req, res) => {
  return proxyRequest({
    req,
    res,
    path: `/api/ai/user-preferences/${encodeURIComponent(req.params.user_id)}`,
    method: 'GET'
  });
});

router.post('/user-preferences/:user_id', async (req, res) => {
  return proxyRequest({
    req,
    res,
    path: `/api/ai/user-preferences/${encodeURIComponent(req.params.user_id)}`,
    method: 'POST',
    body: req.body
  });
});

module.exports = router;
