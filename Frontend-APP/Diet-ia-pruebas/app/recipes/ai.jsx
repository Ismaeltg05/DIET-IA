import { useEffect, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  ActivityIndicator
} from 'react-native';

import '../../global.css';
import { getUserId } from '../../services/auth';
import {
  getAiHealth,
  getUserPreferences,
  rateRecipe,
  recommendRecipe,
  saveUserPreferences
} from '../../services/ai';

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
  const aiReady = health === 'healthy';

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

  const handleRecommend = async () => {
    if (!ingredientsText.trim()) return;

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
      setRating(0);
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
    <ScrollView className="flex-1 bg-zinc-950 px-5 pt-12">

      <Text className="text-white text-3xl font-bold mb-2">
        IA Recetas 🍳
      </Text>

      <Text className="text-zinc-400 mb-8">
        Escribe alimentos o una frase natural.
        La IA procesará el texto, extraerá los ingredientes y te recomendará
        la receta más parecida de la base de datos.
      </Text>

      <Text className="text-zinc-500 mb-4">
        Estado backend AI: {health}
      </Text>

      {!aiReady && (
        <Text className="text-amber-300 mb-4 text-xs">
          El modelo de IA se esta cargando. Espera unos segundos y vuelve a intentarlo.
        </Text>
      )}

      <View className="bg-zinc-900 rounded-2xl p-4 mb-5">
        <Text className="text-white font-semibold mb-2">
          Preferencias del usuario ({userId})
        </Text>

        <Pressable
          onPress={() => setPreferences(prev => ({
            ...prev,
            lactose_intolerant: !prev.lactose_intolerant
          }))}
          className="bg-zinc-800 rounded-xl px-3 py-2 mb-2"
        >
          <Text className="text-zinc-200">
            Sin lactosa: {preferences.lactose_intolerant ? 'Si' : 'No'}
          </Text>
        </Pressable>

        <Pressable
          onPress={() => setPreferences(prev => ({
            ...prev,
            vegan: !prev.vegan
          }))}
          className="bg-zinc-800 rounded-xl px-3 py-2 mb-2"
        >
          <Text className="text-zinc-200">
            Vegano: {preferences.vegan ? 'Si' : 'No'}
          </Text>
        </Pressable>

        <Pressable
          onPress={() => setPreferences(prev => ({
            ...prev,
            gluten_free: !prev.gluten_free
          }))}
          className="bg-zinc-800 rounded-xl px-3 py-2 mb-3"
        >
          <Text className="text-zinc-200">
            Sin gluten: {preferences.gluten_free ? 'Si' : 'No'}
          </Text>
        </Pressable>

        <Pressable
          onPress={handleSavePreferences}
          disabled={prefsLoading}
          className="bg-emerald-600 py-3 rounded-xl"
        >
          <Text className="text-white text-center font-semibold">
            {prefsLoading ? 'Guardando...' : 'Guardar preferencias'}
          </Text>
        </Pressable>

        {!!prefsMessage && (
          <Text className="text-zinc-300 mt-3 text-xs">
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
        className="bg-zinc-900 text-white p-4 rounded-2xl min-h-[120px] mb-5"
      />

      <Pressable
        onPress={handleRecommend}
        disabled={!aiReady || loading}
        className={`py-4 rounded-2xl ${!aiReady || loading ? 'bg-zinc-700' : 'bg-indigo-600'}`}
      >
        <Text className="text-white text-center font-semibold">
          {loading ? 'Buscando...' : 'Buscar receta'}
        </Text>
      </Pressable>

      {!!error && (
        <Text className="text-red-400 mt-4">
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
        <View className="bg-zinc-900 rounded-3xl p-5 mt-8">

          <Text className="text-white text-2xl font-bold mb-3">
            {recipe.Title || recipe.title || 'Recomendación'}
          </Text>

          <Text className="text-indigo-400 mb-4">
            Similitud: {similarityValue != null ? `${similarityValue}%` : 'N/A'}
          </Text>

          <Text className="text-white font-semibold mb-2">
            Ingredientes
          </Text>

          {ingredientsList.map((ingredient, index) => (
            <Text
              key={index}
              className="text-zinc-300 mb-1"
            >
              • {ingredient}
            </Text>
          ))}

          <Text className="text-white font-semibold mt-5 mb-2">
            Categorías
          </Text>

          <Text className="text-zinc-300">
            {tagsList.join(', ')}
          </Text>

          <Text className="text-white font-semibold mt-5 mb-2">
            Preparación
          </Text>

          <Text className="text-zinc-300">
            {stepsList.join('\n\n')}
          </Text>

          <Text className="text-white font-semibold mt-5 mb-2">
            Valora esta receta
          </Text>

          <View className="flex-row gap-2">
            {[1, 2, 3, 4, 5].map((value) => (
              <Pressable
                key={value}
                onPress={() => handleRateRecipe(value)}
                disabled={ratingLoading}
                className={`px-3 py-2 rounded-lg ${rating === value ? 'bg-amber-500' : 'bg-zinc-700'}`}
              >
                <Text className="text-white font-semibold">{value}</Text>
              </Pressable>
            ))}
          </View>

          {!!ratingMessage && (
            <Text className="text-zinc-300 mt-3 text-xs">
              {ratingMessage}
            </Text>
          )}

        </View>
      )}

    </ScrollView>
  );
}