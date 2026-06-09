# 🍳 Cómo Entrenar tu Modelo de Recetas Personalizado

## Problema que encontramos

El archivo `Backend/models/embedder/model.safetensors` era un **puntero de Git LFS** (133 bytes) en lugar del modelo real (90MB).

Esto ocurrió porque:
- Git LFS estaba configurado en `.gitattributes` para manejar archivos `.safetensors`
- El repositorio se clonó sin Git LFS configurado correctamente
- Solo se guardó el puntero, no el archivo real

## Solución aplicada

✅ Desactivé Git LFS para archivos `.safetensors` en `.gitattributes`
✅ Ahora tus modelos se guardan directamente sin punteros de LFS
✅ Mejoré el script de entrenamiento con verificaciones

## Cómo entrenar tu modelo

### Opción 1: Usando Python directamente (Recomendado)

```bash
# Desde la raíz del proyecto
python ENTRENAR_MODELO.py
```

Esto:
1. Cargará tus datos de recetas (`Backend/datasets/RAW_recipes.csv`)
2. Entrenará el modelo de recomendación personalizado
3. Generará un `model.safetensors` válido (no puntero de LFS)
4. Guardará todo en `Backend/models/embedder/`

### Opción 2: Usando el script original

```bash
cd python
python train_recommender.py
```

## Después de entrenar

```bash
# Reconstruir y levantar el contenedor
docker compose build
docker compose up
```

El contenedor ahora usará **tu modelo personalizado** en lugar del genérico.

## Verificación

Puedes verificar que el modelo es correcto:

```bash
# Verifica que no sea un puntero de LFS
ls -lh Backend/models/embedder/model.safetensors

# Debería mostrar un tamaño > 90MB, no 133 bytes
```

## Si algo falla

- **"El archivo es muy pequeño"**: Git LFS está activo. Ejecuta:
  ```bash
  git lfs uninstall
  ```
  Luego reinicia el entrenamiento.

- **"No se encuentra RAW_recipes.csv"**: Asegúrate de tener:
  ```
  Backend/datasets/RAW_recipes.csv
  ```

## Diferencia: Tu modelo vs. Modelo genérico

| Característica | Tu modelo personalizado | all-MiniLM-L6-v2 |
|---|---|---|
| **Entrenado con** | Tus recetas específicas | Datos generales en inglés |
| **Optimizado para** | Recomendación de recetas | Similitud semántica general |
| **Mejor para** | Tu base de datos | Propósito general |

Tu modelo personalizado será **mucho mejor** para tus recetas. 🎯
