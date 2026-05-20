import { View, Text, FlatList, Pressable, ActivityIndicator } from 'react-native';
import { useEffect, useState } from 'react';
import { useRouter } from 'expo-router';
import { buildApiUrl } from '../../../services/api';

import '../../../global.css';

export default function Recipes() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const fetchRecipes = async () => {
      try {
        setError('');
        setLoading(true);

        const res = await fetch(buildApiUrl('/api/recipes'));
        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.error || data.detail || 'No se pudieron cargar las recetas');
        }

        const normalizedRecipes = Array.isArray(data.recipes)
          ? data.recipes
          : Array.isArray(data)
            ? data
            : [];

        setRecipes(normalizedRecipes);
      } catch (error) {
        setError(error.message || 'Error de conexión con el backend');
      } finally {
        setLoading(false);
      }
    };

    fetchRecipes();
  }, []);

  return (
    <View className="flex-1 bg-zinc-950 dark:bg-zinc-50 p-4 pb-28">

      <Text className="text-white dark:text-zinc-950 text-2xl font-bold mb-4">
        Recetas 🍲
      </Text>

      <Pressable
        onPress={() => router.push('/recipes/ai')}
        className="bg-indigo-600 p-4 rounded-2xl mb-5"
      >
        <Text className="text-white text-center font-semibold">
          Probar recomendador IA 🤖
        </Text>

        <Text className="text-indigo-200 text-center text-xs mt-1">
          Escribe tus ingredientes y encuentra una receta
        </Text>
      </Pressable>

      {loading && (
        <ActivityIndicator
          size="large"
          className="mt-6"
        />
      )}

      {!loading && !!error && (
        <Text className="text-red-400 mb-4">
          {error}
        </Text>
      )}

      <FlatList
        data={recipes}
        keyExtractor={(item, index) => item?._id || String(index)}
        renderItem={({ item }) => (
          <View className="bg-zinc-800 dark:bg-zinc-200 p-4 rounded-xl mb-3">
            <Text className="text-white dark:text-zinc-950 font-semibold">
              {item.nvmname || item.name || 'Receta sin nombre'}
            </Text>

            <Text className="text-zinc-400 dark:text-zinc-600 text-xs mt-1">
              {item.minutes || 0} min • {item.n_ingredients || 0} ingredientes
            </Text>
          </View>
        )}
      />

    </View>
  );
}