/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import React, { createContext, useContext, useEffect, useState } from 'react';
import { Appearance, Platform, View } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ThemeContext = createContext({
  theme: 'dark',
  toggleTheme: () => {}
});

export function ThemeProvider({ children }) {
  // Inicializa el tema según la preferencia del sistema.
  const [theme, setTheme] = useState(() => {
    const systemTheme = Appearance.getColorScheme();
    return systemTheme === 'light' ? 'light' : 'dark';
  });

  useEffect(() => {
    let isMounted = true;

    // Recupera el tema guardado en AsyncStorage si existe.
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
    // Guarda el tema actual en AsyncStorage para que persista entre sesiones.
    AsyncStorage.setItem('theme', theme);

    if (Platform.OS === 'web' && typeof document !== 'undefined') {
      const root = document.documentElement;
      const body = document.body;

      // Aplica clases y estilos de tema en la versión web para mantener la
      // consistencia con el tema usado en la app nativa.
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
