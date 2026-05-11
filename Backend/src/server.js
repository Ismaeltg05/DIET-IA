require('dotenv').config();
const express = require('express');
const connectDB = require('./config/db');

const authRoutes = require('./routes/auth');
const aiRoutes = require('./routes/ai');


const app = express();

connectDB();

app.use(express.json());

const recipeRoutes = require("./routes/recipes");

app.use("/api/recipes", recipeRoutes);
app.use('/auth', authRoutes);
app.use('/api/ai', aiRoutes);

app.get('/', (req, res) => {
  res.json({ mensaje: 'API funcionando' });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
});