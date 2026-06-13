"""
LFS Validator - Verifica y descarga archivos de Git LFS si es necesario.
Detecta si un archivo es un puntero de LFS (no descargado) y lo descarga.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"
MIN_FILE_SIZE_KB = 100  # Si es menor a 100KB y es del modelo, probablemente es puntero


def is_lfs_pointer(filepath: str) -> bool:
    """
    Detecta si un archivo es un puntero de LFS (no descargado).
    Los punteros de LFS son archivos pequeños de texto con formato específico.
    """
    try:
        if not os.path.exists(filepath):
            return False
        
        file_size = os.path.getsize(filepath)
        
        # Los punteros de LFS son muy pequeños (típicamente < 500 bytes)
        if file_size > 1000:
            return False
        
        # Verificar si comienza con el header de LFS
        with open(filepath, 'rb') as f:
            content = f.read(100)
            return content.startswith(LFS_POINTER_PREFIX)
    except Exception as e:
        print(f"   Error al verificar {filepath}: {e}")
        return False


def check_model_files(base_dir: str = None) -> Tuple[List[str], List[str]]:
    """
    Verifica el estado de los archivos del modelo.
    Retorna: (archivos_ok, archivos_pendientes)
    """
    if base_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    model_dir = os.path.join(base_dir, "models")
    
    # Archivos críticos que deben estar descargados
    critical_files = [
        os.path.join(model_dir, "embedder", "model.safetensors"),
        os.path.join(model_dir, "ner", "model.safetensors"),
        os.path.join(model_dir, "best_nn_model.pkl"),
        os.path.join(model_dir, "best_nn_metadata.pkl"),
    ]
    
    ok_files = []
    pending_files = []
    
    print("🔍 Verificando archivos del modelo...")
    print(f"   Directorio de modelos: {model_dir}")
    print()
    
    for filepath in critical_files:
        if not os.path.exists(filepath):
            print(f"   ⚠️  No encontrado: {filepath}")
            continue
        
        if is_lfs_pointer(filepath):
            print(f"   📥 Puntero LFS (sin descargar): {Path(filepath).name}")
            pending_files.append(filepath)
        else:
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"   ✅ Descargado: {Path(filepath).name} ({size_mb:.2f} MB)")
            ok_files.append(filepath)
    
    return ok_files, pending_files


def pull_lfs_files(filepaths: List[str] = None) -> bool:
    """
    Intenta descargar archivos de LFS usando 'git lfs pull'.
    Si filepaths es None, descarga todos los archivos LFS tracked.
    """
    try:
        # Verificar que Git LFS está instalado
        result = subprocess.run(
            ["git", "lfs", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print("❌ Git LFS no está instalado o no está disponible")
            print("   Instala con: git lfs install")
            return False
        
        print("\n📥 Descargando archivos de Git LFS...")
        
        if filepaths:
            # Descargar archivos específicos
            for filepath in filepaths:
                print(f"   Descargando: {Path(filepath).name}...")
                result = subprocess.run(
                    ["git", "lfs", "pull", "--include", filepath],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    print(f"   ⚠️  Error descargando {filepath}")
                    print(f"      {result.stderr}")
        else:
            # Descargar todos los archivos LFS
            print("   Descargando todos los archivos LFS...")
            result = subprocess.run(
                ["git", "lfs", "pull"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                print(f"❌ Error en git lfs pull: {result.stderr}")
                return False
        
        print("✅ Descarga completada")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout descargando archivos LFS (archivo muy grande)")
        return False
    except FileNotFoundError:
        print("❌ Git no está instalado o no está en el PATH")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def validate_and_fix_models(base_dir: str = None) -> bool:
    """
    Validación completa: verifica archivos y descarga si es necesario.
    Retorna True si todos los archivos están listos.
    """
    ok_files, pending_files = check_model_files(base_dir)
    
    if not pending_files:
        print("\n✅ Todos los archivos del modelo están listos!")
        return True
    
    print(f"\n⚠️  {len(pending_files)} archivo(s) pendiente(s) de descargar")
    
    if pull_lfs_files(pending_files):
        # Verificar nuevamente
        ok_files_2, pending_files_2 = check_model_files(base_dir)
        
        if not pending_files_2:
            print("\n✅ Todos los archivos descargados exitosamente!")
            return True
        else:
            print("\n⚠️  Algunos archivos aún no están descargados")
            print("   Verifica tu conexión a internet o la configuración de LFS")
            return False
    
    return False


if __name__ == "__main__":
    # Ejecutable desde línea de comandos
    base_dir = sys.argv[1] if len(sys.argv) > 1 else None
    success = validate_and_fix_models(base_dir)
    sys.exit(0 if success else 1)
