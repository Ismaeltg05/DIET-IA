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
    try {
      await registerUser(name, email, password, phone);

      Alert.alert('Éxito', 'Usuario creado');

      router.push('/(auth)/login');

    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  return (
    <View className="flex-1 justify-center items-center p-4 bg-zinc-950 dark:bg-zinc-50">
      <Text className="text-2xl font-semibold mb-6 text-white dark:text-zinc-950">
        Registrarse
      </Text>

      <TextInput
        placeholder="Nombre"
        placeholderTextColor="#71717a"
        value={name}
        onChangeText={setName}
        className="w-full border-b border-zinc-700 dark:border-zinc-300 mb-4 p-2 text-white dark:text-zinc-950 bg-transparent dark:bg-transparent"
      />

      <TextInput
        placeholder="Correo electrónico"
        placeholderTextColor="#71717a"
        value={email}
        onChangeText={setEmail}
        className="w-full border-b border-zinc-700 dark:border-zinc-300 mb-4 p-2 text-white dark:text-zinc-950 bg-transparent dark:bg-transparent"
      />

      <TextInput
        placeholder="Teléfono (opcional)"
        placeholderTextColor="#71717a"
        value={phone}
        onChangeText={setPhone}
        className="w-full border-b border-zinc-700 dark:border-zinc-300 mb-4 p-2 text-white dark:text-zinc-950 bg-transparent dark:bg-transparent"
      />

      <TextInput
        placeholder="Contraseña"
        placeholderTextColor="#71717a"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        className="w-full border-b border-zinc-700 dark:border-zinc-300 mb-6 p-2 text-white dark:text-zinc-950 bg-transparent dark:bg-transparent"
      />

      <Pressable
        onPress={handleRegister}
        className="bg-indigo-600 rounded-full px-6 py-3"
      >
        <Text className="text-white font-semibold">
          Registrarse
        </Text>
      </Pressable>
    </View>
  );
}