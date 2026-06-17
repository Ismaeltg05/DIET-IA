// Servicio de traducción usando Google Translate API
// Sin límites de llamadas, traducción infinita

const TRANSLATE_API = 'https://translate.googleapis.com/translate_a/element.js';

/**
 * Traduce texto de un idioma a otro usando la API de Google Translate
 * @param {string} text - Texto a traducir
 * @param {string} sourceLang - Idioma origen (ej: 'es', 'en')
 * @param {string} targetLang - Idioma destino (ej: 'en', 'es')
 * @returns {Promise<string>} Texto traducido
 */
export const translateText = async (text, sourceLang = 'es', targetLang = 'en') => {
  try {
    if (!text || !text.trim()) return text;

    // Usar el endpoint público de Google Translate
    const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${sourceLang}&tl=${targetLang}&dt=t&q=${encodeURIComponent(text)}`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    if (!response.ok) {
      console.warn('Translation API error:', response.status);
      return text;
    }

    const result = await response.json();
    
    // El resultado viene en formato: [[[translated_text, original_text, ...]]]
    if (result && result[0] && result[0][0] && result[0][0][0]) {
      return result[0][0][0];
    }
    
    return text;
  } catch (error) {
    console.error('Error translating text:', error);
    return text; // Retorna el texto original si hay error
  }
};

/**
 * Traduce un array de ingredientes
 * @param {Array<string>} ingredients - Array de ingredientes
 * @param {string} sourceLang - Idioma origen
 * @param {string} targetLang - Idioma destino
 * @returns {Promise<Array<string>>} Array de ingredientes traducidos
 */
export const translateIngredients = async (
  ingredients,
  sourceLang = 'es',
  targetLang = 'en'
) => {
  try {
    const translatedIngredients = await Promise.all(
      ingredients.map(ingredient => translateText(ingredient, sourceLang, targetLang))
    );
    return translatedIngredients;
  } catch (error) {
    console.error('Error translating ingredients:', error);
    return ingredients; // Retorna ingredientes originales si hay error
  }
};

/**
 * Traduce un objeto de receta completo
 * @param {Object} recipe - Objeto de receta con Title, Ingredients, Tags, Steps
 * @param {string} sourceLang - Idioma origen
 * @param {string} targetLang - Idioma destino
 * @returns {Promise<Object>} Receta traducida
 */
export const translateRecipe = async (
  recipe,
  sourceLang = 'en',
  targetLang = 'es'
) => {
  try {
    const translatedRecipe = { ...recipe };

    // Traducir título
    if (recipe.Title) {
      translatedRecipe.Title = await translateText(recipe.Title, sourceLang, targetLang);
    }

    // Traducir ingredientes
    if (recipe.Ingredients && Array.isArray(recipe.Ingredients)) {
      translatedRecipe.Ingredients = await translateIngredients(
        recipe.Ingredients,
        sourceLang,
        targetLang
      );
    }

    // Traducir tags/categorías
    if (recipe.Tags && Array.isArray(recipe.Tags)) {
      translatedRecipe.Tags = await translateIngredients(recipe.Tags, sourceLang, targetLang);
    }

    // Traducir pasos de preparación
    if (recipe.recipe?.Steps && Array.isArray(recipe.recipe.Steps)) {
      translatedRecipe.recipe.Steps = await Promise.all(
        recipe.recipe.Steps.map(step => translateText(step, sourceLang, targetLang))
      );
    }

    return translatedRecipe;
  } catch (error) {
    console.error('Error translating recipe:', error);
    return recipe; // Retorna receta original si hay error
  }
};

export default {
  translateText,
  translateIngredients,
  translateRecipe
};
