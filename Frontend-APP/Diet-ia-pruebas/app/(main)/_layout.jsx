import React from 'react';
import { View } from 'react-native';
import { Stack } from 'expo-router';
import Navbar from '../../components/Navbar';

export default function MainLayout() {
  return (
    <View className="flex-1">
      <Stack screenOptions={{ headerShown: false }} style={{ flex: 1 }} />
      <Navbar />
    </View>
  );
}