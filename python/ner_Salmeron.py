import json
import os
import numpy as np
import torch
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, BertForTokenClassification, get_linear_schedule_with_warmup
from torch.optim import AdamW
from sklearn.metrics import f1_score


# -------- CONFIG --------
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 5
LR = 3e-5


# -------- PATHS --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../datasets")
MODEL_DIR = os.path.join(BASE_DIR, "../models/ner")
os.makedirs(MODEL_DIR, exist_ok=True)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando dispositivo: {device}")


def load_split(filename):
    with open(os.path.join(DATASET_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


def collect_label_set(*splits):
    labels = set()
    for split in splits:
        for item in split:
            labels.update(item["labels"])
    # For BIO, keep O first and sort the rest for stable ids.
    ordered = ["O"] + sorted([x for x in labels if x != "O"])
    return ordered


class NERDataset(Dataset):
    def __init__(self, data, tokenizer, label_to_id):
        self.data = data
        self.tokenizer = tokenizer
        self.label_to_id = label_to_id

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        words = [w.lower() for w in sample["tokens"]]
        labels = sample["labels"]

        enc = self.tokenizer(
            words,
            is_split_into_words=True,
            truncation=True,
            padding="max_length",
            max_length=MAX_LEN,
            return_tensors="pt"
        )

        word_ids = enc.word_ids(batch_index=0)
        aligned_labels = []

        for word_id in word_ids:
            if word_id is None:
                aligned_labels.append(-100)
            else:
                aligned_labels.append(self.label_to_id[labels[word_id]])

        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(aligned_labels, dtype=torch.long)
        }


def build_class_weights(train_split, label_to_id):
    counts = np.zeros(len(label_to_id), dtype=np.float64)

    for sample in train_split:
        for label in sample["labels"]:
            counts[label_to_id[label]] += 1.0

    counts[counts == 0] = 1.0
    weights = counts.sum() / (len(counts) * counts)

    # Clamp to avoid unstable very large weights on very rare labels.
    weights = np.clip(weights, 0.5, 8.0)
    return torch.tensor(weights, dtype=torch.float32, device=device)


def evaluate(model, loader):
    model.eval()
    y_true = []
    y_pred = []
    total_loss = 0.0

    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            loss = loss_fn(logits.view(-1, logits.shape[-1]), labels.view(-1))
            total_loss += loss.item()

            pred_ids = torch.argmax(logits, dim=-1)
            mask = labels != -100

            y_true.extend(labels[mask].cpu().numpy().tolist())
            y_pred.extend(pred_ids[mask].cpu().numpy().tolist())

    macro_f1 = f1_score(y_true, y_pred, average="macro") if y_true else 0.0
    return total_loss / max(len(loader), 1), macro_f1


if __name__ == "__main__":
    train_data = load_split("train.json")
    val_data = load_split("val.json")

    labels = collect_label_set(train_data, val_data)
    label_to_id = {label: i for i, label in enumerate(labels)}
    id_to_label = {i: label for label, i in label_to_id.items()}

    print(f"Total ejemplos: train={len(train_data)} val={len(val_data)}")
    print(f"Etiquetas: {labels}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)

    train_dataset = NERDataset(train_data, tokenizer, label_to_id)
    val_dataset = NERDataset(val_data, tokenizer, label_to_id)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    model = BertForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(labels),
        id2label=id_to_label,
        label2id=label_to_id
    ).to(device)

    optimizer = AdamW(model.parameters(), lr=LR)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=total_steps
    )

    class_weights = build_class_weights(train_data, label_to_id)
    loss_fn = torch.nn.CrossEntropyLoss(weight=class_weights, ignore_index=-100)

    loss_history = []
    f1_history = []
    best_val_f1 = -1.0

    for epoch in range(EPOCHS):
        model.train()
        epoch_loss = 0.0

        for batch in train_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels_batch = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            loss = loss_fn(logits.view(-1, logits.shape[-1]), labels_batch.view(-1))

            loss.backward()
            optimizer.step()
            scheduler.step()

            epoch_loss += loss.item()

        train_loss = epoch_loss / max(len(train_loader), 1)
        val_loss, val_f1 = evaluate(model, val_loader)

        loss_history.append(train_loss)
        f1_history.append(val_f1)

        print(
            f"Epoch {epoch + 1}/{EPOCHS} | "
            f"train_loss={train_loss:.4f} | val_loss={val_loss:.4f} | val_f1={val_f1:.4f}"
        )

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            model.save_pretrained(MODEL_DIR)
            tokenizer.save_pretrained(MODEL_DIR)
            print(f"Guardado mejor modelo en {MODEL_DIR} (val_f1={val_f1:.4f})")

    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(loss_history)
    plt.title("Train Loss")
    plt.xlabel("Epoch")

    plt.subplot(1, 2, 2)
    plt.plot(f1_history)
    plt.title("Val Macro F1")
    plt.xlabel("Epoch")

    plt.tight_layout()
    metrics_path = os.path.join(MODEL_DIR, "metrics.png")
    plt.savefig(metrics_path)

    print(f"Entrenamiento terminado. Mejor val_f1={best_val_f1:.4f}")
    print(f"Grafica guardada en: {metrics_path}")