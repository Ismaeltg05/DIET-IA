/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import { Text, Pressable } from 'react-native';
import { useTheme } from './ThemeProvider';

// Componente simple para alternar entre el modo oscuro y claro.
export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <Pressable
      onPress={toggleTheme}
      className={`rounded-2xl px-4 py-3 self-start border ${isDark ? 'bg-zinc-800 border-zinc-700' : 'bg-white border-zinc-200 shadow-sm'}`}
    >
      <Text className={`${isDark ? 'text-white' : 'text-zinc-950'} font-semibold`}>
        {isDark ? '🌙 Modo oscuro' : '☀️ Modo claro'}
      </Text>
    </Pressable>
  );
}
