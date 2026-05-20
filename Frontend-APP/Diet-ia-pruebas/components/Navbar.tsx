import React from 'react';
import { View, TouchableOpacity, Text } from 'react-native';
import { useRouter, usePathname } from 'expo-router';
import { useTheme } from './ThemeProvider';

const Navbar = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const router = useRouter();
  const pathname = usePathname();

  const navItems = [
    { name: 'Inicio', icon: '🏠', route: '/(main)/recipes' },
    { name: 'Perfil', icon: '👤', route: '/(main)/profile' },
    { name: 'IA', icon: '🤖', route: '/(main)/ai' },
  ];

  const isActive = (route: string) => {
    return pathname.startsWith(route);
  };

  return (
    <View className={`flex-row justify-around items-center ${isDark ? 'bg-zinc-950 border-t border-zinc-800' : 'bg-white border-t border-gray-200'} safe-area-inset-b`}>
      {navItems.map((item) => (
        <TouchableOpacity
          key={item.route}
          onPress={() => router.push(item.route)}
          className={`flex-1 items-center justify-center py-3 ${
            isActive(item.route) ? `${isDark ? 'bg-blue-900' : 'bg-blue-50'} border-t-2 border-blue-500` : ''
          }`}
        >
          <Text className={`text-2xl mb-1 ${isActive(item.route) ? 'text-blue-500' : isDark ? 'text-zinc-200' : 'text-gray-600'}`}>
            {item.icon}
          </Text>
          <Text
            className={`text-xs font-semibold ${
              isActive(item.route) ? 'text-blue-500' : isDark ? 'text-zinc-400' : 'text-gray-600'
            }`}
          >
            {item.name}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );
};

export default Navbar;
