const Recipe = require("../models/Recipe");
const RecipeRating = require("../models/recipeRating");

const isGuestUser = (userId) => {
  const normalizedUserId = String(userId || '').trim().toLowerCase();
  return !normalizedUserId || normalizedUserId === 'guest' || normalizedUserId === 'invitado';
};

const buildEmptyBreakdown = () => ({
  1: 0,
  2: 0,
  3: 0,
  4: 0,
  5: 0
});

const buildRatingSummary = async ({ recipeId, userId }) => {
  const [summary] = await RecipeRating.aggregate([
    {
      $match: {
        recipeId
      }
    },
    {
      $group: {
        _id: '$recipeId',
        count: { $sum: 1 },
        averageRating: { $avg: '$rating' }
      }
    }
  ]);

  const breakdownDocs = await RecipeRating.aggregate([
    {
      $match: {
        recipeId
      }
    },
    {
      $group: {
        _id: '$rating',
        count: { $sum: 1 }
      }
    }
  ]);

  const ratingBreakdown = buildEmptyBreakdown();

  breakdownDocs.forEach(({ _id, count }) => {
    const ratingValue = Number(_id);

    if (Number.isInteger(ratingValue) && ratingValue >= 1 && ratingValue <= 5) {
      ratingBreakdown[ratingValue] = count;
    }
  });

  const userRating = userId
    ? await RecipeRating.findOne({ recipeId, userId }).lean()
    : null;

  return {
    recipeId,
    ratingCount: summary?.count || 0,
    averageRating: summary ? Number(summary.averageRating.toFixed(2)) : null,
    ratingBreakdown,
    userHasRated: Boolean(userRating),
    userRating: userRating?.rating ?? null
  };
};

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

exports.getRecipeRatings = async (req, res) => {
  try {
    const { recipeId } = req.params;
    const { userId } = req.query;

    if (!recipeId) {
      return res.status(400).json({ error: 'recipeId es obligatorio' });
    }

    const summary = await buildRatingSummary({ recipeId: String(recipeId), userId: userId ? String(userId) : '' });

    return res.json({
      status: 'success',
      ...summary
    });
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
};

exports.saveRecipeRating = async (req, res) => {
  try {
    const { recipeId } = req.params;
    const { userId, rating } = req.body;

    if (!recipeId) {
      return res.status(400).json({ error: 'recipeId es obligatorio' });
    }

    if (!userId) {
      return res.status(400).json({ error: 'userId es obligatorio' });
    }

    if (isGuestUser(userId)) {
      return res.status(403).json({ error: 'Los usuarios invitados no pueden valorar recetas' });
    }

    const parsedRating = Number(rating);

    if (!Number.isInteger(parsedRating) || parsedRating < 1 || parsedRating > 5) {
      return res.status(400).json({ error: 'rating debe ser un entero entre 1 y 5' });
    }

    await RecipeRating.findOneAndUpdate(
      { recipeId: String(recipeId), userId: String(userId) },
      {
        $set: {
          rating: parsedRating
        }
      },
      {
        upsert: true,
        new: true,
        setDefaultsOnInsert: true
      }
    );

    const summary = await buildRatingSummary({ recipeId: String(recipeId), userId: String(userId) });

    return res.json({
      status: 'success',
      message: 'Valoración guardada correctamente',
      ...summary
    });
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
};