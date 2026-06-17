# Soporte Multiidioma - Implementación (ACTUALIZADO)

## Cambios Realizados

### 1. Servicio de Traducción (`services/translation.js`) - ACTUALIZADO
Se actualizo el servicio de traducción para usar la **API pública de Google Translate**.

**Características:**
- ✅ **Traducción infinita** - Sin límites de llamadas
- ✅ **Sin API key requerida**
- ✅ **Gratuita**
- ✅ **Traducción de alta calidad** (usa la misma que Google Translate)

**Funciones principales:**
- `translateText(text, sourceLang, targetLang)` - Traduce texto individual
- `translateIngredients(ingredients, sourceLang, targetLang)` - Traduce un array de ingredientes
- `translateRecipe(recipe, sourceLang, targetLang)` - Traduce una receta completa (título, ingredientes, tags, pasos)

### 2. Pantalla Principal (`app/index.tsx`) - NUEVA FUNCIONALIDAD
Se agregó selector de idioma debajo del botón "Continuar sin cuenta"

**Características:**
- ✅ Selector de idioma (Español/English) prominente
- ✅ Preferencia guardada en AsyncStorage
- ✅ Se persiste entre sesiones
- ✅ Botones visuales e intuitivos

### 3. Componente de IA de Recetas (`app/(main)/recipes/ai.jsx`)

**Cambios:**
- ✅ Lee idioma desde AsyncStorage al cargar
- ✅ Sincroniza con la selección global
- ✅ Mantiene selector de idioma para cambios rápidos
- ✅ Todos los textos de UI traducidos

**Flujo:**
1. Usuario selecciona idioma en pantalla principal (se guarda)
2. Componente IA carga ese idioma al inicializar
3. Usuario puede cambiar idioma en cualquier momento
4. Si es español → traducción automática a inglés → envío a IA
5. IA procesa y devuelve receta en inglés
6. Si está en español → traducción de receta a español

### 4. Componente de Listado de Recetas (`app/(main)/recipes/index.jsx`)

**Cambios:**
- ✅ Lee idioma desde AsyncStorage al cargar
- ✅ Las recetas se traducen a español automáticamente cuando se selecciona ese idioma
- ✅ Se mantiene caché de recetas en inglés original
- ✅ Interfaz completamente traducida
- ✅ Sincronización con selección global

## Cómo Funciona

### Flujo de Traducción - Ingredientes (IA):
```
Usuario (español) → "tomate, cebolla" 
                  ↓
            traducción a inglés (Google Translate API)
                  ↓
"tomato, onion" → API IA → receta en inglés
                  ↓
            traducción a español (Google Translate API)
                  ↓
Usuario recibe → receta en español
```

### Flujo de Idioma Global:
```
Usuario en index.tsx → selecciona idioma
                    ↓
        guardado en AsyncStorage
                    ↓
Componentes leen idioma → se sincroniza automáticamente
```

## API de Traducción Utilizada

**URL:** `https://translate.googleapis.com/translate_a/single`

**Ventajas:**
- ✅ **Sin límites** - Traducción infinita
- ✅ Gratuita
- ✅ Sin API key
- ✅ Alta calidad (Google Translate)
- ✅ Rápida y confiable
- ✅ Funciona sin configuración

**Características:**
- Soporta múltiples idiomas
- Traducción paralela (Promise.all)
- Manejo de errores (retorna texto original si falla)

## Persistencia de Datos

El idioma seleccionado se guarda en **AsyncStorage** con la key `appLanguage`:
- Se carga automáticamente al abrir la app
- Se sincroniza en todos los componentes
- Se persiste entre sesiones

## Testing

### Para probar la traducción:

1. **Pantalla Principal:**
   - Abre la app
   - Selecciona "Español" o "English"
   - Cierra la app completamente
   - Abre nuevamente → debe mantener el idioma seleccionado

2. **Componente de IA:**
   - Selecciona "Español" en pantalla principal
   - Abre "Probar recomendador IA"
   - Debe mostrar el idioma español automáticamente
   - Escribe: "tomate, cebolla, ajo"
   - Verifica que se traduzca a inglés internamente
   - Verifica que la receta se traduzca a español

3. **Componente de Recetas:**
   - Selecciona "Español" en pantalla principal
   - Abre "Recetas"
   - Todas las recetas deben estar en español
   - Cambiar a "English" → recetas originales instantáneamente

## Mejoras Futuras Opcionales

### Opción 1: Traducción en Backend (RECOMENDADO para producción)
Implementar endpoints en el backend que:
- Cacheen traducciones de recetas
- Usen la API de Google Translate en backend (mejor control)
- Reduzcan latencia en frontend

### Opción 2: Más Idiomas
Agregar soporte para otros idiomas:
- Francés (fr), Alemán (de), Italiano (it), etc.
- Solo cambiar los códigos de idioma

### Opción 3: Offline Translation
Para funcionalidad offline, considerar:
- Usar `react-native-ml-kit` o similar
- Descargar modelos locales de traducción
- Funciona sin conexión a internet

## Dependencias Utilizadas

No se requieren dependencias adicionales. La solución usa:
- `react-native` (ya instalado)
- `@react-native-async-storage/async-storage` (ya instalado)
- `fetch` nativo del navegador/RN

## Notas Técnicas

- El servicio de traducción retorna el texto original si hay un error, así que la app nunca "rompe"
- Las traducciones se hacen en paralelo con `Promise.all()` para máxima velocidad
- El idioma está centralizado en AsyncStorage para fácil acceso desde cualquier componente
- Los selectores de idioma en cada pantalla sincronizados con la selección global

