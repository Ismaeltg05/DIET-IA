import { Text, View, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import { useEffect } from 'react';

import '../global.css';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    fetch('http://localhost:3000')
      .then(res => res.json())
      .then(data => console.log('Conectado al backend:', data))
      .catch(err => console.log('Error backend:', err));
  }, []);

  return (
    <View className="flex-1 bg-zinc-950 items-center justify-center px-6">

      <Text className="text-4xl font-extrabold text-white text-center mb-3">
        Bienvenido 🚀
      </Text>

      <Text className="text-zinc-400 text-center mb-10">
        Expo Router + NativeWind funcionando correctamente
      </Text>

      <View className="w-full max-w-sm bg-zinc-900 rounded-3xl p-6 shadow-lg">

        <Text className="text-white text-xl font-semibold text-center mb-6">
          Accede a tu cuenta
        </Text>

        <Pressable
          onPress={() => router.push('/(auth)/login')}
          className="bg-indigo-500 py-4 rounded-2xl active:bg-indigo-600 mb-4"
        >
          <Text className="text-white text-center font-semibold text-base">
            Iniciar sesión
          </Text>
        </Pressable>

        <Pressable
          onPress={() => router.push('/(auth)/register')}
          className="bg-zinc-800 py-4 rounded-2xl active:bg-zinc-700"
        >
          <Text className="text-white text-center font-semibold text-base">
            Crear cuenta
          </Text>
        </Pressable>
      </View>

      <Text className="text-zinc-600 text-xs mt-10">
        NativeWind + Expo Router
      </Text>

    </View>
  );
}