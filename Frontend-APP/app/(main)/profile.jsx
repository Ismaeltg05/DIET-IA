/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import { useEffect, useState } from 'react';
import {
  View,
  Text,
  Pressable,
  ScrollView,
  ActivityIndicator,
  FlatList
} from 'react-native';

import '../../global.css';
import ThemeToggle from '../../components/ThemeToggle';
import { useRouter } from 'expo-router';
import { getUserId, logout } from '../../services/auth';
import { useTranslations } from '../../hooks/useTranslations';

const toBool = (value) => {
  if (typeof value === 'boolean') return value;
  return String(value).toLowerCase() === 'true';
};

export default function Profile() {
  // Estado del perfil: ID, nombre, preferencias y listas relacionadas.
  const [userId, setUserId] = useState('guest');
  const [userName, setUserName] = useState('Usuario');
  const [preferences, setPreferences] = useState({
    lactose_intolerant: false,
    vegan: false,
    gluten_free: false
  });

  const [prefsMessage, setPrefsMessage] = useState('');
  const [favoriteRecipes, setFavoriteRecipes] = useState([]);
  const [ratedRecipes, setRatedRecipes] = useState([]);
  const router = useRouter();
  const t = useTranslations();

  const preferenceOptions = [
    {
      key: 'lactose_intolerant',
      label: t.profile.lactoseFree,
      icon: '🥛',
      disabledLabel: t.profile.lactoseFreeDisabled
    },
    {
      key: 'vegan',
      label: t.profile.vegan,
      icon: '🥦',
      disabledLabel: t.profile.veganDisabled
    },
    {
      key: 'gluten_free',
      label: t.profile.glutenFree,
      icon: '🌾',
      disabledLabel: t.profile.glutenFreeDisabled
    }
  ];

  const togglePreference = (key) => {
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (err) {
      console.warn('Error cerrando sesión:', err);
    } finally {
      router.push('/');
    }
  };

  useEffect(() => {
    const loadInitialState = async () => {
      let resolvedUserId = 'guest';

      try {
        const storedUserId = await getUserId();
        resolvedUserId = storedUserId || 'guest';
        setUserId(resolvedUserId);

        // Actualmente solo se utiliza el ID como nombre de usuario.
        // En una versión futura, se debe solicitar el nombre real al backend.
        setUserName(resolvedUserId);
      } catch {
        setUserId('guest');
      }

      // Preferencias por defecto (sin carga del servidor)
      setPreferences({
        lactose_intolerant: false,
        vegan: false,
        gluten_free: false
      });
    };

    loadInitialState();
  }, []);

  const handleSavePreferences = async () => {
    // Nota: Las preferencias se guardan localmente pero no se persisten en el backend
    // ya que el servicio services/ai.js no existe
    setPrefsMessage('Preferencias actualizadas (solo en local)');
  };

  return (
    <ScrollView className="flex-1 bg-zinc-950 dark:bg-zinc-50 px-5 pt-12 pb-28">
      {/* Header con nombre del usuario */}
      <View className="mb-4">
        <Text className="text-white dark:text-zinc-950 text-3xl font-bold mb-2">
          Perfil 👤
        </Text>
        <Text className="text-white dark:text-zinc-950 text-xl font-semibold mb-1">
          {userName}
        </Text>
        <Text className="text-zinc-400 dark:text-zinc-600 text-sm">
          ID: {userId}
        </Text>
      </View>
      <View className="mb-6">
        <ThemeToggle />
      </View>

      {/* Preferencias del usuario */}
      <View className="bg-zinc-900 dark:bg-zinc-100 rounded-2xl p-4 mb-6">
        <Text className="text-white dark:text-zinc-950 font-semibold mb-4 text-lg">
          {t.profile.preferences}
        </Text>

        {preferenceOptions.map((option) => {
          const isActive = preferences[option.key];
          return (
            <Pressable
              key={option.key}
              onPress={() => togglePreference(option.key)}
              className={`rounded-3xl p-4 mb-3 flex-row items-center justify-between ${isActive ? 'bg-emerald-600' : 'bg-zinc-800 dark:bg-zinc-200 opacity-70'}`}
            >
              <View className="flex-row items-center gap-3">
                <View className={`w-12 h-12 rounded-3xl items-center justify-center ${isActive ? 'bg-emerald-700 dark:bg-emerald-600' : 'bg-zinc-700 dark:bg-zinc-300'}`}>
                  <Text className="text-2xl">{option.icon}</Text>
                </View>
                <View>
                  <Text className="text-white dark:text-zinc-950 font-semibold text-base">
                    {option.label}
                  </Text>
                  <Text className="text-zinc-300 dark:text-zinc-600 text-xs">
                    {isActive ? 'Activado' : option.disabledLabel}
                  </Text>
                </View>
              </View>
              <Text className={`text-sm font-semibold ${isActive ? 'text-white' : 'text-zinc-400 dark:text-zinc-500'}`}>
                {isActive ? 'Sí' : 'No'}
              </Text>
            </Pressable>
          );
        })}

        <Pressable
          onPress={handleSavePreferences}
          className="bg-emerald-600 py-3 rounded-xl"
        >
          <Text className="text-white text-center font-semibold">
            Guardar preferencias
          </Text>
        </Pressable>

        {!!prefsMessage && (
          <Text className="text-zinc-300 dark:text-zinc-700 mt-3 text-xs">
            {prefsMessage}
          </Text>
        )}
      </View>

      {/* Mis recetas favoritas */}
      <View className="bg-zinc-900 dark:bg-zinc-100 rounded-2xl p-4 mb-6">
        <Text className="text-white dark:text-zinc-950 font-semibold mb-4 text-lg">
          ❤️ {t.profile.favoriteRecipes}
        </Text>

        {favoriteRecipes.length === 0 ? (
          <Text className="text-zinc-400 dark:text-zinc-600 text-sm">
            Aún no tienes recetas favoritas. Agrega algunas desde la sección de recetas.
          </Text>
        ) : (
          <FlatList
            scrollEnabled={false}
            data={favoriteRecipes}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <View className="bg-zinc-800 dark:bg-zinc-200 rounded-lg p-3 mb-2">
                <Text className="text-white dark:text-zinc-950 font-semibold">
                  {item.title}
                </Text>
                <Text className="text-zinc-400 dark:text-zinc-600 text-xs">
                  {item.description}
                </Text>
              </View>
            )}
          />
        )}
      </View>

      {/* Recetas que califiqué */}
      <View className="bg-zinc-900 dark:bg-zinc-100 rounded-2xl p-4 mb-20">
        <Text className="text-white dark:text-zinc-950 font-semibold mb-4 text-lg">
          ⭐ {t.profile.ratedRecipes}
        </Text>

        {ratedRecipes.length === 0 ? (
          <Text className="text-zinc-400 text-sm">
            Aún no has calificado recetas. Califica recetas desde la sección de IA.
          </Text>
        ) : (
          <FlatList
            scrollEnabled={false}
            data={ratedRecipes}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <View className="bg-zinc-800 dark:bg-zinc-200 rounded-lg p-3 mb-2">
                <Text className="text-white dark:text-zinc-950 font-semibold">
                  {item.title}
                </Text>
                <Text className="text-amber-400 text-sm">
                  Calificación: {item.rating} / 5 ⭐
                </Text>
                <Text className="text-zinc-400 dark:text-zinc-600 text-xs">
                  {item.date}
                </Text>
              </View>
            )}
          />
        )}
      </View>
      <Pressable
        onPress={handleLogout}
        className="bg-red-600 py-3 rounded-xl mt-4 mb-10"
      >
        <Text className="text-white text-center font-semibold">{t.profile.logout}</Text>
      </Pressable>
    </ScrollView>
  );
}
