/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import React from 'react';
import { View, TouchableOpacity, Text } from 'react-native';
import { useRouter, usePathname } from 'expo-router';
import { useTheme } from './ThemeProvider';

const Navbar = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const router = useRouter();
  const pathname = usePathname();

  // Elementos visibles en la barra de navegación inferior.
  const navItems = [
    { name: 'Inicio', icon: '🏠', route: '/(main)/recipes' },
    { name: 'Perfil', icon: '👤', route: '/(main)/profile' },
    { name: 'IA', icon: '🤖', route: '/(main)/ai' },
  ];

  // Determina si la ruta actual corresponde al elemento activo.
  const isActive = (route: string) => {
    return pathname.startsWith(route);
  };

  return (
    // Barra de navegación inferior.
// Utiliza emojis como iconos y rutas de `expo-router` para cambiar de pantalla.
    <View className={`absolute bottom-0 left-0 right-0 z-50 flex-row justify-around items-center px-2 py-2 ${isDark ? 'bg-zinc-950/95 border-t border-zinc-800 shadow-black/20' : 'bg-white/95 border-t border-zinc-200 shadow-zinc-200/70'} safe-area-inset-b`}>
      {navItems.map((item) => (
        <TouchableOpacity
          key={item.route}
          onPress={() => router.push(item.route)}
          className={`flex-1 items-center justify-center py-3 rounded-2xl ${
            isActive(item.route)
              ? `${isDark ? 'bg-indigo-500/20 border border-indigo-400/30' : 'bg-indigo-50 border border-indigo-200'}`
              : ''
          }`}
        >
          <Text className={`text-2xl mb-1 ${isActive(item.route) ? 'text-indigo-500' : isDark ? 'text-zinc-200' : 'text-zinc-500'}`}>
            {item.icon}
          </Text>
          <Text
            className={`text-xs font-semibold ${
              isActive(item.route) ? 'text-indigo-500' : isDark ? 'text-zinc-400' : 'text-zinc-500'
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
