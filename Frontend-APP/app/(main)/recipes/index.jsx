import { View, Text, FlatList, Pressable } from 'react-native';
import { useEffect, useState } from 'react';
import { useRouter } from 'expo-router';
import API_URL from '../../../services/api';
import { translateRecipe } from '../../../services/translation';
import { useLanguage } from '../../../context/LanguageContext';
import { useTranslations } from '../../../hooks/useTranslations';

import '../../../global.css';

export default function Recipes() {
  const [recipes, setRecipes] = useState([]);
  const [filteredRecipes, setFilteredRecipes] = useState([]);
  const [translatingIndex, setTranslatingIndex] = useState(null);
  const { language } = useLanguage();
  const t = useTranslations();
  const router = useRouter();

  useEffect(() => {
    const fetchRecipes = async () => {
      try {
        const res = await fetch(`${API_URL}/api/recipes`);
        const data = await res.json();
        setRecipes(data.recipes);
        setFilteredRecipes(data.recipes);
      } catch (error) {
        console.log(error);
      }
    };

    fetchRecipes();
  }, []);

  // Cuando cambia el idioma, traducir las recetas si es necesario
  useEffect(() => {
    const translateRecipes = async () => {
      if (language === 'es') {
        const translated = await Promise.all(
          recipes.map((recipe, index) => {
            setTranslatingIndex(index);
            return translateRecipe(recipe, 'en', 'es');
          })
        );
        setFilteredRecipes(translated);
        setTranslatingIndex(null);
      } else {
        setFilteredRecipes(recipes);
      }
    };

    translateRecipes();
  }, [language]);

  return (
    <View className="flex-1 bg-zinc-950 p-4">

      <Text className="text-white text-2xl font-bold mb-4">
        {t.recipes.title}
      </Text>

      <Pressable
        onPress={() => router.push('/recipes/ai')}
        className="bg-indigo-600 p-4 rounded-2xl mb-5"
      >
        <Text className="text-white text-center font-semibold">
          {t.recipes.aiRecommender}
        </Text>

        <Text className="text-indigo-200 text-center text-xs mt-1">
          {t.recipes.aiDescription}
        </Text>
      </Pressable>

      {translatingIndex !== null && (
        <Text className="text-zinc-400 text-center mb-4">
          {t.ai.translating}
        </Text>
      )}

      <FlatList
        data={filteredRecipes}
        keyExtractor={(item) => item._id}
        renderItem={({ item }) => (
          <View className="bg-zinc-800 p-4 rounded-xl mb-3">
            <Text className="text-white font-semibold">
              {item.nvmname}
            </Text>

            <Text className="text-zinc-400 text-xs mt-1">
              {item.minutes} {t.recipes.min} • {item.n_ingredients} {t.recipes.ingredients}
            </Text>
          </View>
        )}
      />

    </View>
  );
}