import os
import ast
import random
from typing import List, Set

import pandas as pd
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, pipeline
from datasets import Dataset
import torch
import matplotlib.pyplot as plt
from datetime import datetime


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


def convert_to_bio(text, entities, label="FOOD"):
    words = text.split()  # simple split
    ner_tags = ["O"] * len(words)
    char_pos = 0
    for word_idx, word in enumerate(words):
        start_char = text.find(word, char_pos)
        end_char = start_char + len(word)
        for ent_start, ent_end, ent_label in entities:
            if ent_start <= start_char < ent_end:
                ner_tags[word_idx] = f"B-{label}"
                # mark following words as I if they overlap
                current_end = end_char
                for j in range(word_idx + 1, len(words)):
                    next_start = text.find(words[j], current_end)
                    if next_start < ent_end:
                        ner_tags[j] = f"I-{label}"
                        current_end = next_start + len(words[j])
                    else:
                        break
                break
        char_pos = end_char
    return words, ner_tags


def build_train_data(df: pd.DataFrame, sample_size=8000):
    df = df.dropna(subset=["Ingredients", "Instructions"]).reset_index(drop=True)
    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42)

    train_data = []
    for _, row in sample_df.iterrows():
        ingredients = [str(i).strip().lower() for i in to_list(row["Ingredients"]) if str(i).strip()]
        if not ingredients:
            continue

        text = steps_to_text(row["Instructions"])
        text_low = text.lower()
        entities = []

        for ingr in ingredients:
            start = text_low.find(ingr)
            if start != -1:
                end = start + len(ingr)
                entities.append((start, end, "FOOD"))

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
    model_name = "chambliss/distilbert-for-food-extraction"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)

    label2id = model.config.label2id
    id2label = model.config.id2label

    # convert train_data
    converted_data = []
    for text, annotations in train_data:
        entities = annotations["entities"]
        words, ner_tags = convert_to_bio(text, entities, "FOOD")
        ner_tag_ids = [label2id.get(tag, 0) for tag in ner_tags]  # default to O if not found
        converted_data.append({"tokens": words, "ner_tags": ner_tag_ids})

    dataset = Dataset.from_list(converted_data)

    # tokenize
    def tokenize_and_align_labels(examples):
        tokenized_inputs = tokenizer(examples["tokens"], truncation=True, is_split_into_words=True, max_length=512, padding=True)
        labels = []
        for i, label in enumerate(examples["ner_tags"]):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            previous_word_idx = None
            label_ids = []
            for word_idx in word_ids:
                if word_idx is None:
                    label_ids.append(-100)
                elif word_idx != previous_word_idx:
                    label_ids.append(label[word_idx])
                else:
                    label_ids.append(label[word_idx])
            # Pad labels to match the padded input length
            label_ids += [-100] * (len(tokenized_inputs["input_ids"][i]) - len(label_ids))
            labels.append(label_ids)
        tokenized_inputs["labels"] = labels
        return tokenized_inputs

    tokenized_dataset = dataset.map(tokenize_and_align_labels, batched=True)

    # training args
    training_args = TrainingArguments(
        output_dir="./results",
        eval_strategy="no",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=n_iter,
        weight_decay=0.01,
        save_strategy="no",
        logging_dir="./logs",
        logging_steps=10,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    trainer.train()

    # Plot training loss
    log_history = trainer.state.log_history
    losses = [log['loss'] for log in log_history if 'loss' in log]
    steps = [log['step'] for log in log_history if 'loss' in log]

    if losses:
        plt.figure()
        plt.plot(steps, losses)
        plt.xlabel('Step')
        plt.ylabel('Loss')
        plt.title('Training Loss')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(model_dir, f'training_loss_{timestamp}.png')
        plt.savefig(plot_path)
        print(f"Gráfica de pérdida guardada en: {plot_path}")

    return model, tokenizer


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


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_dir = os.path.join(base_dir, "datasets")
    dataset_path = os.path.join(dataset_dir, "df_recetas_processed.csv")
    model_dir = os.path.join(base_dir, "models", "ner")
    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset no encontrado: {dataset_path}")

    df = pd.read_csv(dataset_path)
    print(f"Dataset cargado: {len(df)} filas")

    all_ingredients = []
    for ing in df["Ingredients"].dropna():
        item_list = to_list(ing)
        all_ingredients.extend(str(i).strip().lower() for i in item_list if str(i).strip())

    unique_ingredients = sorted(set(all_ingredients))
    print(f"Ingredientes únicos: {len(unique_ingredients)}")

    train_data = build_train_data(df)
    print(f"Entradas de entrenamiento generadas: {len(train_data)}")

    model, tokenizer = train_ner_model(train_data, n_iter=8)

    model.save_pretrained(os.path.join(model_dir, "best_ner_model"))
    tokenizer.save_pretrained(os.path.join(model_dir, "best_ner_model"))
    print(f"Modelo NER guardado en: {os.path.join(model_dir, 'best_ner_model')}")

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
        print(extract_ingredients_hybrid(line, model, tokenizer, unique_ingredients_sorted))


if __name__ == "__main__":
    main()
