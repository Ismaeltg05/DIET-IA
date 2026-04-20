### Para archivos grandes poner
```
git add RutaArchivoGrande
```

## Entorno, dependencias e instrucciones (Python puro)
1. Asegúrate de estar en la raíz del proyecto:

```bash
cd C:\\Users\\Salmeron\\Desktop\\Diet-AI\\DIET-IA
```

2. Crear/activar entorno virtual (recomendado):

```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
# o
source .venv/bin/activate  # Linux/Mac
```

3. Instalar paquetes necesarios:

```bash
pip install --upgrade pip
pip install pandas numpy scikit-learn matplotlib sentence-transformers joblib transformers torch datasets accelerate flask
pip install seqeval
```

4. Archivos de entrenamiento generados:

`python/train_recommender.py` y `python/ner_Salmeron.py`

1. Ejecutar entrenamiento KNN semántico:

```bash
python ./python/rain_recommender.py
```

6. Ejecutar entrenamiento NER de ingredientes:

```bash
python ./python/ner_Salmeron.py
```

6. Artefactos generados (carpeta `models/`):
- `df_recetas_processed.csv`
- `best_nn_model.pkl`
- `best_nn_metadata.pkl`
- carpeta `embedder/` con transformer guardado
- `history_YYYYMMDD_HHMMSS.csv`
- `history_plot_YYYYMMDD_HHMMSS.png`
- carpeta `ner/` con `best_ner_model/`, `unique_ingredients.txt`, y `training_loss_YYYYMMDD_HHMMSS.png` (si se genera)

## API REST

Después de entrenar los modelos, puedes levantar una API para usarlos.

1. Ejecutar la API: `python ./python api.py`

2. La API estará disponible en `http://localhost:5000`

### Endpoints

- **POST /extract_ingredients**: Extrae ingredientes de un texto.
  - Input: `{"text": "Texto con ingredientes"}`
  - Output: `{"ingredients": ["ingrediente1", "ingrediente2"]}`

- **POST /recommend_recipes**: Recomienda recetas basadas en ingredientes.
  - Input: `{"ingredients": ["ingrediente1", "ingrediente2"]}`
  - Output: `{"recommendations": [{"Title": "Receta1", "Instructions": "Pasos..."}, ...]}`

### Ejemplo de uso con curl

```bash
# Extracción de ingredientes
curl -X POST http://localhost:5000/extract_ingredients -H "Content-Type: application/json" -d '{"text": "I have tomatoes, potatoes, olive oil and peppers at home."}'

# Recomendación de recetas
curl -X POST http://localhost:5000/recommend_recipes -H "Content-Type: application/json" -d '{"ingredients": ["tomatoes", "olive oil"]}'
```

## Importaciones que usa el script
```python
import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split
```

## Notas
- El `.csv` se carga desde `datasets/recetas.csv`. Si usas otro fichero, cambia `dataset_path` en el script.
- El modelo es KNN sobre embeddings, no es un modelo entrenado tipo red neuronal (por eso se guarda con `joblib`).
- Ajusta `n_neighbors` en el listado `[3,5,7,10,15]` si quieres otro rango de búsqueda.
