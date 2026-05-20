import { Text, Pressable } from 'react-native';
import { useTheme } from './ThemeProvider';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <Pressable
      onPress={toggleTheme}
      className={`rounded-full px-4 py-3 self-start ${isDark ? 'bg-zinc-800' : 'bg-zinc-200'}`}
    >
      <Text className={`${isDark ? 'text-white' : 'text-zinc-950'} font-semibold`}>
        {isDark ? 'Modo oscuro' : 'Modo claro'}
      </Text>
    </Pressable>
  );
}
