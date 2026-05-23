/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import { Text, View, Pressable, Image, Animated, Dimensions } from 'react-native';
import { useRouter } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

import '../global.css';

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  // Tamaño responsive para móvil
  const logoSize = Dimensions.get('window').width * 0.22;

  // Animaciones
  const floatAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.85)).current;

  useEffect(() => {
    const checkUser = async () => {
      const userId = await AsyncStorage.getItem('userId');

      if (userId) {
        router.replace('/recipes');
      } else {
        setLoading(false);
      }
    };

    checkUser();

    // Animación suave
    Animated.parallel([
      Animated.spring(scaleAnim, {
        toValue: 1,
        friction: 5,
        useNativeDriver: true,
      }),

      Animated.loop(
        Animated.sequence([
          Animated.timing(floatAnim, {
            toValue: -6,
            duration: 1800,
            useNativeDriver: true,
          }),
          Animated.timing(floatAnim, {
            toValue: 0,
            duration: 1800,
            useNativeDriver: true,
          }),
        ])
      ),
    ]).start();
  }, []);

  if (loading) return null;

  return (
    <View className="flex-1 bg-zinc-950 dark:bg-zinc-50 justify-center items-center px-6">

      {/* Logo */}
      <Animated.View
        className="mb-8"
        style={{
          transform: [
            { translateY: floatAnim },
            { scale: scaleAnim },
          ],
        }}
      >
        <Image
          source={require('../assets/logo.png')}
          style={{
            width: logoSize,
            height: logoSize,
            borderRadius: logoSize / 2,
          }}
          resizeMode="cover"
        />
      </Animated.View>

      {/* Card */}
      <View className="w-full max-w-sm bg-zinc-900 dark:bg-zinc-100 rounded-3xl p-6">

        <Text className="text-white dark:text-zinc-950 text-xl font-semibold text-center mb-6">
          Accede a tu cuenta
        </Text>

        <Pressable
          onPress={() => router.push('/(auth)/login')}
          className="bg-indigo-500 py-4 rounded-2xl mb-4 active:opacity-80"
        >
          <Text className="text-white text-center font-semibold">
            Iniciar sesión
          </Text>
        </Pressable>

        <Pressable
          onPress={() => router.push('/(auth)/register')}
          className="bg-zinc-800 py-4 rounded-2xl mb-4 active:opacity-80"
        >
          <Text className="text-white text-center font-semibold">
            Crear cuenta
          </Text>
        </Pressable>

        <Pressable
          onPress={() => router.push('/recipes')}
          className="bg-green-600 py-4 rounded-2xl active:opacity-80"
        >
          <Text className="text-white text-center font-semibold">
            Continuar sin cuenta
          </Text>
        </Pressable>

      </View>

    </View>
  );
}