/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import React from 'react';
import { View } from 'react-native';
import { Stack } from 'expo-router';
import Navbar from '../../components/Navbar';

// Layout principal de la sección principal de la app.
// Este componente coloca el Stack de `expo-router` debajo de una barra
// de navegación inferior personalizada para que la navegación sea consistente.
export default function MainLayout() {
  return (
    <View className="flex-1">
      {/* Stack de pantallas: oculta cabecera nativa para usar Navbar personalizado */}
      <Stack screenOptions={{ headerShown: false }} style={{ flex: 1 }} />
      <Navbar />
    </View>
  );
}