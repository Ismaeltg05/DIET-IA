import { View, Text, FlatList, Pressable } from 'react-native';
import { useEffect, useState } from 'react';
import { useRouter } from 'expo-router';
import API_URL from '../../services/api';

import '../../global.css';

export default function Recipes() {
  const [recipes, setRecipes] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const fetchRecipes = async () => {
      try {
        const res = await fetch(`${API_URL}/api/recipes`);
        const data = await res.json();
        setRecipes(data.recipes);
      } catch (error) {
        console.log(error);
      }
    };

    fetchRecipes();
  }, []);

  return (
    <View className="flex-1 bg-zinc-950 p-4">

      <Text className="text-white text-2xl font-bold mb-4">
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

      <FlatList
        data={recipes}
        keyExtractor={(item) => item._id}
        renderItem={({ item }) => (
          <View className="bg-zinc-800 p-4 rounded-xl mb-3">
            <Text className="text-white font-semibold">
              {item.nvmname}
            </Text>

            <Text className="text-zinc-400 text-xs mt-1">
              {item.minutes} min • {item.n_ingredients} ingredientes
            </Text>
          </View>
        )}
      />

    </View>
  );
}