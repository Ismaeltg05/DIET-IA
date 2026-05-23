/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

const mongoose = require('mongoose');

/**
 * connectDB
 * Conecta a MongoDB usando la variable de entorno `MONGO_URI`.
 * - Si la conexión falla, termina el proceso para que el orquestador
 *   pueda reiniciar el contenedor (comportamiento intencional).
 */
const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI);
    console.log('Mongo conectado');
  } catch (error) {
    console.error(error);
    // En entornos de producción se puede preferir reintento en lugar de exit
    process.exit(1);
  }
};

module.exports = connectDB;