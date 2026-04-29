import { View, Text, TextInput, Pressable } from 'react-native';
import { useRouter } from 'expo-router';
import '../../global.css';
export default function Login() {
  const router = useRouter();

  return (
    <View className="flex-1 justify-center items-center p-4">
      <Text className="text-2xl font-semibold mb-6">Iniciar sesión</Text>

      <TextInput
        placeholder="Correo electrónico"
        className="w-full border-b mb-4 p-2"
      />
      <TextInput
        placeholder="Contraseña"
        secureTextEntry
        className="w-full border-b mb-6 p-2"
      />

      <Pressable
        onPress={() => {/* lógica de login */}}
        className="bg-indigo-600 rounded-full px-6 py-3"
      >
        <Text className="text-white font-semibold">Entrar</Text>
      </Pressable>

      <Pressable onPress={() => router.push('/(auth)/register')} className="mt-4">
        <Text className="text-indigo-600">¿No tienes cuenta? Regístrate</Text>
      </Pressable>
    </View>
  );
}