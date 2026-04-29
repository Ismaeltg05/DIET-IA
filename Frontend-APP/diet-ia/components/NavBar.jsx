import { View, Text, Pressable } from 'react-native';
import { useRouter } from 'expo-router';

export default function NavBar() {
  const router = useRouter();

  return (
    <View className="flex-row items-center justify-between p-4 bg-indigo-600">
      <Text className="text-white text-xl font-semibold">MiApp</Text>

      <View className="flex-row space-x-4">
        <Pressable onPress={() => router.push('/(auth)/login')}>
          <Text className="text-white">Login</Text>
        </Pressable>
        <Pressable onPress={() => router.push('/(auth)/register')}>
          <Text className="text-white">Registrarse</Text>
        </Pressable>
      </View>
    </View>
  );
}