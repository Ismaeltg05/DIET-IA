import os
import re
import sys
import json
import torch
from transformers import AutoTokenizer, BertForTokenClassification

# --- Configuración de rutas ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from python.recipe_similarity_ai import RecipeSimilarityAI
except ImportError:
    print("Error: No se pudo importar 'recipe_similarity_ai'.")
    sys.exit(1)

# --- Rutas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../models/ner")
INGREDIENTS_JSON = os.path.join(BASE_DIR, "../datasets/ALL_INGREDIENTS.json")

# --- Carga de Diccionario (CORREGIDO) ---
ALL_FOODS = set()
try:
    # EL FIX: Separamos el modo 'r' del encoding 'utf-8-sig'
    if os.path.exists(INGREDIENTS_JSON):
        with open(INGREDIENTS_JSON, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            ALL_FOODS = {str(ing).lower().strip() for ing in data}
        print(f"✅ Diccionario cargado con {len(ALL_FOODS)} ingredientes.")
    else:
        print(f"❌ No se encuentra el archivo en: {INGREDIENTS_JSON}")
except Exception as e:
    print(f"❌ Error al cargar diccionario: {e}")

# --- Carga de IA ---
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = BertForTokenClassification.from_pretrained(MODEL_DIR)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

recipe_ai = RecipeSimilarityAI()
id2label = {int(k): v for k, v in model.config.id2label.items()}

def predict(text, debug=False):
    # 1. PASADA NER (IA)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        logits = model(**inputs).logits[0]
        pred_ids = torch.argmax(torch.softmax(logits, dim=-1), dim=-1)

    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    ner_ingredients = set()
    current_ing = ""

    for idx, (token, pred_id) in enumerate(zip(tokens, pred_ids)):
        if token in ["[CLS]", "[SEP]", "[PAD]"]: continue
        label = id2label.get(pred_id.item(), "O")
        clean_token = token.replace("##", "")

        if label == "B-FOOD":
            if current_ing: ner_ingredients.add(current_ing.strip().lower())
            current_ing = clean_token
        elif label == "I-FOOD" and current_ing:
            current_ing += clean_token if token.startswith("##") else " " + clean_token
        else:
            if current_ing:
                ner_ingredients.add(current_ing.strip().lower())
                current_ing = ""
    if current_ing: ner_ingredients.add(current_ing.strip().lower())

    # 2. PASADA POR DICCIONARIO (Failsafe mejorado)
    # Limpiamos el texto para que "cheese," sea "cheese"
    words_in_input = re.findall(r'\b\w+\b', text.lower())
    keyword_ingredients = {w for w in words_in_input if w in ALL_FOODS and len(w) > 2}
    
    final_list = list(ner_ingredients.union(keyword_ingredients))
    
    if debug:
        print(f"\n🔍 [DEBUG] NER detectó: {list(ner_ingredients)}")
        print(f"🔍 [DEBUG] Failsafe detectó: {list(keyword_ingredients)}")

    return [(ing, 1.0) for ing in final_list]

# --- Bucle ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 DIET-IA ACTIVADO (MODO HÍBRIDO)")
    print("="*50)

    while True:
        prompt = input("\n👉 ")
        if prompt.lower() in ["exit", "salir"]: break
        
        detected_ings = predict(prompt, debug=True)
        ing_names = [i[0] for i in detected_ings]

        print("\n🥗 INGREDIENTES DETECTADOS:")
        if not ing_names:
            print("  (Ninguno)")
            continue
        
        for name in ing_names:
            print(f"  • {name}")

        best_recipe = recipe_ai.recommend_best_recipe(ing_names)

        if best_recipe:
            print(f"\n🍽️ MEJOR RECETA: {best_recipe.get('Title')}")
            meta = best_recipe.get("recipe", {})
            print(f"  🛡️ Sin Lactosa: {'No ❌' if meta.get('contains_lactose') else 'Sí ✅'}")
            print("\n  👨‍🍳 PASOS:")
            for i, step in enumerate(meta.get('Steps', []), 1):
                print(f"    {i}. {step}")
        
        print("\n" + "-"*50)