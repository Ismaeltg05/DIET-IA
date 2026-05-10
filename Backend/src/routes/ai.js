const express = require('express');
const router = express.Router();

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

    res.json(data);

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;