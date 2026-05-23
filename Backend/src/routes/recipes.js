const express = require("express");
const router = express.Router();
const {
	getAllRecipes,
	getRecipeRatings,
	saveRecipeRating
} = require("../controllers/recipeController");

router.get("/", getAllRecipes);
router.get("/:recipeId/ratings", getRecipeRatings);
router.post("/:recipeId/ratings", saveRecipeRating);

module.exports = router;