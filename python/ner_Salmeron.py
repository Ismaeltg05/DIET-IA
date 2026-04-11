import json
import os
import torch
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from torch.optim import AdamW

# -------- CONFIG --------
MODEL_NAME = "bert-base-uncased"
MAX_LEN = 128
BATCH_SIZE = 32
EPOCHS = 3
LR = 2e-5

# -------- PATHS --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../datasets")
MODEL_DIR = os.path.join(BASE_DIR, "../models/ner")

os.makedirs(MODEL_DIR, exist_ok=True)

print("🚀 Cargando datasets...")

# -------- LOAD LABELS --------
with open(os.path.join(DATASET_DIR, "ALL_INGREDIENTS.json")) as f:
    ALL_INGREDIENTS = [x.lower() for x in json.load(f)]

with open(os.path.join(DATASET_DIR, "ALL_TAGS.json")) as f:
    ALL_TAGS = [x.lower() for x in json.load(f)]

ALL_LABELS = ALL_INGREDIENTS + ALL_TAGS
NUM_LABELS = len(ALL_LABELS)

ingredient_to_idx = {ing: i for i, ing in enumerate(ALL_INGREDIENTS)}
tag_to_idx = {tag: i for i, tag in enumerate(ALL_TAGS)}

# -------- LOAD DATA --------
with open(os.path.join(DATASET_DIR, "datasetNER.json")) as f:
    data = json.load(f)

print(f"📦 Dataset cargado: {len(data)} ejemplos")

# -------- CLEAN DATA --------
texts = []
labels_list = []

for item in data:
    texts.append(item["text"].lower())

    labels = [0] * NUM_LABELS

    for ing in item["ingredients"]:
        ing = ing.lower()
        if ing in ingredient_to_idx:
            labels[ingredient_to_idx[ing]] = 1

    for tag in item["tags"]:
        tag = tag.lower()
        if tag in tag_to_idx:
            labels[len(ALL_INGREDIENTS) + tag_to_idx[tag]] = 1

    labels_list.append(labels)

# -------- TOKENIZER --------
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

print("⚡ Tokenizando dataset (UNA SOLA VEZ)...")

encodings = tokenizer(
    texts,
    truncation=True,
    padding="max_length",
    max_length=MAX_LEN
)

input_ids = torch.tensor(encodings["input_ids"])
attention_mask = torch.tensor(encodings["attention_mask"])
labels_tensor = torch.tensor(labels_list, dtype=torch.float)

# -------- DATASET OPTIMIZADO --------
class RecipeDataset(Dataset):
    def __init__(self, input_ids, attention_mask, labels):
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        self.labels = labels

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return {
            "input_ids": self.input_ids[idx],
            "attention_mask": self.attention_mask[idx],
            "labels": self.labels[idx]
        }

dataset = RecipeDataset(input_ids, attention_mask, labels_tensor)

loader = DataLoader(
    dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

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

best_loss = float("inf")

model.train()

print("🔥 INICIANDO ENTRENAMIENTO...\n")

for epoch in range(EPOCHS):
    total_loss = 0
    correct = 0
    total = 0

    for i, batch in enumerate(loader):

        if i % 50 == 0:
            print(f"Batch {i}/{len(loader)}")

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

        preds = (torch.sigmoid(logits) > 0.5).float()
        correct += (preds == labels).sum().item()
        total += labels.numel()

    avg_loss = total_loss / len(loader)
    accuracy = correct / total

    loss_history.append(avg_loss)
    accuracy_history.append(accuracy)

    print(f"\n📊 Epoch {epoch+1}")
    print(f"Loss: {avg_loss:.4f}")
    print(f"Acc:  {accuracy:.4f}")

    # -------- SAVE BEST MODEL --------
    if avg_loss < best_loss:
        best_loss = avg_loss
        print("💾 Mejor modelo guardado")

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
print("✅ Entrenamiento terminado. Mejor modelo guardado en:", MODEL_DIR)