import json
import os
import sys
import numpy as np
import torch
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, BertForTokenClassification, get_linear_schedule_with_warmup
from torch.optim import AdamW
from seqeval.metrics import f1_score as seq_f1, classification_report

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
MODEL_NAME  = "bert-base-uncased"
MAX_LEN     = 128
BATCH_SIZE  = 32        # larger batch → more stable gradients
EPOCHS      = 5
LR          = 2e-5      # slightly lower — safer for BERT fine-tuning
WARMUP_RATIO = 0.1      # 10% of total steps used for warmup
GRAD_CLIP   = 1.0       # max gradient norm
PATIENCE    = 3         # early stopping: stop after N epochs with no improvement

# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../datasets")
MODEL_DIR   = os.path.join(BASE_DIR, "../models/ner")
os.makedirs(MODEL_DIR, exist_ok=True)

def resolve_device():
    force_cuda = os.getenv("FORCE_CUDA", "0") == "1"
    if torch.cuda.is_available():
        return torch.device("cuda")
    if force_cuda:
        raise RuntimeError(
            "FORCE_CUDA=1 pero CUDA no esta disponible. "
            f"Python={sys.executable} | torch={torch.__version__} | cuda={torch.version.cuda}"
        )
    return torch.device("cpu")


device = resolve_device()
print(f"Python: {sys.executable}")
print(f"Torch: {torch.__version__} | CUDA toolkit: {torch.version.cuda}")
print(f"Device: {device}")


# ─────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────
def load_split(filename):
    with open(os.path.join(DATASET_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


def collect_label_set(*splits):
    labels = set()
    for split in splits:
        for item in split:
            labels.update(item["labels"])
    return ["O"] + sorted(x for x in labels if x != "O")


# ─────────────────────────────────────────
# DATASET
# ─────────────────────────────────────────
class NERDataset(Dataset):
    def __init__(self, data, tokenizer, label_to_id):
        self.data        = data
        self.tokenizer   = tokenizer
        self.label_to_id = label_to_id

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        words  = [w.lower() for w in sample["tokens"]]
        labels = sample["labels"]

        enc = self.tokenizer(
            words,
            is_split_into_words=True,
            truncation=True,
            padding="max_length",
            max_length=MAX_LEN,
            return_tensors="pt",
        )

        word_ids       = enc.word_ids(batch_index=0)
        aligned_labels = []
        prev_word_id   = None

        for word_id in word_ids:
            if word_id is None:
                aligned_labels.append(-100)
            elif word_id != prev_word_id:
                # First sub-token of a word → real label
                aligned_labels.append(self.label_to_id[labels[word_id]])
            else:
                # Continuation sub-tokens → ignore in loss
                aligned_labels.append(-100)
            prev_word_id = word_id

        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels":         torch.tensor(aligned_labels, dtype=torch.long),
        }


# ─────────────────────────────────────────
# CLASS WEIGHTS
# ─────────────────────────────────────────
def build_class_weights(train_split, label_to_id):
    counts = np.zeros(len(label_to_id), dtype=np.float64)
    for sample in train_split:
        for label in sample["labels"]:
            counts[label_to_id[label]] += 1.0
    counts[counts == 0] = 1.0
    weights = counts.sum() / (len(counts) * counts)
    weights = np.clip(weights, 0.5, 5.0)   # tighter clamp
    return torch.tensor(weights, dtype=torch.float32, device=device)


# ─────────────────────────────────────────
# ENTITY-LEVEL EVALUATION  (seqeval)
# ─────────────────────────────────────────
def evaluate(model, loader, id_to_label, loss_fn):
    """Returns (val_loss, entity_f1, report_string)."""
    model.eval()
    total_loss = 0.0
    all_true   = []   # list of label-sequences (strings)
    all_pred   = []

    with torch.no_grad():
        for batch in loader:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits  = outputs.logits
            loss    = loss_fn(logits.view(-1, logits.shape[-1]), labels.view(-1))
            total_loss += loss.item()

            pred_ids = torch.argmax(logits, dim=-1)

            for i in range(labels.shape[0]):
                true_seq = []
                pred_seq = []
                for t, p in zip(labels[i].cpu().tolist(), pred_ids[i].cpu().tolist()):
                    if t == -100:
                        continue
                    true_seq.append(id_to_label[t])
                    pred_seq.append(id_to_label[p])
                all_true.append(true_seq)
                all_pred.append(pred_seq)

    entity_f1 = seq_f1(all_true, all_pred)
    report    = classification_report(all_true, all_pred)
    avg_loss  = total_loss / max(len(loader), 1)
    return avg_loss, entity_f1, report


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    # --- Load data ---
    train_data = load_split("train.json")
    val_data   = load_split("val.json")

    label_list  = collect_label_set(train_data, val_data)
    label_to_id = {l: i for i, l in enumerate(label_list)}
    id_to_label = {i: l for l, i in label_to_id.items()}

    print(f"Train: {len(train_data)}  Val: {len(val_data)}")
    print(f"Labels: {label_list}")

    # --- Tokenizer & datasets ---
    tokenizer     = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
    train_dataset = NERDataset(train_data, tokenizer, label_to_id)
    val_dataset   = NERDataset(val_data,   tokenizer, label_to_id)

    pin_memory = device.type == "cuda"
    train_loader  = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,  num_workers=2, pin_memory=pin_memory)
    val_loader    = DataLoader(val_dataset,   batch_size=BATCH_SIZE, shuffle=False, num_workers=2, pin_memory=pin_memory)

    # --- Model ---
    model = BertForTokenClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(label_list),
        id2label=id_to_label,
        label2id=label_to_id,
    ).to(device)

    # --- Optimizer + scheduler with warmup ---
    optimizer    = AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    total_steps  = len(train_loader) * EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler    = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps,
    )

    # --- Weighted loss ---
    class_weights = build_class_weights(train_data, label_to_id)
    loss_fn       = torch.nn.CrossEntropyLoss(weight=class_weights, ignore_index=-100)

    # --- Training loop ---
    loss_history   = []
    f1_history     = []
    best_val_f1    = -1.0
    patience_count = 0

    for epoch in range(EPOCHS):
        model.train()
        epoch_loss = 0.0

        for batch in train_loader:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels_batch   = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits  = outputs.logits
            loss    = loss_fn(logits.view(-1, logits.shape[-1]), labels_batch.view(-1))

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)  # gradient clipping
            optimizer.step()
            scheduler.step()

            epoch_loss += loss.item()

        train_loss             = epoch_loss / max(len(train_loader), 1)
        val_loss, val_f1, report = evaluate(model, val_loader, id_to_label, loss_fn)

        loss_history.append(train_loss)
        f1_history.append(val_f1)

        print(
            f"\nEpoch {epoch+1}/{EPOCHS} | "
            f"train_loss={train_loss:.4f} | val_loss={val_loss:.4f} | entity_f1={val_f1:.4f}"
        )
        print(report)

        # --- Save best ---
        if val_f1 > best_val_f1:
            best_val_f1    = val_f1
            patience_count = 0
            model.save_pretrained(MODEL_DIR)
            tokenizer.save_pretrained(MODEL_DIR)
            print(f"✔ Best model saved (entity_f1={val_f1:.4f})")
        else:
            patience_count += 1
            print(f"No improvement ({patience_count}/{PATIENCE})")
            if patience_count >= PATIENCE:
                print("Early stopping triggered.")
                break

    # --- Plot ---
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(loss_history, marker="o")
    plt.title("Train Loss")
    plt.xlabel("Epoch")

    plt.subplot(1, 2, 2)
    plt.plot(f1_history, marker="o", color="green")
    plt.title("Val Entity F1 (seqeval)")
    plt.xlabel("Epoch")

    plt.tight_layout()
    metrics_path = os.path.join(MODEL_DIR, "metrics.png")
    plt.savefig(metrics_path)
    print(f"\nTraining done. Best entity_f1={best_val_f1:.4f}")
    print(f"Plot saved: {metrics_path}")