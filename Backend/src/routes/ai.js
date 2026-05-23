/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

const express = require('express');
const router = express.Router();

/**
 * Proxy simple hacia el microservicio AI (FastAPI) que corre en el puerto 8000.
 * Recibe un body con la petición de recomendación y la reenvía al servicio AI.
 * Esto desacopla el frontend/backend Node de detalles de implementación AI.
 */
router.post('/recommend', async (req, res) => {
  try {
    const response = await fetch('http://localhost:8000/recommend', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(req.body)
    });

    const data = await response.json();

    // Reenvía la respuesta tal cual al consumidor
    res.json(data);

  } catch (error) {
    // Errores de red o del servicio AI se transforman en 500 para el cliente
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;