const Recipe = require("../models/Recipe");

exports.getAllRecipes = async (req, res) => {
  try {
    const recipes = await Recipe.find();

    return res.json({
      message: "Recetas obtenidas correctamente",
      count: recipes.length,
      recipes
    });

  } catch (error) {
    return res.status(500).json({
      error: error.message
    });
  }
};