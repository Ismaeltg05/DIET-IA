/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

const mongoose = require('mongoose');

/**
 * Esquema de valoraciones de recetas.
 * - `rating` es un entero entre 1 y 5.
 * - Index compuesto (recipeId, userId) evita duplicados por usuario.
 */
const recipeRatingSchema = new mongoose.Schema({
  recipeId: {
    type: String,
    required: true,
    index: true
  },
  userId: {
    type: String,
    required: true,
    index: true
  },
  rating: {
    type: Number,
    required: true,
    min: 1,
    max: 5
  }
}, {
  timestamps: true
});

// Índice único para prevenir múltiples valoraciones del mismo usuario
recipeRatingSchema.index({ recipeId: 1, userId: 1 }, { unique: true });

module.exports = mongoose.model('RecipeRating', recipeRatingSchema);