import { Text, View, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

import '../global.css';

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkUser = async () => {
      const userId = await AsyncStorage.getItem('userId');

      if (userId) {
        router.replace('/recipes'); // si ya está logueado
      } else {
        setLoading(false);
      }
    };

    checkUser();
  }, []);

  if (loading) return null;

  return (
    <View className="flex-1 bg-zinc-950 items-center justify-center px-6">

      <Text className="text-4xl font-extrabold text-white text-center mb-3">
        Bienvenido 🚀
      </Text>

      <Text className="text-zinc-400 text-center mb-10">
        Explora recetas o inicia sesión
      </Text>

      <View className="w-full max-w-sm bg-zinc-900 rounded-3xl p-6 shadow-lg">

        <Text className="text-white text-xl font-semibold text-center mb-6">
          Accede a tu cuenta
        </Text>

        <Pressable
          onPress={() => router.push('/(auth)/login')}
          className="bg-indigo-500 py-4 rounded-2xl mb-4"
        >
          <Text className="text-white text-center font-semibold">
            Iniciar sesión
          </Text>
        </Pressable>

        <Pressable
          onPress={() => router.push('/(auth)/register')}
          className="bg-zinc-800 py-4 rounded-2xl mb-4"
        >
          <Text className="text-white text-center font-semibold">
            Crear cuenta
          </Text>
        </Pressable>

        <Pressable
          onPress={() => router.push('/recipes')}
          className="bg-green-600 py-4 rounded-2xl"
        >
          <Text className="text-white text-center font-semibold">
            Continuar sin cuenta
          </Text>
        </Pressable>

      </View>

    </View>
  );
}