import { View, Text, TextInput, Pressable, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { useState } from 'react';

import { registerUser } from '../../services/auth';
import { useTranslations } from '../../hooks/useTranslations';
import '../../global.css';

export default function Register() {
  const router = useRouter();
  const t = useTranslations();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');

  const handleRegister = async () => {
    try {
      await registerUser(name, email, password, phone);

      Alert.alert(t.register.success, 'Usuario creado');

      router.push('/(auth)/login');

    } catch (error) {
      Alert.alert(t.register.error, error.message);
    }
  };

  return (
    <View className="flex-1 justify-center items-center p-4 bg-zinc-950">
      <Text className="text-2xl font-semibold mb-6 text-white">
        {t.register.title}
      </Text>

      <TextInput
        placeholder="Nombre"
        placeholderTextColor="#71717a"
        value={name}
        onChangeText={setName}
        className="w-full border-b border-zinc-700 mb-4 p-2 text-white"
      />

      <TextInput
        placeholder={t.register.email}
        placeholderTextColor="#71717a"
        value={email}
        onChangeText={setEmail}
        className="w-full border-b border-zinc-700 mb-4 p-2 text-white"
      />

      <TextInput
        placeholder="Teléfono (opcional)"
        placeholderTextColor="#71717a"
        value={phone}
        onChangeText={setPhone}
        className="w-full border-b border-zinc-700 mb-4 p-2 text-white"
      />

      <TextInput
        placeholder={t.register.password}
        placeholderTextColor="#71717a"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        className="w-full border-b border-zinc-700 mb-6 p-2 text-white"
      />

      <Pressable
        onPress={handleRegister}
        className="bg-indigo-600 rounded-full px-6 py-3"
      >
        <Text className="text-white font-semibold">
          {t.register.registerBtn}
        </Text>
      </Pressable>
    </View>
  );
}