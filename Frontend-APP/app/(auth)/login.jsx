import { View, Text, TextInput, Pressable, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { useState } from 'react';

import { loginUser } from '../../services/auth';
import '../../global.css';

const validarEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

export default function Login() {
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    if (!validarEmail(email)) {
      Alert.alert('Error', 'Por favor, introduce un email válido');
      return;
    }

    try {
      const data = await loginUser(email, password);

      console.log('Login correcto:', data);

      Alert.alert('Éxito', `ID usuario: ${data.userId}`);

      router.push('/');

    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  return (
    <View className="flex-1 justify-center items-center p-4 bg-zinc-950">
      <Text className="text-2xl font-semibold mb-6 text-white">
        Iniciar sesión
      </Text>

      <TextInput
        placeholder="Correo electrónico"
        placeholderTextColor="#71717a"
        value={email}
        onChangeText={setEmail}
        className="w-full border-b border-zinc-700 mb-4 p-2 text-white"
      />

      <TextInput
        placeholder="Contraseña"
        placeholderTextColor="#71717a"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        className="w-full border-b border-zinc-700 mb-6 p-2 text-white"
      />

      <Pressable
        onPress={handleLogin}
        className="bg-indigo-600 rounded-full px-6 py-3"
      >
        <Text className="text-white font-semibold">
          Entrar
        </Text>
      </Pressable>

      <Pressable
        onPress={() => router.push('/(auth)/register')}
        className="mt-4"
      >
        <Text className="text-indigo-400">
          ¿No tienes cuenta? Regístrate
        </Text>
      </Pressable>
    </View>
  );
}