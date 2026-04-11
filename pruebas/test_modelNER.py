import os
import json
import torch
from transformers import BertTokenizer, BertForSequenceClassification

# -------- PATHS --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../models/ner")
DATASET_DIR = os.path.join(BASE_DIR, "../datasets")

# -------- LOAD MODEL --------
tokenizer = BertTokenizer.from_pretrained(MODEL_DIR)
model = BertForSequenceClassification.from_pretrained(MODEL_DIR)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

print("🔥 MODELO CARGADO EN:", device)

# -------- LOAD LABELS --------
with open(os.path.join(DATASET_DIR, "ALL_INGREDIENTS.json")) as f:
    ALL_INGREDIENTS = [x.lower() for x in json.load(f)]

with open(os.path.join(DATASET_DIR, "ALL_TAGS.json")) as f:
    ALL_TAGS = [x.lower() for x in json.load(f)]

ALL_LABELS = ALL_INGREDIENTS + ALL_TAGS


# -------- PREDICT FUNCTION --------
def predict(text, threshold=0.2, debug=False):
    text = text.lower()

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

        # 🔥 SIGMOID CORRECTO
        probs = torch.sigmoid(logits)[0]

    if debug:
        print("\n📊 PROBABILIDADES COMPLETAS:")
        for label, p in zip(ALL_LABELS, probs.tolist()):
            print(f"{label}: {p:.3f}")

    ingredients = []
    tags = []

    for i, p in enumerate(probs):
        if p.item() > threshold:
            label = ALL_LABELS[i]

            if label in ALL_INGREDIENTS:
                ingredients.append((label, round(p.item(), 3)))
            else:
                tags.append((label, round(p.item(), 3)))

    return ingredients, tags


# -------- INTERACTIVE MODE --------
if __name__ == "__main__":

    print("\n🚀 SISTEMA DE PRUEBA DE RECETAS")
    print("Escribe una frase (o 'exit')\n")

    while True:
        text = input("👉 ")

        if text.lower() == "exit":
            break

        ing, tags = predict(text, threshold=0.2, debug=True)

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