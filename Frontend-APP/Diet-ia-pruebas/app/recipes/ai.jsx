import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  ActivityIndicator
} from 'react-native';

import '../../global.css';
import { buildApiUrl } from '../../services/api';
import { getUserId } from '../../services/auth';

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

      const response = await fetch(buildApiUrl('/api/ai/recommend'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ingredients,
          user_id: userId || 'guest'
        })
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.error || data.detail || 'No se pudo obtener recomendación');
      }

      setRecipe(data);

    } catch (error) {
      setError(error.message || 'Error de conexión con el backend');
    } finally {
      setLoading(false);
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
        className="bg-indigo-600 py-4 rounded-2xl"
      >
        <Text className="text-white text-center font-semibold">
          Buscar receta
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

        </View>
      )}

    </ScrollView>
  );
}