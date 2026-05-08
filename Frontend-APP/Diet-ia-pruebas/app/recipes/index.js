import { View, Text, FlatList } from 'react-native';
import { useEffect, useState } from 'react';
import API_URL from '../../services/api';

import '../../global.css';

export default function Recipes() {
  const [recipes, setRecipes] = useState([]);

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