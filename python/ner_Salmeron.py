import json
import os
import torch
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, AdamW

# -------- CONFIG --------
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 128
BATCH_SIZE = 8
EPOCHS = 3
LR = 2e-5

# -------- PATHS (ROBUSTOS) --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../datasets")
MODEL_DIR = os.path.join(BASE_DIR, "../models/ner")

# -------- CREATE DIR --------
os.makedirs(MODEL_DIR, exist_ok=True)

# -------- LOAD LABELS --------
with open(os.path.join(DATASET_DIR, "ALL_INGREDIENTS.json")) as f:
    ALL_INGREDIENTS = [ing.lower() for ing in json.load(f)]

with open(os.path.join(DATASET_DIR, "ALL_TAGS.json")) as f:
    ALL_TAGS = [tag.lower() for tag in json.load(f)]

ALL_LABELS = ALL_INGREDIENTS + ALL_TAGS
NUM_LABELS = len(ALL_LABELS)

# Índices rápidos
ingredient_to_idx = {ing: i for i, ing in enumerate(ALL_INGREDIENTS)}
tag_to_idx = {tag: i for i, tag in enumerate(ALL_TAGS)}

# -------- LOAD DATA --------
with open(os.path.join(DATASET_DIR, "datasetNER.json")) as f:
    data = json.load(f)

# -------- CLEAN DATA --------
for item in data:
    item["text"] = item["text"].lower()
    item["ingredients"] = [i.lower() for i in item["ingredients"]]
    item["tags"] = [t.lower() for t in item["tags"]]

# -------- DATASET --------
class RecipeDataset(Dataset):
    def __init__(self, data, tokenizer):
        self.data = data
        self.tokenizer = tokenizer

    def encode_labels(self, item):
        labels = [0] * NUM_LABELS

        for ing in item["ingredients"]:
            if ing in ingredient_to_idx:
                labels[ingredient_to_idx[ing]] = 1

        for tag in item["tags"]:
            if tag in tag_to_idx:
                labels[len(ALL_INGREDIENTS) + tag_to_idx[tag]] = 1

        return torch.tensor(labels, dtype=torch.float)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        encoding = self.tokenizer(
            item["text"],
            truncation=True,
            padding="max_length",
            max_length=MAX_LEN,
            return_tensors="pt"
        )

        labels = self.encode_labels(item)

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": labels
        }

# -------- TOKENIZER --------
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

dataset = RecipeDataset(data, tokenizer)
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# -------- MODEL --------
model = BertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=NUM_LABELS,
    problem_type="multi_label_classification"
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

optimizer = AdamW(model.parameters(), lr=LR)
loss_fn = torch.nn.BCEWithLogitsLoss()

# -------- TRAIN --------
loss_history = []
accuracy_history = []

model.train()

for epoch in range(EPOCHS):
    total_loss = 0
    correct = 0
    total = 0

    for batch in loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        logits = outputs.logits
        loss = loss_fn(logits, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        # -------- ACCURACY --------
        preds = (torch.sigmoid(logits) > 0.5).float()
        correct += (preds == labels).sum().item()
        total += labels.numel()

    avg_loss = total_loss / len(loader)
    accuracy = correct / total

    loss_history.append(avg_loss)
    accuracy_history.append(accuracy)

    print(f"Epoch {epoch+1} - Loss: {avg_loss:.4f} - Acc: {accuracy:.4f}")

# -------- SAVE MODEL --------
model.save_pretrained(MODEL_DIR)
tokenizer.save_pretrained(MODEL_DIR)

# -------- SAVE GRAPH --------
plt.figure()
plt.plot(loss_history, label="Loss")
plt.plot(accuracy_history, label="Accuracy")

plt.xlabel("Epoch")
plt.ylabel("Value")
plt.title("Training Metrics")
plt.legend()

graph_path = os.path.join(MODEL_DIR, "training.png")
plt.savefig(graph_path)

print(f"📊 Gráfico guardado en: {graph_path}")
print("✅ Modelo guardado en:", MODEL_DIR)