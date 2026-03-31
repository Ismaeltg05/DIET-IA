import os
import ast
import random
from typing import List, Set

import pandas as pd
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding


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


def steps_to_text(steps_val):
    if isinstance(steps_val, list):
        return " ".join(str(s) for s in steps_val)
    if isinstance(steps_val, str):
        try:
            v = ast.literal_eval(steps_val)
            if isinstance(v, list):
                return " ".join(str(s) for s in v)
        except Exception:
            return steps_val
    return str(steps_val)


def clean_substrings(ings: List[str]) -> List[str]:
    ings = sorted(set(ings), key=len, reverse=True)
    final = []
    for ing in ings:
        if not any(ing != other and ing in other for other in ings):
            final.append(ing)
    return final


def build_train_data(df: pd.DataFrame, sample_size=8000):
    df = df.dropna(subset=["ingredients", "steps"]).reset_index(drop=True)
    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42)

    train_data = []
    for _, row in sample_df.iterrows():
        ingredients = [str(i).strip().lower() for i in to_list(row["ingredients"]) if str(i).strip()]
        if not ingredients:
            continue

        text = steps_to_text(row["steps"])
        text_low = text.lower()
        entities = []

        for ingr in ingredients:
            start = text_low.find(ingr)
            if start != -1:
                end = start + len(ingr)
                entities.append((start, end, "INGREDIENT"))

        if not entities:
            continue

        entities = sorted(entities, key=lambda x: (x[0], -(x[1] - x[0])))
        clean = []
        last_end = -1
        for start, end, label in entities:
            if start >= last_end:
                clean.append((start, end, label))
                last_end = end

        if not clean:
            continue

        train_data.append((text, {"entities": clean}))

    return train_data


def train_ner_model(train_data, n_iter=8):
    nlp = spacy.load("en_core_web_sm")
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    ner.add_label("INGREDIENT")

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                examples = []
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    examples.append(Example.from_dict(doc, annotations))
                nlp.update(examples, sgd=optimizer, losses=losses)
            print(f"Iteración {itn + 1}/{n_iter} Losses: {losses}")

    return nlp


def extract_ingredients_hybrid(text: str, nlp_model, unique_ingredients_sorted: List[str]) -> Set[str]:
    text_low = text.lower()
    doc = nlp_model(text_low)
    ents = {ent.text for ent in doc.ents if ent.label_ == "INGREDIENT"}

    # heurística extra: coincidencia de ingredientes conocidos
    for ingr in unique_ingredients_sorted:
        if ingr in text_low and ingr not in ents:
            ents.add(ingr)

    return set(clean_substrings(list(ents)))


def main():
    dataset_path = os.path.join("..", "datasets", "RAW_recipes.csv")
    model_dir = os.path.join("..", "models", "ner_ingredients")
    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset no encontrado: {dataset_path}")

    df = pd.read_csv(dataset_path)
    print(f"Dataset cargado: {len(df)} filas")

    all_ingredients = []
    for ing in df["ingredients"].dropna():
        item_list = to_list(ing)
        all_ingredients.extend(str(i).strip().lower() for i in item_list if str(i).strip())

    unique_ingredients = sorted(set(all_ingredients))
    print(f"Ingredientes únicos: {len(unique_ingredients)}")

    train_data = build_train_data(df)
    print(f"Entradas de entrenamiento generadas: {len(train_data)}")

    nlp_model = train_ner_model(train_data, n_iter=8)

    nlp_model.to_disk(model_dir)
    print(f"Modelo NER guardado en: {model_dir}")

    unique_path = os.path.join(model_dir, "unique_ingredients.txt")
    with open(unique_path, "w", encoding="utf-8") as f:
        for ingr in unique_ingredients:
            f.write(ingr + "\n")
    print(f"Ingredientes únicos guardados en: {unique_path}")

    default_test_lines = [
        "I have tomatoes, potatoes, olive oil and peppers at home.",
        "cook the chicken with garlic, onion and rice in a large pot.",
        "For breakfast I ate oats with milk, banana and a spoon of peanut butter.",
    ]

    unique_ingredients_sorted = sorted(unique_ingredients, key=len, reverse=True)
    for line in default_test_lines:
        print(line)
        print(extract_ingredients_hybrid(line, nlp_model, unique_ingredients_sorted))


if __name__ == "__main__":
    main()
