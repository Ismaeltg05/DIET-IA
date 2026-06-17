import { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  ActivityIndicator
} from 'react-native';

import '../../../global.css';
import API_URL from '../../../services/api';
import { translateIngredients, translateRecipe } from '../../../services/translation';
import { useLanguage } from '../../../context/LanguageContext';
import { useTranslations } from '../../../hooks/useTranslations';

export default function AIRecipes() {
  const [ingredientsText, setIngredientsText] = useState('');
  const [loading, setLoading] = useState(false);
  const [recipe, setRecipe] = useState(null);
  const { language } = useLanguage();
  const t = useTranslations();

  const handleRecommend = async () => {
    if (!ingredientsText.trim()) return;

    try {
      setLoading(true);

      let ingredients = ingredientsText
        .split(',')
        .map(i => i.trim())
        .filter(Boolean);

      // Si el idioma es español, traducir a inglés
      if (language === 'es') {
        ingredients = await translateIngredients(ingredients, 'es', 'en');
      }

      const response = await fetch(`${API_URL}/api/ai/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ ingredients })
      });

      const data = await response.json();

      // Si el idioma es español, traducir la receta de vuelta
      if (language === 'es') {
        const translatedRecipe = await translateRecipe(data, 'en', 'es');
        setRecipe(translatedRecipe);
      } else {
        setRecipe(data);
      }

    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView className="flex-1 bg-zinc-950 px-5 pt-12">
      <Text className="text-white text-3xl font-bold mb-2">
        {t.ai.title}
      </Text>

      <Text className="text-zinc-400 mb-8">
        {t.ai.description}
      </Text>

      <TextInput
        multiline
        value={ingredientsText}
        onChangeText={setIngredientsText}
        placeholder={t.ai.placeholder}
        placeholderTextColor="#71717a"
        className="bg-zinc-900 text-white p-4 rounded-2xl min-h-[120px] mb-5"
      />

      <Pressable
        onPress={handleRecommend}
        className="bg-indigo-600 py-4 rounded-2xl"
      >
        <Text className="text-white text-center font-semibold">
          {t.ai.searchBtn}
        </Text>
      </Pressable>

      {loading && (
        <ActivityIndicator
          size="large"
          className="mt-8"
        />
      )}

      {recipe && (
        <View className="bg-zinc-900 rounded-3xl p-5 mt-8">

          <Text className="text-white text-2xl font-bold mb-3">
            {recipe.Title}
          </Text>

          <Text className="text-indigo-400 mb-4">
            {t.ai.similarity}: {recipe.similarity_percent}%
          </Text>

          <Text className="text-white font-semibold mb-2">
            {t.ai.ingredients}
          </Text>

          {recipe.Ingredients?.map((ingredient, index) => (
            <Text
              key={index}
              className="text-zinc-300 mb-1"
            >
              • {ingredient}
            </Text>
          ))}

          <Text className="text-white font-semibold mt-5 mb-2">
            {t.ai.categories}
          </Text>

          <Text className="text-zinc-300">
            {recipe.Tags?.join(', ')}
          </Text>

          <Text className="text-white font-semibold mt-5 mb-2">
            {t.ai.steps}
          </Text>

          <Text className="text-zinc-300">
            {recipe.recipe?.Steps?.join('\n\n')}
          </Text>

        </View>
      )}

    </ScrollView>
  );
}