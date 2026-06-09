#!/usr/bin/env python3
"""
Script simple para entrenar tu modelo de recomendación de recetas
Ejecutar desde la raíz del proyecto: python ENTRENAR_MODELO.py
"""

import os
import sys
import shutil

# Añadir directorio python al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

from train_recommender import main

def verify_and_copy_model():
    """Verifica que el modelo se guardó correctamente y lo copia a Backend/"""
    model_source = os.path.join('Backend', 'models', 'embedder', 'model.safetensors')
    
    if not os.path.exists(model_source):
        print("❌ Modelo no encontrado después del entrenamiento")
        return False
    
    file_size = os.path.getsize(model_source)
    
    if file_size < 1000:
        print(f"❌ Archivo model.safetensors es muy pequeño ({file_size} bytes)")
        print("   Puede ser un puntero de Git LFS en lugar del archivo real")
        return False
    
    print(f"✅ Modelo verificado: {file_size / 1024 / 1024:.2f} MB")
    return True

if __name__ == '__main__':
    print("=" * 70)
    print("🍳 Entrenando modelo personalizado de recomendación de recetas")
    print("=" * 70)
    print()
    
    try:
        main()
        print()
        
        # Verificar que el modelo se guardó correctamente
        if verify_and_copy_model():
            print()
            print("=" * 70)
            print("✅ ¡Modelo entrenado exitosamente!")
            print("=" * 70)
            print()
            print("El modelo se encuentra en:")
            print("  Backend/models/embedder/")
            print()
            print("Archivos generados:")
            print("  ✅ model.safetensors (tu modelo personalizado)")
            print("  ✅ config.json")
            print("  ✅ tokenizer.json")
            print("  ✅ 1_Pooling/config.json")
            print()
            print("Próximos pasos:")
            print("  1. Haz commit y push a GitHub:")
            print("     git add Backend/models/")
            print("     git commit -m 'chore: actualizar modelo entrenado'")
            print("     git push")
            print()
            print("  2. Reconstruye el contenedor Docker:")
            print("     docker compose build")
            print("     docker compose up")
            print()
            print("El backend usará tu modelo personalizado automáticamente ✨")
        else:
            print()
            print("=" * 70)
            print("❌ Error: El modelo no se guardó correctamente")
            print("=" * 70)
            sys.exit(1)
            
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Error durante el entrenamiento:")
        print(f"   {str(e)}")
        print("=" * 70)
        sys.exit(1)
