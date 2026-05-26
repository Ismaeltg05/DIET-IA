/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

require('dotenv').config();
const express = require('express');
const connectDB = require('./config/db');

const authRoutes = require('./routes/auth');
const aiRoutes = require('./routes/ai');

/**
 * API principal del backend Node.js.
 * - Monta rutas de autenticación, recetas y proxy hacia el servicio AI.
 * - Conecta a MongoDB al arrancar.
 */
const app = express();

// Conectar a la base de datos MongoDB utilizando variables de entorno.
connectDB();

// Middleware que permite recibir JSON en el body de las peticiones.
app.use(express.json());

const recipeRoutes = require("./routes/recipes");

// Rutas principales del servicio
// - /api/recipes: operaciones sobre recetas y valoraciones.
// - /auth: registro e inicio de sesión.
// - /api/ai: proxy hacia el servicio AI de recomendación.
app.use("/api/recipes", recipeRoutes);
app.use('/auth', authRoutes);
app.use('/api/ai', aiRoutes);

// Ruta raíz simple para comprobación rápida del servicio.
// Esta ruta permite comprobar que el servidor está en línea
// sin necesidad de autenticación o servicios externos.
app.get('/', (req, res) => {
  res.json({ mensaje: 'API funcionando' });
});

const PORT = process.env.PORT || 3000;

// Arranca el servidor HTTP
app.listen(PORT, () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
});