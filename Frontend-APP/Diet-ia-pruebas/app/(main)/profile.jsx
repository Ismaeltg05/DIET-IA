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
import { getUserId } from '../../services/auth';
import {
  getUserPreferences,
  saveUserPreferences
} from '../../services/ai';

const toBool = (value) => {
  if (typeof value === 'boolean') return value;
  return String(value).toLowerCase() === 'true';
};

export default function Profile() {
  // Estado del perfil: id, nombre, preferencias y listas del usuario
  const [userId, setUserId] = useState('guest');
  const [userName, setUserName] = useState('Usuario');
  const [preferences, setPreferences] = useState({
    lactose_intolerant: false,
    vegan: false,
    gluten_free: false
  });
  const [prefsLoading, setPrefsLoading] = useState(false);
  const [prefsMessage, setPrefsMessage] = useState('');
  const [favoriteRecipes, setFavoriteRecipes] = useState([]);
  const [ratedRecipes, setRatedRecipes] = useState([]);

  const preferenceOptions = [
    {
      key: 'lactose_intolerant',
      label: 'Sin lactosa',
      icon: '🥛',
      disabledLabel: 'Sin restricción'
    },
    {
      key: 'vegan',
      label: 'Vegano',
      icon: '🥦',
      disabledLabel: 'Sin preferencia vegana'
    },
    {
      key: 'gluten_free',
      label: 'Sin gluten',
      icon: '🌾',
      disabledLabel: 'Sin restricción de gluten'
    }
  ];

  const togglePreference = (key) => {
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  useEffect(() => {
    const loadInitialState = async () => {
      let resolvedUserId = 'guest';

      try {
        const storedUserId = await getUserId();
        resolvedUserId = storedUserId || 'guest';
        setUserId(resolvedUserId);
        // TODO: Traer el nombre del usuario desde el backend
        setUserName(resolvedUserId);
      } catch {
        setUserId('guest');
      }

      // Intentar recuperar preferencias del backend; si falla, usar valores por defecto
      try {
        const data = await getUserPreferences(resolvedUserId);
        const loadedPrefs = data?.preferences || {};

        setPreferences({
          lactose_intolerant: toBool(loadedPrefs.lactose_intolerant),
          vegan: toBool(loadedPrefs.vegan),
          gluten_free: toBool(loadedPrefs.gluten_free)
        });
      } catch {
        setPreferences({
          lactose_intolerant: false,
          vegan: false,
          gluten_free: false
        });
      }
    };

    loadInitialState();
  }, []);

  const handleSavePreferences = async () => {
    try {
      setPrefsLoading(true);
      setPrefsMessage('');

      await saveUserPreferences(userId || 'guest', preferences);
      setPrefsMessage('Preferencias guardadas correctamente');
    } catch (err) {
      setPrefsMessage(err.message || 'No se pudieron guardar las preferencias');
    } finally {
      setPrefsLoading(false);
    }
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
          Preferencias dietéticas
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
          disabled={prefsLoading}
          className="bg-emerald-600 py-3 rounded-xl"
        >
          <Text className="text-white text-center font-semibold">
            {prefsLoading ? 'Guardando...' : 'Guardar preferencias'}
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
          ❤️ Mis recetas favoritas
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
          ⭐ Recetas que califiqué
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
    </ScrollView>
  );
}
