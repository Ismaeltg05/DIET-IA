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

// Conectar a la base de datos (MongoDB)
connectDB();

// Middleware para parsear JSON en las peticiones entrantes
app.use(express.json());

const recipeRoutes = require("./routes/recipes");

// Rutas principales del servicio
app.use("/api/recipes", recipeRoutes); // CRUD y ratings sobre recetas
app.use('/auth', authRoutes); // Registro / Login
app.use('/api/ai', aiRoutes); // Proxy a microservicio AI (FastAPI)

// Ruta raíz simple para comprobación rápida
app.get('/', (req, res) => {
  res.json({ mensaje: 'API funcionando' });
});

const PORT = process.env.PORT || 3000;

// Arranca el servidor HTTP
app.listen(PORT, () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
});