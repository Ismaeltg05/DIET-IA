/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import React from 'react';
import { View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Slot } from 'expo-router';
import Navbar from '../../components/Navbar';

// Layout principal de la sección principal de la app.
// Este componente coloca el Stack de `expo-router` debajo de una barra
// de navegación inferior personalizada para que la navegación sea consistente.
export default function MainLayout() {
  return (
    <SafeAreaView className="flex-1 bg-transparent">
      <View className="flex-1">
        {/* Slot de rutas: evita el stack nativo porque la navegación la controla Navbar */}
        <Slot />
      </View>
      <Navbar />
    </SafeAreaView>
  );
}