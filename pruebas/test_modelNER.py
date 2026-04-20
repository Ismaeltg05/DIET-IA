import os
import re
import torch
from transformers import AutoTokenizer, BertForTokenClassification

# -------- PATHS --------
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(BASE_DIR, "../models/ner")

# -------- LOAD MODEL --------
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=True)
model     = BertForTokenClassification.from_pretrained(MODEL_DIR)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

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

        print("\n" + "-" * 50 + "\n")