/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import { View, Text, TextInput, Pressable, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { useState } from 'react';

import { loginUser } from '../../services/auth';
import '../../global.css';

// Valida formato básico de email.
// Esta función no comprueba la existencia del dominio, solo el formato general.
const validarEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

export default function Login() {
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  const handleLogin = async () => {
    if (!validarEmail(email)) {
      const msg = 'Por favor, introduce un email válido';
      setLoginError(msg);
      Alert.alert('Error', msg);
      return;
    }

    // Envia las credenciales al backend y procesa la respuesta.
    try {
      setLoginError('');
      const data = await loginUser(email, password);

      console.log('Login correcto:', data);
      Alert.alert('Éxito', `ID usuario: ${data.userId}`);

      // Después de un inicio de sesión exitoso, redirige al inicio.
      router.push('/');
    } catch (error) {
      const message = (error && (error.message || String(error))) || 'Error al iniciar sesión';
      setLoginError(message);
      Alert.alert('Error', message);
    }
  };

  return (
    <View className="flex-1 justify-center items-center p-4 bg-zinc-950 dark:bg-zinc-50">
      <View className="w-full max-w-md rounded-3xl p-6 bg-zinc-900 dark:bg-white border border-zinc-800 dark:border-zinc-200 shadow-xl shadow-black/20">
        <Text className="text-2xl font-semibold mb-2 text-white dark:text-zinc-950">
          Iniciar sesión
        </Text>
        <Text className="text-zinc-400 dark:text-zinc-500 mb-6 text-sm">
          Accede para guardar tus valoraciones y preferencias.
        </Text>

        <TextInput
          placeholder="Correo electrónico"
          placeholderTextColor="#71717a"
          value={email}
          onChangeText={setEmail}
          className="w-full rounded-2xl border border-zinc-700 dark:border-zinc-200 mb-4 px-4 py-3 text-white dark:text-zinc-950 bg-zinc-950 dark:bg-zinc-50"
        />

        <TextInput
          placeholder="Contraseña"
          placeholderTextColor="#71717a"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
          className="w-full rounded-2xl border border-zinc-700 dark:border-zinc-200 mb-6 px-4 py-3 text-white dark:text-zinc-950 bg-zinc-950 dark:bg-zinc-50"
        />

        <Pressable
          onPress={handleLogin}
          className="bg-indigo-600 dark:bg-indigo-500 rounded-2xl px-6 py-4"
        >
          <Text className="text-white text-center font-semibold">
            Entrar
          </Text>
        </Pressable>

        {loginError ? (
          <Text className="text-red-400 text-center mt-3">{loginError}</Text>
        ) : null}

        <Pressable
          onPress={() => router.push('/(auth)/register')}
          className="mt-4"
        >
          <Text className="text-indigo-400 dark:text-indigo-500 text-center">
            ¿No tienes cuenta? Regístrate
          </Text>
        </Pressable>
      </View>
    </View>
  );
}