import { Text, View, Pressable } from 'react-native';
import { useRouter } from 'expo-router';

import '../global.css';

export default function Home() {
  const router = useRouter();

  return (
    <View className="flex-1 bg-zinc-950 items-center justify-center px-6">

      {/* Título */}
      <Text className="text-4xl font-extrabold text-white text-center mb-3">
        Bienvenido 🚀
      </Text>

      <Text className="text-zinc-400 text-center mb-10">
        Expo Router + NativeWind funcionando correctamente
      </Text>

      {/* Card */}
      <View className="w-full max-w-sm bg-zinc-900 rounded-3xl p-6 shadow-lg">

        <Text className="text-white text-xl font-semibold text-center mb-6">
          Accede a tu cuenta
        </Text>

        {/* Botón Login */}
        <Pressable
          onPress={() => router.push('/(auth)/login')}
          className="bg-indigo-500 py-4 rounded-2xl active:bg-indigo-600 mb-4"
        >
          <Text className="text-white text-center font-semibold text-base">
            Iniciar sesión
          </Text>
        </Pressable>

        {/* Botón Register */}
        <Pressable
          onPress={() => router.push('/(auth)/register')}
          className="bg-zinc-800 py-4 rounded-2xl active:bg-zinc-700"
        >
          <Text className="text-white text-center font-semibold text-base">
            Crear cuenta
          </Text>
        </Pressable>
      </View>

      {/* Footer */}
      <Text className="text-zinc-600 text-xs mt-10">
        NativeWind + Expo Router
      </Text>

    </View>
  );
}