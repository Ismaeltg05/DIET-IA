import React, { createContext, useContext, useEffect, useState } from 'react';
import { Appearance, Platform, View } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ThemeContext = createContext({
  theme: 'dark',
  toggleTheme: () => {}
});

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    const systemTheme = Appearance.getColorScheme();
    return systemTheme === 'light' ? 'light' : 'dark';
  });

  useEffect(() => {
    let isMounted = true;

    AsyncStorage.getItem('theme').then((savedTheme) => {
      if (!isMounted) return;

      if (savedTheme === 'light' || savedTheme === 'dark') {
        setTheme(savedTheme);
      }
    });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    AsyncStorage.setItem('theme', theme);

    if (Platform.OS === 'web' && typeof document !== 'undefined') {
      const root = document.documentElement;
      const body = document.body;

      root.classList.toggle('dark', theme === 'dark');
      body.classList.toggle('dark', theme === 'dark');
      root.style.colorScheme = theme;
      body.style.colorScheme = theme;
      body.style.backgroundColor = theme === 'dark' ? '#09090b' : '#f8fafc';
      body.style.color = theme === 'dark' ? '#fafafa' : '#09090b';
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <View className={`${theme === 'dark' ? 'dark bg-zinc-950' : 'bg-zinc-50'} flex-1`}>
        {children}
      </View>
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
