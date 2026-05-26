/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

const mongoose = require("mongoose");

/**
 * Modelo de receta (schema flexible).
 * - `strict: false` permite guardar cualquier estructura de receta sin validación rígida,
 *   útil para prototipos o datasets heterogéneos.
 * - La colección forzada es `test` por compatibilidad con los datos actuales.
 */
const recipeSchema = new mongoose.Schema({}, { strict: false });

// 👇 fuerza la colección "test"
module.exports = mongoose.model("Recipe", recipeSchema, "test");