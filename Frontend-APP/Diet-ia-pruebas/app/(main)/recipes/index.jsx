/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

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

        // Normaliza la respuesta del backend para aceptar ambos formatos:
        // - { recipes: [...] }
        // - [ ... ]

    fetchRecipes();
  }, []);

  const screenSurface = 'bg-zinc-950 dark:bg-zinc-50';
  const cardSurface = 'bg-zinc-900 dark:bg-white border border-zinc-800 dark:border-zinc-200 shadow-lg shadow-black/10 dark:shadow-zinc-300/40';
  const titleText = 'text-white dark:text-zinc-950';
  const bodyText = 'text-zinc-400 dark:text-zinc-600';

  return (
    <View className={`flex-1 ${screenSurface} p-4 pb-28`}>

      <View className={`mb-4 rounded-3xl p-5 ${cardSurface}`}>
        <Text className={`${titleText} text-2xl font-bold mb-2`}>
          Recetas 🍲
        </Text>
        <Text className={`${bodyText} text-sm leading-5`}>
          Explora la base de datos o usa la IA para encontrar una receta con lo que tengas a mano.
        </Text>
      </View>

      <Pressable
        onPress={() => router.push('/recipes/ai')}
        className="bg-indigo-600 dark:bg-indigo-500 p-4 rounded-3xl mb-5 border border-indigo-400/30 shadow-lg shadow-indigo-900/20"
      >
        <Text className="text-white text-center font-semibold text-base">
          Probar recomendador IA 🤖
        </Text>

        <Text className="text-indigo-100 dark:text-indigo-50/90 text-center text-xs mt-1">
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
        <Text className="text-red-500 dark:text-red-400 mb-4">
          {error}
        </Text>
      )}

      {/* Lista de recetas obtenidas del backend. Usa FlatList para
          renderizar de forma eficiente y manejar muchos elementos. */}
      <FlatList
        data={recipes}
        keyExtractor={(item, index) => item?._id || String(index)}
        renderItem={({ item }) => (
          <View className={`p-4 rounded-2xl mb-3 ${cardSurface}`}>
            <Text className={`${titleText} font-semibold`}>
              {item.nvmname || item.name || 'Receta sin nombre'}
            </Text>

            <Text className={`${bodyText} text-xs mt-1`}>
              {item.minutes || 0} min • {item.n_ingredients || 0} ingredientes
            </Text>
          </View>
        )}
      />

    </View>
  );
}