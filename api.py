import os
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from sentence_transformers import SentenceTransformer
import joblib
import pandas as pd
import ast
from typing import List, Set

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

def clean_substrings(ings: List[str]) -> List[str]:
    ings = sorted(set(ings), key=len, reverse=True)
    final = []
    for ing in ings:
        if not any(ing != other and ing in other for other in ings):
            final.append(ing)
    return final

def extract_ingredients_hybrid(text: str, model, tokenizer, unique_ingredients_sorted: List[str]) -> Set[str]:
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
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForTokenClassification.from_pretrained(model_dir)

unique_path = os.path.join(base_dir, "models", "ner", "unique_ingredients.txt")
with open(unique_path, "r") as f:
    unique_ingredients = [line.strip() for line in f]
unique_ingredients_sorted = sorted(unique_ingredients, key=len, reverse=True)

# Load recommender model and data
embedder_dir = os.path.join(base_dir, "models", "embedder")
embedder = SentenceTransformer(embedder_dir)

nn_path = os.path.join(base_dir, "models", "best_nn_model.pkl")
nn = joblib.load(nn_path)

train_df_path = os.path.join(base_dir, "models", "df_recetas_processed.csv")
train_df = pd.read_csv(train_df_path)

app = Flask(__name__)

@app.route('/extract_ingredients', methods=['POST'])
def extract():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    ents = extract_ingredients_hybrid(text, model, tokenizer, unique_ingredients_sorted)
    return jsonify({"ingredients": list(ents)})

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

if __name__ == '__main__':
    app.run(debug=True)