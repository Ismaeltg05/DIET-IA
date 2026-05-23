import { useEffect, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  ActivityIndicator
} from 'react-native';

import '../../../global.css';
import { getUserId } from '../../../services/auth';
import {
  getAiHealth,
  getRecipeRatingSummary,
  getUserPreferences,
  rateRecipe,
  recommendRecipe,
  saveUserPreferences
} from '../../../services/ai';

const toArray = (value) => {
  if (Array.isArray(value)) return value;
  if (typeof value === 'string') {
    return value
      .split(/[\n,|]/)
      .map(item => item.trim())
      .filter(Boolean);
  }
  return [];
};

export default function AIRecipes() {
  const [ingredientsText, setIngredientsText] = useState('');
  const [loading, setLoading] = useState(false);
  const [recipe, setRecipe] = useState(null);
  const [error, setError] = useState('');
  const [health, setHealth] = useState('checking');
  const [userId, setUserId] = useState('guest');
  const [preferences, setPreferences] = useState({
    lactose_intolerant: false,
    vegan: false,
    gluten_free: false
  });
  const [prefsLoading, setPrefsLoading] = useState(false);
  const [prefsMessage, setPrefsMessage] = useState('');
  const [rating, setRating] = useState(0);
  const [ratingLoading, setRatingLoading] = useState(false);
  const [ratingMessage, setRatingMessage] = useState('');
  const [ratingSummary, setRatingSummary] = useState(null);
  const aiReady = health === 'healthy';
  const isGuestUser = String(userId || '').trim().toLowerCase() === 'guest' || String(userId || '').trim().toLowerCase() === 'invitado';
  const screenSurface = 'bg-zinc-950 dark:bg-zinc-50';
  const cardSurface = 'bg-zinc-900 dark:bg-white border border-zinc-800 dark:border-zinc-200 shadow-sm shadow-black/20 dark:shadow-zinc-300/40';
  const cardMutedSurface = 'bg-zinc-800 dark:bg-zinc-100 border border-zinc-700 dark:border-zinc-200';
  const titleText = 'text-white dark:text-zinc-950';
  const bodyText = 'text-zinc-300 dark:text-zinc-600';
  const mutedText = 'text-zinc-400 dark:text-zinc-500';

  const preferenceOptions = [
    {
      key: 'lactose_intolerant',
      label: 'Sin lactosa',
      icon: '🥛',
      disabledLabel: 'Sin restricción'
    },
    {
      key: 'vegan',
      label: 'Vegano',
      icon: '🥦',
      disabledLabel: 'Sin preferencia vegana'
    },
    {
      key: 'gluten_free',
      label: 'Sin gluten',
      icon: '🌾',
      disabledLabel: 'Sin restricción de gluten'
    }
  ];

  const togglePreference = (key) => {
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const toBool = (value) => {
    if (typeof value === 'boolean') return value;
    return String(value).toLowerCase() === 'true';
  };

  useEffect(() => {
    const loadInitialState = async () => {
      let resolvedUserId = 'guest';

      try {
        const storedUserId = await getUserId();
        resolvedUserId = storedUserId || 'guest';
        setUserId(resolvedUserId);
      } catch {
        setUserId('guest');
      }

      try {
        const data = await getAiHealth();
        setHealth(data.overall || 'unknown');
      } catch {
        setHealth('offline');
      }

      try {
        const data = await getUserPreferences(resolvedUserId);
        const loadedPrefs = data?.preferences || {};

        setPreferences({
          lactose_intolerant: toBool(loadedPrefs.lactose_intolerant),
          vegan: toBool(loadedPrefs.vegan),
          gluten_free: toBool(loadedPrefs.gluten_free)
        });
      } catch {
        setPreferences({
          lactose_intolerant: false,
          vegan: false,
          gluten_free: false
        });
      }
    };

    loadInitialState();
  }, []);

  useEffect(() => {
    const loadRecipeRating = async () => {
      if (!recipe) {
        setRatingSummary(null);
        return;
      }

      const recipeId = String(recipe.recipe_id || recipe.id || recipe._id || recipe.Title || 'unknown');

      try {
        const data = await getRecipeRatingSummary({
          userId: userId || 'guest',
          recipeId
        });

        setRatingSummary(data);
        setRating(data.userRating || 0);
      } catch {
        setRatingSummary(null);
      }
    };

    loadRecipeRating();
  }, [recipe, userId]);

  const handleRecommend = async () => {
    if (!ingredientsText.trim() || loading) return;

    try {
      setError('');
      setLoading(true);
      setRecipe(null);

      const ingredients = ingredientsText
        .split(',')
        .map(i => i.trim())
        .filter(Boolean);

      const userId = await getUserId();

      const data = await recommendRecipe({
        ingredients,
        userId: userId || 'guest'
      });

      setRecipe(data);
      setRatingMessage('');

    } catch (error) {
      setError(error.message || 'Error de conexión con el backend');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreferences = async () => {
    try {
      setPrefsLoading(true);
      setPrefsMessage('');

      await saveUserPreferences(userId || 'guest', preferences);
      setPrefsMessage('Preferencias guardadas correctamente');
    } catch (err) {
      setPrefsMessage(err.message || 'No se pudieron guardar las preferencias');
    } finally {
      setPrefsLoading(false);
    }
  };

  const handleRateRecipe = async (value) => {
    if (!recipe) return;

    if (isGuestUser) {
      setRatingMessage('Los usuarios invitados no pueden valorar recetas');
      return;
    }

    const recipeId = String(recipe.recipe_id || recipe.id || recipe._id || recipe.Title || 'unknown');

    try {
      setRatingLoading(true);
      setRatingMessage('');
      setRating(value);

      await rateRecipe({
        userId: userId || 'guest',
        recipeId,
        rating: value
      });

      setRatingSummary(prev => prev ? {
        ...prev,
        userHasRated: true,
        userRating: value
      } : prev);
      setRating(value);
      setRatingMessage('Valoracion enviada');
    } catch (err) {
      setRatingMessage(err.message || 'No se pudo enviar la valoracion');
    } finally {
      setRatingLoading(false);
    }
  };

  const ingredientsList = toArray(recipe?.Ingredients ?? recipe?.ingredients ?? recipe?.recipe?.IngredientsList);
  const tagsList = toArray(recipe?.Tags ?? recipe?.tags ?? recipe?.recipe?.Tags);
  const stepsList = toArray(recipe?.recipe?.Steps ?? recipe?.steps ?? recipe?.Instructions ?? recipe?.instructions);

  const similarityValue = (() => {
    if (!recipe) return null;
    // Backend may return various keys (camelcase, PascalCase or snake_case)
    const percent = recipe.SimilarityPercent ?? recipe.similarity_percent ?? recipe.similarityPercent ?? recipe.similarity_percent;
    if (percent != null) return percent;

    const score = recipe.SimilarityScore ?? recipe.similarity_score ?? recipe.similarity ?? recipe.Score ?? null;
    if (score == null) return null;

    // If score looks like 0..1, convert to percent
    const num = Number(score);
    if (isNaN(num)) return null;
    return num > 1 ? num : Math.round(num * 10000) / 100; // keep 2 decimals
  })();

  return (
    <ScrollView className={`flex-1 ${screenSurface} px-5 pt-12 pb-28`}>

      <Text className={`${titleText} text-3xl font-bold mb-2`}>
        IA Recetas 🍳
      </Text>

      <Text className={`${bodyText} mb-8`}>
        Escribe alimentos o una frase natural.
        La IA procesará el texto, extraerá los ingredientes y te recomendará
        la receta más parecida de la base de datos.
      </Text>

      <Text className={`${mutedText} mb-4`}>
        Estado backend AI: {health}
      </Text>

      {!aiReady && (
        <Text className="text-amber-300 mb-4 text-xs">
          El modelo de IA se esta cargando. Espera unos segundos y vuelve a intentarlo.
        </Text>
      )}

      <View className={`rounded-3xl p-4 mb-5 ${cardSurface}`}>
        <Text className={`${titleText} font-semibold mb-2`}>
          Preferencias del usuario ({userId})
        </Text>

        {preferenceOptions.map((option) => {
          const isActive = preferences[option.key];
          return (
            <Pressable
              key={option.key}
              onPress={() => togglePreference(option.key)}
              className={`rounded-3xl p-4 mb-3 flex-row items-center justify-between border ${isActive ? 'bg-emerald-600 border-emerald-500' : 'bg-zinc-800 dark:bg-zinc-100 border-zinc-700 dark:border-zinc-200 opacity-100'}`}
            >
              <View className="flex-row items-center gap-3">
                <View className={`w-12 h-12 rounded-3xl items-center justify-center ${isActive ? 'bg-emerald-700' : 'bg-zinc-700 dark:bg-zinc-200 border border-zinc-600 dark:border-zinc-300'}`}>
                  <Text className="text-2xl">{option.icon}</Text>
                </View>
                <View>
                  <Text className={`${isActive ? 'text-white' : titleText} font-semibold text-base`}>
                    {option.label}
                  </Text>
                  <Text className={`${isActive ? 'text-white/90' : bodyText} text-xs`}>
                    {isActive ? 'Activado' : option.disabledLabel}
                  </Text>
                </View>
              </View>
              <Text className={`text-sm font-semibold ${isActive ? 'text-white' : mutedText}`}>
                {isActive ? 'Sí' : 'No'}
              </Text>
            </Pressable>
          );
        })}

        <Pressable
          onPress={handleSavePreferences}
          disabled={prefsLoading}
          className="bg-emerald-600 py-3 rounded-2xl shadow-sm shadow-emerald-900/10"
        >
          <Text className="text-white text-center font-semibold">
            {prefsLoading ? 'Guardando...' : 'Guardar preferencias'}
          </Text>
        </Pressable>

        {!!prefsMessage && (
          <Text className={`${bodyText} mt-3 text-xs`}>
            {prefsMessage}
          </Text>
        )}
      </View>

      <TextInput
        multiline
        value={ingredientsText}
        onChangeText={setIngredientsText}
        placeholder="Ej: Tengo tomate, cebolla, ajo y aceite de oliva"
        placeholderTextColor="#71717a"
        className="bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-950 border border-zinc-800 dark:border-zinc-200 rounded-3xl p-4 min-h-[120px] mb-5 shadow-sm shadow-black/20 dark:shadow-zinc-300/30"
      />

      <Pressable
        onPress={handleRecommend}
        className="py-4 rounded-2xl bg-indigo-600 dark:bg-indigo-500 shadow-lg shadow-indigo-900/20"
      >
        <Text className="text-white text-center font-semibold">
          {loading ? 'Buscando...' : 'Buscar receta'}
        </Text>
      </Pressable>

      {!!error && (
        <Text className="text-red-500 dark:text-red-400 mt-4">
          {error}
        </Text>
      )}

      {loading && (
        <ActivityIndicator
          size="large"
          className="mt-8"
        />
      )}

      {recipe && (
        <View className={`rounded-3xl p-5 mt-8 ${cardSurface}`}>

          <Text className={`${titleText} text-2xl font-bold mb-3`}>
            {recipe.Title || recipe.title || 'Recomendación'}
          </Text>

          <Text className="text-indigo-400 dark:text-indigo-500 mb-4">
            Similitud: {similarityValue != null ? `${similarityValue}%` : 'N/A'}
          </Text>

          <View className={`rounded-2xl p-4 mb-4 ${cardMutedSurface}`}>
            <Text className={`${titleText} font-semibold mb-1`}>
              Valoraciones
            </Text>
            <Text className={`${bodyText} text-sm`}>
              Cantidad: {ratingSummary?.ratingCount ?? 0}
            </Text>
            <Text className={`${bodyText} text-sm`}>
              Media: {ratingSummary?.averageRating != null ? `${ratingSummary.averageRating} / 5` : 'Aún sin valoraciones'}
            </Text>
            <Text className={`${bodyText} text-sm mt-1`}>
              {ratingSummary?.userHasRated
                ? `Ya la valoraste con ${ratingSummary.userRating} / 5`
                : 'Todavía no la has valorado'}
            </Text>

            <View className="mt-4 gap-2">
              {[5, 4, 3, 2, 1].map((value) => (
                <View key={value} className="flex-row items-center justify-between">
                  <Text className={`${bodyText} text-sm font-medium`}>
                    {value} estrella{value > 1 ? 's' : ''}
                  </Text>
                  <Text className={`${bodyText} text-sm font-semibold`}>
                    {ratingSummary?.ratingBreakdown?.[value] ?? 0}
                  </Text>
                </View>
              ))}
            </View>
          </View>

          <Text className={`${titleText} font-semibold mb-2`}>
            Ingredientes
          </Text>

          {ingredientsList.map((ingredient, index) => (
            <Text
              key={index}
              className={`${bodyText} mb-1`}
            >
              • {ingredient}
            </Text>
          ))}

          <Text className={`${titleText} font-semibold mt-5 mb-2`}>
            Categorías
          </Text>

          <Text className={bodyText}>
            {tagsList.join(', ')}
          </Text>

          <Text className={`${titleText} font-semibold mt-5 mb-2`}>
            Preparación
          </Text>

          <Text className={bodyText}>
            {stepsList.join('\n\n')}
          </Text>

          <Text className={`${titleText} font-semibold mt-5 mb-2`}>
            Valora esta receta
          </Text>

          {isGuestUser && (
            <Text className="text-amber-300 dark:text-amber-600 text-xs mb-3">
              Inicia sesión para poder valorar recetas.
            </Text>
          )}

          <View className="flex-row gap-2">
            {[1, 2, 3, 4, 5].map((value) => (
              <Pressable
                key={value}
                onPress={() => handleRateRecipe(value)}
                disabled={ratingLoading || isGuestUser}
                className={`px-3 py-2 rounded-lg border ${rating === value ? 'bg-amber-500 border-amber-400' : 'bg-zinc-700 dark:bg-zinc-200 border-zinc-600 dark:border-zinc-300'}`}
              >
                <Text className={`${rating === value ? 'text-white' : titleText} font-semibold`}>{value}</Text>
              </Pressable>
            ))}
          </View>

          {!!ratingMessage && (
            <Text className={`${bodyText} mt-3 text-xs`}>
              {ratingMessage}
            </Text>
          )}

        </View>
      )}

    </ScrollView>
  );
}