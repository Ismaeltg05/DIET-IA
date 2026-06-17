export const translations = {
  es: {
    // Pantalla principal (index.tsx)
    home: {
      title: 'Accede a tu cuenta',
      loginBtn: 'Iniciar sesión',
      registerBtn: 'Crear cuenta',
      continueBtn: 'Continuar sin cuenta'
    },
    
    // Login
    login: {
      title: 'Iniciar sesión',
      email: 'Correo electrónico',
      password: 'Contraseña',
      loginBtn: 'Entrar',
      noAccount: '¿No tienes cuenta? Regístrate',
      errorEmail: 'Por favor, introduce un email válido',
      error: 'Error',
      success: 'Éxito',
      successMessage: 'ID usuario: {userId}'
    },

    // Register
    register: {
      title: 'Crear cuenta',
      email: 'Correo electrónico',
      password: 'Contraseña',
      confirmPassword: 'Confirmar contraseña',
      registerBtn: 'Registrarse',
      haveAccount: '¿Ya tienes cuenta? Inicia sesión',
      errorEmail: 'Por favor, introduce un email válido',
      errorPassword: 'Las contraseñas no coinciden',
      error: 'Error',
      success: 'Éxito',
      successMessage: 'Registro completado. ID usuario: {userId}'
    },

    // Perfil
    profile: {
      preferences: 'Preferencias',
      lactoseFree: 'Sin lactosa',
      lactoseFreeDisabled: 'Sin restricción',
      vegan: 'Vegano',
      veganDisabled: 'Sin preferencia vegana',
      glutenFree: 'Sin gluten',
      glutenFreeDisabled: 'Sin restricción de gluten',
      favoriteRecipes: 'Recetas Favoritas',
      ratedRecipes: 'Recetas Calificadas',
      logout: 'Cerrar Sesión',
      guest: 'Usuario'
    },

    // Recetas (listado)
    recipes: {
      title: 'Recetas 🍲',
      aiRecommender: 'Probar recomendador IA 🤖',
      aiDescription: 'Escribe tus ingredientes y encuentra una receta',
      ingredients: 'ingredientes',
      min: 'min'
    },

    // IA de Recetas
    ai: {
      title: 'IA Recetas 🍳',
      description: 'Escribe alimentos o una frase natural. La IA procesará el texto, extraerá los ingredientes y te recomendará la receta más parecida de la base de datos.',
      placeholder: 'Ej: Tengo tomate, cebolla, ajo y aceite de oliva',
      searchBtn: 'Buscar receta',
      similarity: 'Similitud',
      ingredients: 'Ingredientes',
      categories: 'Categorías',
      steps: 'Preparación',
      translating: 'Traduciendo recetas...'
    }
  },

  en: {
    // Home Screen (index.tsx)
    home: {
      title: 'Access your account',
      loginBtn: 'Login',
      registerBtn: 'Sign Up',
      continueBtn: 'Continue without account'
    },

    // Login
    login: {
      title: 'Login',
      email: 'Email',
      password: 'Password',
      loginBtn: 'Enter',
      noAccount: "Don't have an account? Sign up",
      errorEmail: 'Please enter a valid email',
      error: 'Error',
      success: 'Success',
      successMessage: 'User ID: {userId}'
    },

    // Register
    register: {
      title: 'Sign Up',
      email: 'Email',
      password: 'Password',
      confirmPassword: 'Confirm Password',
      registerBtn: 'Register',
      haveAccount: 'Already have an account? Login',
      errorEmail: 'Please enter a valid email',
      errorPassword: 'Passwords do not match',
      error: 'Error',
      success: 'Success',
      successMessage: 'Registration completed. User ID: {userId}'
    },

    // Profile
    profile: {
      preferences: 'Preferences',
      lactoseFree: 'Lactose Free',
      lactoseFreeDisabled: 'No restriction',
      vegan: 'Vegan',
      veganDisabled: 'No vegan preference',
      glutenFree: 'Gluten Free',
      glutenFreeDisabled: 'No gluten restriction',
      favoriteRecipes: 'Favorite Recipes',
      ratedRecipes: 'Rated Recipes',
      logout: 'Logout',
      guest: 'User'
    },

    // Recipes (listing)
    recipes: {
      title: 'Recipes 🍲',
      aiRecommender: 'Try AI Recommender 🤖',
      aiDescription: 'Write your ingredients and find a recipe',
      ingredients: 'ingredients',
      min: 'min'
    },

    // AI Recipes
    ai: {
      title: 'AI Recipes 🍳',
      description: 'Write foods or a natural sentence. The AI will process the text, extract the ingredients, and recommend the most similar recipe from the database.',
      placeholder: 'Ex: I have tomato, onion, garlic and olive oil',
      searchBtn: 'Search recipe',
      similarity: 'Similarity',
      ingredients: 'Ingredients',
      categories: 'Categories',
      steps: 'Steps',
      translating: 'Translating recipes...'
    }
  }
};
