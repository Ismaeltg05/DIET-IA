/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

import { Slot } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ThemeProvider } from '../components/ThemeProvider';
import { LanguageProvider } from '../context/LanguageContext';

// @ts-ignore
import '../global.css';

// Layout raíz de la aplicación.
// - LanguageProvider: controla el idioma global y sincroniza cambios en toda la app.
// - ThemeProvider: controla el tema oscuro/claro y aplica clases globales.
// - SafeAreaProvider: asegura que el contenido no se superponga con la barra
//   de estado ni con los bordes seguros de dispositivos modernos.
export default function RootLayout() {
  return (
    <LanguageProvider>
      <ThemeProvider>
        <SafeAreaProvider>
          <Slot />
        </SafeAreaProvider>
      </ThemeProvider>
    </LanguageProvider>
  );
}