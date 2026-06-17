import { View, Text, TextInput, Pressable, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { useState } from 'react';

import { loginUser } from '../../services/auth';
import { useTranslations } from '../../hooks/useTranslations';
import '../../global.css';

const validarEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

export default function Login() {
  const router = useRouter();
  const t = useTranslations();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    if (!validarEmail(email)) {
      Alert.alert(t.login.error, t.login.errorEmail);
      return;
    }

    try {
      const data = await loginUser(email, password);

      console.log('Login correcto:', data);

      Alert.alert(t.login.success, t.login.successMessage.replace('{userId}', data.userId));

      router.push('/');

    } catch (error) {
      Alert.alert(t.login.error, error.message);
    }
  };

  return (
    <View className="flex-1 justify-center items-center p-4 bg-zinc-950">
      <Text className="text-2xl font-semibold mb-6 text-white">
        {t.login.title}
      </Text>

      <TextInput
        placeholder={t.login.email}
        placeholderTextColor="#71717a"
        value={email}
        onChangeText={setEmail}
        className="w-full border-b border-zinc-700 mb-4 p-2 text-white"
      />

      <TextInput
        placeholder={t.login.password}
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
          {t.login.loginBtn}
        </Text>
      </Pressable>

      <Pressable
        onPress={() => router.push('/(auth)/register')}
        className="mt-4"
      >
        <Text className="text-indigo-400">
          {t.login.noAccount}
        </Text>
      </Pressable>
    </View>
  );
}