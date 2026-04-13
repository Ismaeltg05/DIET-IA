import json
import os
import torch
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForTokenClassification, get_linear_schedule_with_warmup
from torch.optim import AdamW
from sklearn.metrics import f1_score

# -----------------------------
# CONFIG
# -----------------------------
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 5
LR = 3e-5

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Usando dispositivo: {device}")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../datasets")
MODEL_DIR = os.path.join(BASE_DIR, "../models/ner")
os.makedirs(MODEL_DIR, exist_ok=True)

# -----------------------------
# LABELS
# -----------------------------
LABELS = ["O", "B-FOOD", "I-FOOD"]
label_to_id = {l: i for i, l in enumerate(LABELS)}
NUM_LABELS = len(LABELS)

# -----------------------------
# LOAD DATA
# -----------------------------
def load_split(file):
    with open(os.path.join(DATASET_DIR, file), encoding="utf-8") as f:
        return json.load(f)

train_data = load_split("train.json")
val_data = load_split("val.json")
test_data = load_split("test.json")

# -----------------------------
# PREP DATA FUNCTION
# -----------------------------
def preprocess(data):
    texts = []
    labels = []

    for item in data:
        tokens = item["tokens"]
        label_ids = [label_to_id[l] for l in item["labels"]]

        texts.append(" ".join(tokens).lower())
        labels.append(label_ids)

    return texts, labels

train_texts, train_labels = preprocess(train_data)
val_texts, val_labels = preprocess(val_data)

# -----------------------------
# TOKENIZER
# -----------------------------
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

def encode(texts):
    return tokenizer(
        texts,
        truncation=True,
        padding="max_length",
        max_length=MAX_LEN,
        return_tensors="pt"
    )

train_enc = encode(train_texts)
val_enc = encode(val_texts)

# -----------------------------
# PAD LABELS
# -----------------------------
def pad_labels(labels_list):
    padded = []

    for labels in labels_list:
        labels = labels[:MAX_LEN]
        labels += [-100] * (MAX_LEN - len(labels))
        padded.append(labels)

    return torch.tensor(padded)

train_labels_tensor = pad_labels(train_labels)
val_labels_tensor = pad_labels(val_labels)

# -----------------------------
# DATASET CLASS
# -----------------------------
class NERDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: self.encodings[k][idx] for k in self.encodings}
        item["labels"] = self.labels[idx]
        return item

train_dataset = NERDataset(train_enc, train_labels_tensor)
val_dataset = NERDataset(val_enc, val_labels_tensor)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

# -----------------------------
# MODEL
# -----------------------------
model = BertForTokenClassification.from_pretrained(
    MODEL_NAME,
    num_labels=NUM_LABELS
).to(device)

optimizer = AdamW(model.parameters(), lr=LR)
total_steps = len(train_loader) * EPOCHS

scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=0,
    num_training_steps=total_steps
)

scaler = torch.cuda.amp.GradScaler(enabled=torch.cuda.is_available())

# -----------------------------
# TRAIN LOOP
# -----------------------------
loss_history = []
f1_history = []
best_loss = float("inf")

for epoch in range(EPOCHS):

    model.train()
    total_loss = 0

    for batch in train_loader:
        optimizer.zero_grad()

        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels_batch = batch["labels"].to(device)

        with torch.cuda.amp.autocast(enabled=torch.cuda.is_available()):
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels_batch
            )

            loss = outputs.loss

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        scheduler.step()

        total_loss += loss.item()

    # -------------------------
    # VALIDATION REAL
    # -------------------------
    model.eval()
    preds_list = []
    true_list = []

    with torch.no_grad():
        for batch in val_loader:

            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels_batch = batch["labels"].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )

            preds = torch.argmax(outputs.logits, dim=-1)

            for p, l in zip(preds, labels_batch):
                mask = l != -100
                preds_list.extend(p[mask].cpu().numpy())
                true_list.extend(l[mask].cpu().numpy())

    avg_loss = total_loss / len(train_loader)
    epoch_f1 = f1_score(true_list, preds_list, average="macro")

    loss_history.append(avg_loss)
    f1_history.append(epoch_f1)

    print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {avg_loss:.4f} | Val F1: {epoch_f1:.4f}")

    if avg_loss < best_loss:
        best_loss = avg_loss
        model.save_pretrained(MODEL_DIR)
        tokenizer.save_pretrained(MODEL_DIR)
        print("💾 Modelo guardado.")

# -----------------------------
# PLOTS
# -----------------------------
plt.figure(figsize=(10,5))

plt.subplot(1,2,1)
plt.plot(loss_history)
plt.title("Loss")

plt.subplot(1,2,2)
plt.plot(f1_history)
plt.title("Val F1")

plt.tight_layout()
plt.savefig(os.path.join(MODEL_DIR, "metrics.png"))

print("✅ Entrenamiento terminado")