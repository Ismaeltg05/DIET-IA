/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

const express = require("express");
const router = express.Router();
const {
	getAllRecipes,
	getRecipeRatings,
	saveRecipeRating
} = require("../controllers/recipeController");

/**
 * Rutas de recetas y valoraciones.
 * - GET /api/recipes: obtiene todas las recetas disponibles.
 * - GET /api/recipes/:recipeId/ratings: obtiene estadísticas de rating para una receta.
 * - POST /api/recipes/:recipeId/ratings: guarda o actualiza la valoración de un usuario.
 */
router.get("/", getAllRecipes);
router.get("/:recipeId/ratings", getRecipeRatings);
router.post("/:recipeId/ratings", saveRecipeRating);

module.exports = router;