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

// Rutas relacionadas con recetas y valoraciones
router.get("/", getAllRecipes);
router.get("/:recipeId/ratings", getRecipeRatings);
router.post("/:recipeId/ratings", saveRecipeRating);

module.exports = router;