import os
import json
import torch
from transformers import AutoTokenizer, BertForTokenClassification

# -------- PATHS --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../models/ner")
DATASET_DIR = os.path.join(BASE_DIR, "../datasets")

# -------- LOAD MODEL --------
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=True)
model = BertForTokenClassification.from_pretrained(MODEL_DIR)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

print("🔥 MODELO CARGADO EN:", device)

# -------- LOAD LABEL MAP --------
id2label = {int(k): v for k, v in model.config.id2label.items()}


# -------- PREDICT FUNCTION --------
def predict(text, debug=False):
    words = text.lower().split()
    if not words:
        return [], []

    inputs = tokenizer(
        words,
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128
    )

    word_ids = inputs.word_ids(batch_index=0)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits[0]
        probs = torch.softmax(logits, dim=-1)
        pred_ids = torch.argmax(probs, dim=-1)

    # Keep one prediction per original word (first subtoken).
    word_preds = []
    word_scores = []
    prev_word_id = None

    for token_idx, word_id in enumerate(word_ids):
        if word_id is None or word_id == prev_word_id:
            continue

        label_id = int(pred_ids[token_idx].item())
        label_name = id2label.get(label_id, "O")
        score = float(probs[token_idx, label_id].item())
        word_preds.append((word_id, label_name))
        word_scores.append((word_id, score))
        prev_word_id = word_id

    if debug:
        print("\n📊 TOKENS Y ETIQUETAS:")
        for (word_id, label_name), (_, score) in zip(word_preds, word_scores):
            print(f"{words[word_id]} -> {label_name} ({score:.3f})")

    ingredients = []
    current_tokens = []
    current_scores = []

    for (word_id, label_name), (_, score) in zip(word_preds, word_scores):
        token = words[word_id]

        if label_name == "B-FOOD":
            if current_tokens:
                ingredients.append((" ".join(current_tokens), round(sum(current_scores) / len(current_scores), 3)))
            current_tokens = [token]
            current_scores = [score]
        elif label_name == "I-FOOD" and current_tokens:
            current_tokens.append(token)
            current_scores.append(score)
        else:
            if current_tokens:
                ingredients.append((" ".join(current_tokens), round(sum(current_scores) / len(current_scores), 3)))
                current_tokens = []
                current_scores = []

    if current_tokens:
        ingredients.append((" ".join(current_tokens), round(sum(current_scores) / len(current_scores), 3)))

    # Remove duplicates preserving order.
    seen = set()
    unique_ingredients = []
    for ing, conf in ingredients:
        if ing not in seen:
            seen.add(ing)
            unique_ingredients.append((ing, conf))

    return unique_ingredients, []


# -------- INTERACTIVE MODE --------
if __name__ == "__main__":

    print("\n🚀 SISTEMA DE PRUEBA DE RECETAS")
    print("Escribe una frase (o 'exit')\n")

    while True:
        text = input("👉 ")

        if text.lower() == "exit":
            break

        ing, tags = predict(text, debug=True)

        print("\n🥗 INGREDIENTES DETECTADOS:")
        if ing:
            for i in ing:
                print(" -", i)
        else:
            print(" (ninguno)")

        print("\n🏷️ TAGS DETECTADOS:")
        if tags:
            for t in tags:
                print(" -", t)
        else:
            print(" (ninguno)")

        print("\n" + "-" * 50 + "\n")