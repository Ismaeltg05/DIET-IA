/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import { Slot } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ThemeProvider } from '../components/ThemeProvider';

// @ts-ignore
import '../global.css';

// Layout raíz de la aplicación.
// - ThemeProvider: controla el tema oscuro/claro y aplica clases globales.
// - SafeAreaProvider: asegura que el contenido no se superponga con la barra
//   de estado ni con los bordes seguros de dispositivos modernos.
export default function RootLayout() {
  return (
    <ThemeProvider>
      <SafeAreaProvider>
        <Slot />
      </SafeAreaProvider>
    </ThemeProvider>
  );
}