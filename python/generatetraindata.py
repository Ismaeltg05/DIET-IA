import random
import json
import re
import os
import string

# -------------------------
# INGREDIENTES
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../datasets")
with open(os.path.join(DATASET_DIR, "ALL_INGREDIENTS.json"), encoding="utf-8-sig") as f:
    ingredients = json.load(f)

# -------------------------
# CONFIG
# -------------------------
N_SAMPLES = 60000
NEGATIVE_RATIO = 0.20
MAX_INGS_PER_SAMPLE = 3

# -------------------------
# PALABRAS NO COMIDA (IMPORTANTES)
# -------------------------
COMMON_WORDS = [
    "and", "or", "but", "if", "the", "a",
    "computer", "phone", "car", "music",
    "run", "walk", "think", "know",
    "blue", "fast", "big", "happy"
]

# -------------------------
# GENERADOR DE TOKENS RANDOM (CLAVE)
# -------------------------
def random_token():
    length = random.randint(3, 10)
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# -------------------------
# NOISE REAL HUMANO
# -------------------------
NOISES = [
    "", " like", " maybe", " I think", " not sure",
    " honestly", " kind of", " idk", " probably", " I guess"
]

SLANG_PREFIX = [
    "bro", "yo", "hey", "so", "well", ""
]

QUESTION_NOISE = [
    "what do you think?", "any ideas?", "is that ok?",
    "would that work?", "help?", ""
]

# -------------------------
# TEMPLATES NATURALES
# -------------------------
TEMPLATES = [
    "I want something with {ings}",
    "I need a quick meal using {ings}",
    "What can I cook with {ings}?",
    "Give me dinner ideas with {ings}",
    "I have {ings}, what should I make?",
    "Can I cook something with {ings}?",
    "I found {ings} in my fridge",
    "Make me something with {ings}",
    "Is {ings} enough for a meal?",
    "My fridge has {ings}",
    "I just found {ings} at home",
]

NEGATIVE_TEMPLATES = [
    "I want a recipe but I don't know what to use",
    "Give me a random dinner idea",
    "What should I cook today?",
    "Any easy meal suggestions?",
    "I'm hungry but no idea what to cook",
]

# -------------------------
# TOKENIZER
# -------------------------
def tokenize(text):
    return re.sub(r"[^a-zA-Z\s]", "", text.lower()).split()

# -------------------------
# INGREDIENT SAMPLING
# -------------------------
def sample_ingredients():
    k = random.choices([1,2,3], weights=[0.4,0.4,0.2])[0]
    return random.sample(ingredients, k)

def format_ingredients(ings):
    return ", ".join(ings)

# -------------------------
# NOISE
# -------------------------
def add_noise(text):
    return text + random.choice(NOISES) + " " + random.choice(QUESTION_NOISE)

def maybe_slang(text):
    if random.random() < 0.3:
        return random.choice(SLANG_PREFIX) + " " + text
    return text

# -------------------------
# 🔥 HARD NEGATIVE (CLAVE)
# -------------------------
def generate_hard_negative():
    k = random.randint(5, 10)
    tokens = []

    for _ in range(k):
        if random.random() < 0.5:
            tokens.append(random.choice(COMMON_WORDS))
        else:
            tokens.append(random_token())

    return {
        "tokens": tokens,
        "labels": ["O"] * len(tokens)
    }

# -------------------------
# 🔥 INYECTAR TOKENS DESCONOCIDOS
# -------------------------
def inject_unknowns(tokens):
    if random.random() < 0.5:
        pos = random.randint(0, len(tokens))
        tokens.insert(pos, random_token())
    return tokens

# -------------------------
# BIO LABELING
# -------------------------
def bio_tag(tokens, ings):
    labels = ["O"] * len(tokens)

    for ing in ings:
        ing_tokens = ing.lower().split()

        for i in range(len(tokens) - len(ing_tokens) + 1):
            if tokens[i:i+len(ing_tokens)] == ing_tokens:
                labels[i] = "B-FOOD"
                for j in range(1, len(ing_tokens)):
                    labels[i+j] = "I-FOOD"

    return labels

# -------------------------
# SAMPLE GENERATOR
# -------------------------
def generate_example():
    use_ingredients = random.random() > NEGATIVE_RATIO

    # -------------------------
    # NEGATIVOS
    # -------------------------
    if not use_ingredients:
        if random.random() < 0.6:
            return generate_hard_negative()
        else:
            text = random.choice(NEGATIVE_TEMPLATES)
            tokens = tokenize(text)
            return {"tokens": tokens, "labels": ["O"] * len(tokens)}

    # -------------------------
    # POSITIVOS
    # -------------------------
    ings = sample_ingredients()
    ing_text = format_ingredients(ings)

    template = random.choice(TEMPLATES)
    text = template.format(ings=ing_text)

    if random.random() < 0.7:
        text = add_noise(text)

    text = maybe_slang(text)

    tokens = tokenize(text)

    # 🔥 AQUÍ ESTÁ LA MAGIA
    tokens = inject_unknowns(tokens)

    labels = bio_tag(tokens, ings)

    return {
        "tokens": tokens,
        "labels": labels
    }

# -------------------------
# DATASET
# -------------------------
def generate_dataset(n=N_SAMPLES):
    data = [generate_example() for _ in range(n)]
    random.shuffle(data)
    return data

# -------------------------
# SPLIT
# -------------------------
def split(data):
    n = len(data)
    train_end = int(0.8 * n)
    val_end = int(0.9 * n)
    return data[:train_end], data[train_end:val_end], data[val_end:]

# -------------------------
# CHECK
# -------------------------
def check_dataset(data):
    empty = sum(1 for d in data if all(l == "O" for l in d["labels"]))
    print(f"⚠ Samples sin entidades: {empty}/{len(data)}")

# -------------------------
# SAVE
# -------------------------
def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -------------------------
# RUN
# -------------------------
data = generate_dataset()

train, val, test = split(data)

check_dataset(train)

save("train.json", train)
save("val.json", val)
save("test.json", test)

print("Train:", len(train))
print("Val:", len(val))
print("Test:", len(test))
print("Saved ✔")