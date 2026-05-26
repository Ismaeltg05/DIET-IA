/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import { View, Text, TextInput, Pressable, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { useState } from 'react';

import { registerUser } from '../../services/auth';
import '../../global.css';

export default function Register() {
  const router = useRouter();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');

  const handleRegister = async () => {
    // Llamada al backend para crear un nuevo usuario.
    // No hay validación adicional aquí, se delega al backend.
    try {
      await registerUser(name, email, password, phone);

      Alert.alert('Éxito', 'Usuario creado');

      // Tras el registro, redirige al formulario de inicio de sesión
      // para que el usuario pueda acceder con sus nuevas credenciales.
      router.push('/(auth)/login');
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  return (
    <View className="flex-1 justify-center items-center p-4 bg-zinc-950 dark:bg-zinc-50">
      <View className="w-full max-w-md rounded-3xl p-6 bg-zinc-900 dark:bg-white border border-zinc-800 dark:border-zinc-200 shadow-xl shadow-black/20">
        <Text className="text-2xl font-semibold mb-2 text-white dark:text-zinc-950">
          Registrarse
        </Text>
        <Text className="text-zinc-400 dark:text-zinc-500 mb-6 text-sm">
          Crea tu cuenta para guardar tus recetas y valoraciones.
        </Text>

        <TextInput
          placeholder="Nombre"
          placeholderTextColor="#71717a"
          value={name}
          onChangeText={setName}
          className="w-full rounded-2xl border border-zinc-700 dark:border-zinc-200 mb-4 px-4 py-3 text-white dark:text-zinc-950 bg-zinc-950 dark:bg-zinc-50"
        />

        <TextInput
          placeholder="Correo electrónico"
          placeholderTextColor="#71717a"
          value={email}
          onChangeText={setEmail}
          className="w-full rounded-2xl border border-zinc-700 dark:border-zinc-200 mb-4 px-4 py-3 text-white dark:text-zinc-950 bg-zinc-950 dark:bg-zinc-50"
        />

        <TextInput
          placeholder="Teléfono (opcional)"
          placeholderTextColor="#71717a"
          value={phone}
          onChangeText={setPhone}
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
          onPress={handleRegister}
          className="bg-indigo-600 dark:bg-indigo-500 rounded-2xl px-6 py-4"
        >
          <Text className="text-white text-center font-semibold">
            Registrarse
          </Text>
        </Pressable>
      </View>
    </View>
  );
}