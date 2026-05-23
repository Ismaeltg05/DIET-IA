const mongoose = require('mongoose');

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

recipeRatingSchema.index({ recipeId: 1, userId: 1 }, { unique: true });

module.exports = mongoose.model('RecipeRating', recipeRatingSchema);