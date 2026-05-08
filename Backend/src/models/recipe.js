const mongoose = require("mongoose");

const recipeSchema = new mongoose.Schema({}, { strict: false });

// 👇 fuerza la colección "test"
module.exports = mongoose.model("Recipe", recipeSchema, "test");