/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import { Slot } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ThemeProvider } from '../components/ThemeProvider';

// @ts-ignore
import '../global.css';

// Layout raíz de la aplicación. Envuelve las pantallas con el proveedor de tema
// y SafeArea para respetar zonas seguras en dispositivos móviles.
export default function RootLayout() {
  return (
    <ThemeProvider>
      <SafeAreaProvider>
        <Slot />
      </SafeAreaProvider>
    </ThemeProvider>
  );
}