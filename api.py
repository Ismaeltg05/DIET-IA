"""
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
"""

import os
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from sentence_transformers import SentenceTransformer
import joblib
import pandas as pd
import ast
from typing import List, Set

"""
API de servicio para extracción de ingredientes y recomendación de recetas.

Este módulo expone endpoints HTTP (Flask) para:
- Extraer ingredientes de un texto usando un modelo NER y heurísticas.
- Recomendar recetas usando un embedder + modelo KNN previamente entrenado.

Notas importantes:
- El script asume que existen artefactos en `models/` y `datasets/`.
- No realiza entrenamiento; solo carga modelos ya entrenados.
"""

def to_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            v = ast.literal_eval(x)
            return v if isinstance(v, list) else [x]
        except Exception:
            return [x]
    return []


# Helper: eliminar ingredientes que son substrings de otros más largos.
def clean_substrings(ings: List[str]) -> List[str]:
    """
    Dado un iterable de ingredientes, preserva solo aquellos que no son
    substrings de otros (ej: 'oil' no debería aparecer si existe 'olive oil').
    Esto ayuda a devolver un set de entidades limpio y no redundante.
    """
    ings = sorted(set(ings), key=len, reverse=True)
    final = []
    for ing in ings:
        if not any(ing != other and ing in other for other in ings):
            final.append(ing)
    return final

def extract_ingredients_hybrid(text: str, model, tokenizer, unique_ingredients_sorted: List[str]) -> Set[str]:
    """
    Extrae ingredientes usando una combinación (hybrid) de:
    1) pipeline NER (modelo de tokens) que identifica entidades etiquetadas como FOOD
    2) búsqueda heurística de coincidencias de ingredientes conocidos dentro del texto

    El pipeline de transformers se ejecuta sobre `text.lower()` y se filtra por
    agrupación `entity_group == 'FOOD'`. Después agregamos coincidencias exactas
    de ingredientes reconocidos (`unique_ingredients_sorted`) para cubrir casos
    en que el modelo no detectó expresiones compuestas.

    Finalmente limpiamos substrings redundantes con `clean_substrings`.
    """
    ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    results = ner_pipeline(text.lower())
    ents = {ent["word"] for ent in results if ent["entity_group"] == "FOOD"}

    # heurística extra: coincidencia de ingredientes conocidos
    text_low = text.lower()
    for ingr in unique_ingredients_sorted:
        if ingr in text_low and ingr not in ents:
            ents.add(ingr)

    return set(clean_substrings(list(ents)))

# Load NER model and data
base_dir = os.path.abspath(os.path.dirname(__file__))
model_dir = os.path.join(base_dir, "models", "ner", "best_ner_model")
# Cargamos tokenizer y modelo de clasificación de tokens (NER). Deben existir
# en `models/ner/best_ner_model`. Si faltan, `from_pretrained` lanzará una excepción.
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForTokenClassification.from_pretrained(model_dir)

unique_path = os.path.join(base_dir, "models", "ner", "unique_ingredients.txt")
# Lista auxiliar de ingredientes únicos para matching heurístico
with open(unique_path, "r") as f:
    unique_ingredients = [line.strip() for line in f]
unique_ingredients_sorted = sorted(unique_ingredients, key=len, reverse=True)

# Load recommender model and data
embedder_dir = os.path.join(base_dir, "models", "embedder")
# Cargar modelo de embeddings (SentenceTransformer). Se puede usar un
# embedder local exportado en `models/embedder` o caer en un modelo remoto.
embedder = SentenceTransformer(embedder_dir)

nn_path = os.path.join(base_dir, "models", "best_nn_model.pkl")
# NearestNeighbors guardado con joblib (KNN para recomendación)
nn = joblib.load(nn_path)

raw_recipes_path = os.path.join(base_dir, "datasets", "RAW_recipes.csv")
if not os.path.exists(raw_recipes_path):
    raise FileNotFoundError(f"No se encontró RAW_recipes.csv en {os.path.join(base_dir, 'datasets')}")

# Cargar CSV de recetas y normalizar nombres de columnas a lo que el código
# espera downstream. `extract_recipe_tags` y `tag_lookup` deben existir en el
# módulo o entorno (aquí se asume su disponibilidad externa).
train_df = pd.read_csv(raw_recipes_path)
train_df = train_df.rename(columns={
    'nvmname': 'Title',
    'name': 'Title',
    'ingredients': 'Ingredients',
    'steps': 'Instructions',
    'tags': 'Category',
})
train_df = train_df.dropna(subset=['Title', 'Ingredients', 'Instructions'])
train_df['Title'] = train_df['Title'].astype(str)
train_df['Ingredients'] = train_df['Ingredients'].apply(lambda value: ' '.join(to_list(value)))
train_df['Instructions'] = train_df['Instructions'].apply(lambda value: ' | '.join(to_list(value)))
train_df['Features'] = train_df['Ingredients']
# La línea siguiente asume la existencia de funciones auxiliares para extraer
# tags; si faltan, esto lanzará NameError. Se mantiene por compatibilidad.
train_df['Tags'] = train_df['Category'].apply(lambda value: extract_recipe_tags(value, tag_lookup))

app = Flask(__name__)

@app.route('/extract_ingredients', methods=['POST'])
def extract():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    ents = extract_ingredients_hybrid(text, model, tokenizer, unique_ingredients_sorted)
    return jsonify({"ingredients": list(ents)})


# NOTE:
# - Este endpoint devuelve una lista (sin clasificación ni normalización
#   adicional). Dependiendo del consumo se podría querer normalizar la salida
#   (minúsculas, join multi-palabra, orden, etc.).

@app.route('/recommend_recipes', methods=['POST'])
def recommend():
    data = request.get_json()
    ingredients = data.get('ingredients', [])
    if not ingredients:
        return jsonify({"error": "No ingredients provided"}), 400

    # Join ingredients to create feature string
    features = " ".join(ingredients)
    query_emb = embedder.encode([features])[0]
    dist, indices = nn.kneighbors([query_emb], n_neighbors=5)
    recommendations = train_df.iloc[indices[0]][['Title', 'Instructions']].to_dict('records')
    return jsonify({"recommendations": recommendations})


# Nota: response contiene `Title` y `Instructions`. Para uso en frontend es
# posible enriquecer con `Ingredients`, `Tags` y otras columnas del dataframe.

if __name__ == '__main__':
    app.run(debug=True)