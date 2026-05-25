"""
Genera un mapa de calor por token para el modelo NER de ingredientes.

La visualización usa la probabilidad agregada de las etiquetas FOOD como una
proxy de importancia: cuanto más alta es la intensidad, más contribuye el token
al candidato de ingrediente.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import List, Optional, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import torch
from transformers import AutoTokenizer, BertForTokenClassification


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "Backend", "models", "ner")
DATASET_DIR = os.path.join(BASE_DIR, "..", "Backend", "datasets")


def resolve_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = BertForTokenClassification.from_pretrained(MODEL_DIR)
    device = resolve_device()
    model.to(device)
    model.eval()
    return tokenizer, model, device


def get_food_label_ids(model) -> List[int]:
    food_ids: List[int] = []
    for label_id, label_name in model.config.id2label.items():
        if isinstance(label_name, str) and "FOOD" in label_name.upper():
            food_ids.append(int(label_id))
    return food_ids


def load_labeled_sample(split: str, sample_index: int) -> Tuple[List[str], List[str]]:
    dataset_path = os.path.join(DATASET_DIR, f"{split}.json")
    with open(dataset_path, encoding="utf-8") as handle:
        samples = json.load(handle)

    if sample_index < 0 or sample_index >= len(samples):
        raise IndexError(f"sample_index fuera de rango para {split}.json: {sample_index}")

    sample = samples[sample_index]
    tokens = [str(token) for token in sample["tokens"]]
    labels = [str(label) for label in sample["labels"]]
    if len(tokens) != len(labels):
        raise ValueError("El sample seleccionado tiene tokens y labels con distinta longitud.")
    return tokens, labels


def load_labeled_samples(split: str, start_index: int, sample_count: int) -> List[Tuple[int, List[str], List[str]]]:
    dataset_path = os.path.join(DATASET_DIR, f"{split}.json")
    with open(dataset_path, encoding="utf-8") as handle:
        samples = json.load(handle)

    if sample_count < 1:
        raise ValueError("sample_count debe ser al menos 1")
    if start_index < 0 or start_index >= len(samples):
        raise IndexError(f"sample_index fuera de rango para {split}.json: {start_index}")

    end_index = min(len(samples), start_index + sample_count)
    batch: List[Tuple[int, List[str], List[str]]] = []
    for sample_index in range(start_index, end_index):
        sample = samples[sample_index]
        tokens = [str(token) for token in sample["tokens"]]
        labels = [str(label) for label in sample["labels"]]
        if len(tokens) != len(labels):
            raise ValueError(f"El sample {sample_index} tiene tokens y labels con distinta longitud.")
        batch.append((sample_index, tokens, labels))

    return batch


def build_text_importance(
    text: str,
    tokenizer,
    model,
    device: torch.device,
) -> Tuple[List[str], List[str], List[float]]:
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128,
    )
    inputs = {key: value.to(device) for key, value in inputs.items()}

    food_label_ids = get_food_label_ids(model)
    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits[0], dim=-1)

    token_ids = inputs["input_ids"][0].detach().cpu().tolist()
    tokens = tokenizer.convert_ids_to_tokens(token_ids)
    predicted_ids = torch.argmax(probabilities, dim=-1).detach().cpu().tolist()

    visible_tokens: List[str] = []
    visible_labels: List[str] = []
    visible_scores: List[float] = []

    for token, predicted_id, token_probs in zip(tokens, predicted_ids, probabilities.detach().cpu()):
        if token in {"[CLS]", "[SEP]", "[PAD]"}:
            continue

        score = float(token_probs[food_label_ids].sum().item()) if food_label_ids else float(token_probs.max().item())
        visible_tokens.append(token.replace("##", ""))
        visible_labels.append(model.config.id2label.get(int(predicted_id), "O"))
        visible_scores.append(score)

    return visible_tokens, visible_labels, visible_scores


def build_sample_importance(
    tokens: Sequence[str],
    gold_labels: Sequence[str],
    tokenizer,
    model,
    device: torch.device,
) -> Tuple[List[str], List[str], List[str], List[float]]:
    inputs = tokenizer(
        [token.lower() for token in tokens],
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128,
    )
    inputs = {key: value.to(device) for key, value in inputs.items()}

    food_label_ids = get_food_label_ids(model)
    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits[0], dim=-1)

    token_ids = inputs["input_ids"][0].detach().cpu().tolist()
    word_ids = tokenizer(
        [token.lower() for token in tokens],
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128,
    ).word_ids(batch_index=0)
    decoded_tokens = tokenizer.convert_ids_to_tokens(token_ids)

    visible_tokens: List[str] = []
    visible_pred_labels: List[str] = []
    visible_gold_labels: List[str] = []
    visible_scores: List[float] = []

    previous_word_id: Optional[int] = None
    for token, word_id, token_probs in zip(decoded_tokens, word_ids, probabilities.detach().cpu()):
        if word_id is None or word_id == previous_word_id:
            previous_word_id = word_id
            continue
        if token in {"[CLS]", "[SEP]", "[PAD]"}:
            previous_word_id = word_id
            continue

        predicted_id = int(torch.argmax(token_probs).item())
        score = float(token_probs[food_label_ids].sum().item()) if food_label_ids else float(token_probs.max().item())

        visible_tokens.append(tokens[word_id])
        visible_pred_labels.append(model.config.id2label.get(predicted_id, "O"))
        visible_gold_labels.append(gold_labels[word_id])
        visible_scores.append(score)
        previous_word_id = word_id

    return visible_tokens, visible_pred_labels, visible_gold_labels, visible_scores


def normalize_scores(scores: Sequence[float]) -> List[float]:
    if not scores:
        return []
    min_score = min(scores)
    max_score = max(scores)
    if abs(max_score - min_score) < 1e-12:
        return [0.0 for _ in scores]
    return [(score - min_score) / (max_score - min_score) for score in scores]


def render_heatmap(
    tokens: Sequence[str],
    predicted_labels: Sequence[str],
    gold_labels: Sequence[str],
    scores: Sequence[float],
    output_path: str,
) -> str:
    if not tokens:
        raise ValueError("No se pudieron generar tokens visibles para el heatmap.")

    normalized_scores = normalize_scores(scores)
    width = max(10.0, len(tokens) * 0.55)
    fig, (ax_pred, ax_gold) = plt.subplots(2, 1, figsize=(width, 5.2), sharex=True)

    pred_heatmap = np.array([normalized_scores])
    pred_image = ax_pred.imshow(pred_heatmap, aspect="auto", cmap="YlOrRd", vmin=0.0, vmax=1.0)

    gold_values = [1.0 if label.upper().endswith("FOOD") else 0.0 for label in gold_labels]
    gold_heatmap = np.array([gold_values])
    gold_image = ax_gold.imshow(gold_heatmap, aspect="auto", cmap="Greens", vmin=0.0, vmax=1.0)

    ax_pred.set_yticks([])
    ax_gold.set_yticks([])
    ax_gold.set_xticks(range(len(tokens)))
    ax_gold.set_xticklabels(tokens, rotation=45, ha="right")
    ax_pred.set_title("Predicción de la IA")
    ax_gold.set_title("Valores reales")

    for index, (token, predicted_label, gold_label, score) in enumerate(zip(tokens, predicted_labels, gold_labels, scores)):
        ax_pred.text(
            index,
            0,
            f"P: {predicted_label}\n{score:.2f}",
            ha="center",
            va="center",
            fontsize=8,
            color="black",
        )
        ax_gold.text(
            index,
            0,
            f"R: {gold_label}",
            ha="center",
            va="center",
            fontsize=8,
            color="black",
        )

    colorbar = fig.colorbar(pred_image, ax=ax_pred, fraction=0.035, pad=0.04)
    colorbar.set_label("Importancia normalizada")
    fig.colorbar(gold_image, ax=ax_gold, fraction=0.035, pad=0.04).set_label("Valor real")
    fig.tight_layout()

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def render_multi_heatmap(
    sample_results: Sequence[Tuple[int, Sequence[str], Sequence[str], Sequence[str], Sequence[float]]],
    output_path: str,
) -> str:
    if not sample_results:
        raise ValueError("No hay samples para renderizar.")

    columns = len(sample_results)
    max_tokens = max(len(tokens) for _, tokens, _, _, _ in sample_results)
    column_width = max(5.0, max_tokens * 0.7)
    fig, axes = plt.subplots(2, columns, figsize=(column_width * columns, 6.2), squeeze=False)

    for column, (sample_index, tokens, predicted_labels, gold_labels, scores) in enumerate(sample_results):
        normalized_scores = normalize_scores(scores)
        pred_image = axes[0][column].imshow(np.array([normalized_scores]), aspect="auto", cmap="YlOrRd", vmin=0.0, vmax=1.0)
        gold_values = [1.0 if label.upper().endswith("FOOD") else 0.0 for label in gold_labels]
        gold_image = axes[1][column].imshow(np.array([gold_values]), aspect="auto", cmap="Greens", vmin=0.0, vmax=1.0)

        axes[0][column].set_title(f"Predicción - sample {sample_index}")
        axes[1][column].set_title(f"Real - sample {sample_index}")
        axes[0][column].set_yticks([])
        axes[1][column].set_yticks([])
        axes[0][column].set_xticks([])
        axes[1][column].set_xticks(range(len(tokens)))
        axes[1][column].set_xticklabels(tokens, rotation=45, ha="right")
        axes[1][column].tick_params(axis="x", labelsize=7)

        for index, (token, predicted_label, gold_label, score) in enumerate(zip(tokens, predicted_labels, gold_labels, scores)):
            axes[0][column].text(
                index,
                0,
                f"P: {predicted_label}\n{score:.2f}",
                ha="center",
                va="center",
                fontsize=7,
                color="black",
            )
            axes[1][column].text(
                index,
                0,
                f"R: {gold_label}",
                ha="center",
                va="center",
                fontsize=7,
                color="black",
            )

        fig.colorbar(pred_image, ax=axes[0][column], fraction=0.035, pad=0.04).set_label("Importancia normalizada")
        fig.colorbar(gold_image, ax=axes[1][column], fraction=0.035, pad=0.04).set_label("Valor real")

    fig.tight_layout()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera un mapa de calor para el modelo NER de ingredientes.")
    parser.add_argument(
        "--mode",
        choices=["text", "sample"],
        default="sample",
        help="Usa texto libre o un ejemplo etiquetado del dataset.",
    )
    parser.add_argument(
        "--text",
        default="I cooked tomato onion garlic with spoon on the table and water",
        help="Texto de entrada que se quiere analizar.",
    )
    parser.add_argument(
        "--split",
        choices=["train", "val", "test"],
        default="test",
        help="Split del dataset a usar en modo sample.",
    )
    parser.add_argument(
        "--sample-index",
        type=int,
        default=0,
        help="Índice del ejemplo a usar en modo sample.",
    )
    parser.add_argument(
        "--sample-count",
        type=int,
        default=3,
        help="Cantidad de ejemplos a renderizar en modo sample.",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(BASE_DIR, "..", "artifacts", "ner_heatmap.png"),
        help="Ruta del PNG de salida.",
    )
    args = parser.parse_args()

    tokenizer, model, device = load_model()
    if args.mode == "sample":
        sample_rows = load_labeled_samples(args.split, args.sample_index, args.sample_count)
        sample_results = []
        for sample_index, tokens, gold_labels in sample_rows:
            tokens, predicted_labels, gold_labels, scores = build_sample_importance(tokens, gold_labels, tokenizer, model, device)
            sample_results.append((sample_index, tokens, predicted_labels, gold_labels, scores))
        output_file = render_multi_heatmap(sample_results, args.output)
    else:
        tokens, predicted_labels, scores = build_text_importance(args.text, tokenizer, model, device)
        gold_labels = ["O" for _ in tokens]
        output_file = render_heatmap(tokens, predicted_labels, gold_labels, scores, args.output)

    print(f"Heatmap generado en: {output_file}")
    if args.mode == "sample":
        for sample_index, tokens, predicted_labels, gold_labels, scores in sample_results:
            print(f"\nSample {sample_index}")
            for token, predicted_label, gold_label, score in zip(tokens, predicted_labels, gold_labels, scores):
                print(f"{token:>16} | pred={predicted_label:<8} | real={gold_label:<8} | {score:.4f}")
    else:
        for token, predicted_label, gold_label, score in zip(tokens, predicted_labels, gold_labels, scores):
            print(f"{token:>16} | pred={predicted_label:<8} | real={gold_label:<8} | {score:.4f}")


if __name__ == "__main__":
    main()