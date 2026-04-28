import os
import re
import sys
import json
import torch
from transformers import AutoTokenizer, BertForTokenClassification

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from python.recipe_similarity_ai import RecipeSimilarityAI, ingredients_from_ner_output

# -------- PATHS --------
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(BASE_DIR, "../models/ner")

# -------- LOAD MODEL --------
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=True)
model     = BertForTokenClassification.from_pretrained(MODEL_DIR)

def resolve_device():
    force_cuda = os.getenv("FORCE_CUDA", "0") == "1"
    if torch.cuda.is_available():
        return torch.device("cuda")
    if force_cuda:
        raise RuntimeError(
            "FORCE_CUDA=1 pero CUDA no esta disponible. "
            f"Python={sys.executable} | torch={torch.__version__} | cuda={torch.version.cuda}"
        )
    return torch.device("cpu")


device = resolve_device()
model.to(device)
model.eval()

recipe_ai = RecipeSimilarityAI()

print("Python:", sys.executable)
print("Torch:", torch.__version__, "| CUDA toolkit:", torch.version.cuda)
print("🔥 MODELO CARGADO EN:", device)

id2label = {int(k): v for k, v in model.config.id2label.items()}


# -------- TOKENIZER (matches training) --------
def clean_tokenize(text):
    """Strip punctuation and lowercase — identical to training pipeline."""
    return re.sub(r"[^a-zA-Z\s]", "", text.lower()).split()


# -------- PREDICT --------
def predict(text, debug=False):
    words = clean_tokenize(text)   # ← THE FIX: was text.lower().split()
    if not words:
        return [], []

    inputs   = tokenizer(
        words,
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128,
    )
    word_ids = inputs.word_ids(batch_index=0)
    inputs   = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits  = model(**inputs).logits[0]
        probs   = torch.softmax(logits, dim=-1)
        pred_ids = torch.argmax(probs, dim=-1)

    # One prediction per word (first sub-token only)
    word_preds  = []
    word_scores = []
    prev_word_id = None

    for token_idx, word_id in enumerate(word_ids):
        if word_id is None or word_id == prev_word_id:
            continue
        label_id   = int(pred_ids[token_idx].item())
        label_name = id2label.get(label_id, "O")
        score      = float(probs[token_idx, label_id].item())
        word_preds.append((word_id, label_name))
        word_scores.append((word_id, score))
        prev_word_id = word_id

    if debug:
        print("\n📊 TOKENS Y ETIQUETAS:")
        for (word_id, label), (_, score) in zip(word_preds, word_scores):
            print(f"  {words[word_id]:<15} -> {label} ({score:.3f})")

    # -------- SPAN EXTRACTION --------
    ingredients   = []
    current_toks  = []
    current_scores = []

    for (word_id, label), (_, score) in zip(word_preds, word_scores):
        token = words[word_id]

        if label == "B-FOOD":
            if current_toks:
                ingredients.append((" ".join(current_toks),
                                    round(sum(current_scores) / len(current_scores), 3)))
            current_toks   = [token]
            current_scores = [score]

        elif label == "I-FOOD" and current_toks:
            current_toks.append(token)
            current_scores.append(score)

        else:  # O — close any open span
            if current_toks:
                ingredients.append((" ".join(current_toks),
                                    round(sum(current_scores) / len(current_scores), 3)))
                current_toks   = []
                current_scores = []

    if current_toks:
        ingredients.append((" ".join(current_toks),
                            round(sum(current_scores) / len(current_scores), 3)))

    # Deduplicate
    seen, unique = set(), []
    for ing, conf in ingredients:
        if ing not in seen:
            seen.add(ing)
            unique.append((ing, conf))

    return unique, []


# -------- INTERACTIVE --------
if __name__ == "__main__":
    print("\n🚀 SISTEMA DE PRUEBA DE RECETAS")
    print("Escribe una frase (o 'exit')\n")

    while True:
        text = input("👉 ")
        if text.lower() == "exit":
            break

        ings, tags = predict(text, debug=True)

        print("\n🥗 INGREDIENTES DETECTADOS:")
        for i in ings:
            print("  -", i)
        if not ings:
            print("  (ninguno)")
        else:
            detected_ingredients = ingredients_from_ner_output(ings)
            best_recipe = recipe_ai.recommend_best_recipe(detected_ingredients)

            print("\n🍽️ MEJOR RECETA ENCONTRADA:")
            print("  Título:", best_recipe["Title"])
            print(f"  Similitud: {best_recipe['similarity_percent']:.2f}%")
            print("  Ingredientes detectados:", ", ".join(best_recipe["Ingredients"]))
            print("  Tags:", ", ".join(best_recipe["Tags"]))
            print("  Indicadores dietéticos:")
            recipe_meta = best_recipe["recipe"]
            print(f"    - Contiene lactosa: {recipe_meta.get('contains_lactose')}")
            print(f"    - Contiene gluten: {recipe_meta.get('contains_gluten')}")
            print(f"    - Bajo en calorías: {recipe_meta.get('low_calories')}")
            print(f"    - Bajo en grasa: {recipe_meta.get('low_fat')}")
            print(f"    - Vegetariano: {recipe_meta.get('is_vegetarian')}")
            print("\n  Pasos para elaborar la receta:")
            for step_i, step in enumerate(recipe_meta.get('Steps', []), start=1):
                print(f"    {step_i}. {step}")
            print("\n  Receta completa (resumen):")
            print(json.dumps({
                "Title": recipe_meta.get("Title"),
                "IngredientsList": recipe_meta.get("IngredientsList"),
                "Tags": recipe_meta.get("Tags"),
                "Calories": recipe_meta.get("Calories"),
                "Instructions": recipe_meta.get("Instructions"),
            }, ensure_ascii=False, indent=2))

        print("\n" + "-" * 50 + "\n")