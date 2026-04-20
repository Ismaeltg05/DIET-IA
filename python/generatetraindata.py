import json
import re
import os
import random

# -------------------------
# INGREDIENTS
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../datasets")
with open(os.path.join(DATASET_DIR, "ALL_INGREDIENTS.json"), encoding="utf-8-sig") as f:
    ingredients = json.load(f)

# -------------------------
# CONFIG
# -------------------------
N_SAMPLES = 60000
NEGATIVE_RATIO = 0.20   # increased: more "no food" examples
MAX_INGS_PER_SAMPLE = 4  # allow up to 4

# -------------------------
# STOP WORDS (never tag these)
# -------------------------
STOP_WORDS = {
    "and", "or", "with", "some", "a", "an", "the", "like", "of",
    "maybe", "i", "think", "not", "sure", "honestly", "kind",
    "idk", "probably", "guess", "bro", "yo", "hey", "so", "well",
    "whit", "using", "use", "make", "cook", "recipe", "meal",
    "dinner", "lunch", "breakfast", "food", "dish", "idea", "ideas",
    "what", "can", "do", "is", "that", "ok", "would", "help",
    "any", "just", "found", "have", "has", "my", "fridge", "home",
    "want", "need", "quick", "give", "me", "something", "enough",
    "for", "lot", "lots", "bit", "few", "today", "random",
    "hungry", "but", "no", "know",
}

# -------------------------
# NOISE
# -------------------------
TRAILING_NOISES = [
    "", ", what do you think?", ", any ideas?", ", is that ok?",
    ", would that work?", ", help?", " please", " thanks",
    " lol", " :)", " idk", " i guess",
]

SLANG_PREFIXES = [
    "bro ", "yo ", "hey ", "so ", "well ", "",
]

# -------------------------
# TYPO SIMULATION (realistic human errors)
# -------------------------
COMMON_TYPOS = {
    "with": ["whit", "wiht", "wit"],
    "some": ["som", "somme"],
    "recipe": ["recipie", "reciepe"],
    "tomato": ["tomatoe", "tomato"],
    "lettuce": ["letuce", "letttuce"],
}

def maybe_typo(text):
    for correct, wrongs in COMMON_TYPOS.items():
        if correct in text and random.random() < 0.08:
            text = text.replace(correct, random.choice(wrongs), 1)
    return text

# -------------------------
# TEMPLATES — varied structures
# -------------------------
# {ings} will be replaced by a naturally-formatted list

POSITIVE_TEMPLATES = [
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
    "I'd like a recipe with {ings}",
    "I'll like a recipe with {ings}",
    "Could you suggest something using {ings}?",
    "Help me cook {ings}",
    "I only have {ings} left",
    "What meal can I make out of {ings}?",
    "Any ideas with {ings}?",
    "I want to use {ings}",
    "Recipe ideas for {ings} please",
    "Tonight I have {ings}",
    "Using {ings}, what can I prepare?",
    "I wish I could make something with {ings}",
    "I want a recipe using {ings}",
]

NEGATIVE_TEMPLATES = [
    "I want a recipe but I don't know what to use",
    "Give me a random dinner idea",
    "What should I cook today?",
    "Any easy meal suggestions?",
    "I'm hungry but no idea what to cook",
    "What's a good dish for tonight?",
    "Suggest me something delicious",
    "I need inspiration for dinner",
    "What do people usually cook for lunch?",
    "Can you recommend a healthy meal?",
    "I feel like eating something different",
    "Surprise me with a recipe",
    "Something quick and easy please",
    "Hola me llamo Luis",          # non-English garbage
    "Hello my name is John",
    "What's the weather like today?",
    "Tell me a joke",
    "I like cooking but I'm not sure what",
]

# -------------------------
# TOKENIZER — strips punctuation cleanly
# -------------------------
def tokenize(text):
    """Lowercase, remove all punctuation, split on whitespace."""
    return re.sub(r"[^a-zA-Z\s]", "", text.lower()).split()

# -------------------------
# INGREDIENT LIST FORMATTING
# Produces natural English lists: "X", "X and Y", "X, Y and Z"
# -------------------------
def format_ingredients(ings):
    if len(ings) == 1:
        return ings[0]
    elif len(ings) == 2:
        return f"{ings[0]} and {ings[1]}"
    else:
        return ", ".join(ings[:-1]) + f" and {ings[-1]}"

def sample_ingredients():
    k = random.choices([1, 2, 3, 4], weights=[0.3, 0.35, 0.25, 0.1])[0]
    return random.sample(ingredients, k)

# -------------------------
# BIO TAGGING — robust, no stop words, no conjunctions
# -------------------------
def bio_tag(tokens, ings):
    """
    Tags each ingredient as B-FOOD / I-FOOD.
    Skips tokens that are stop words to avoid tagging 'and', 'some', etc.
    Each ingredient is searched independently; 'and' between two ingredients
    remains O.
    """
    labels = ["O"] * len(tokens)

    for ing in ings:
        ing_tokens = re.sub(r"[^a-zA-Z\s]", "", ing.lower()).split()
        if not ing_tokens:
            continue

        for i in range(len(tokens) - len(ing_tokens) + 1):
            window = tokens[i:i + len(ing_tokens)]
            if window == ing_tokens:
                # Extra safety: don't tag if any token is a stop word
                # (protects against single-word ingredients that are stop words)
                if any(t in STOP_WORDS for t in ing_tokens):
                    continue
                labels[i] = "B-FOOD"
                for j in range(1, len(ing_tokens)):
                    labels[i + j] = "I-FOOD"

    return labels

# -------------------------
# EXAMPLE GENERATOR
# -------------------------
def generate_example():
    is_negative = random.random() < NEGATIVE_RATIO

    if is_negative:
        text = random.choice(NEGATIVE_TEMPLATES)
        tokens = tokenize(text)
        return {"tokens": tokens, "labels": ["O"] * len(tokens)}

    # --- Positive sample ---
    ings = sample_ingredients()
    ing_text = format_ingredients(ings)

    template = random.choice(POSITIVE_TEMPLATES)
    text = template.format(ings=ing_text)

    # Natural noise
    if random.random() < 0.5:
        text = text + random.choice(TRAILING_NOISES)
    if random.random() < 0.25:
        text = random.choice(SLANG_PREFIXES) + text
    if random.random() < 0.1:
        text = maybe_typo(text)

    tokens = tokenize(text)
    labels = bio_tag(tokens, ings)

    return {"tokens": tokens, "labels": labels}

# -------------------------
# DATASET GENERATION
# -------------------------
def generate_dataset(n=N_SAMPLES):
    data = [generate_example() for _ in range(n)]
    random.shuffle(data)
    return data

# -------------------------
# TRAIN / VAL / TEST SPLIT
# -------------------------
def split(data):
    n = len(data)
    train = data[:int(0.8 * n)]
    val = data[int(0.8 * n):int(0.9 * n)]
    test = data[int(0.9 * n):]
    return train, val, test

# -------------------------
# VALIDATION
# -------------------------
def check_dataset(data, label="dataset"):
    total = len(data)
    empty = sum(1 for d in data if all(l == "O" for l in d["labels"]))
    has_food = total - empty

    # Count 'and' incorrectly tagged
    bad_and = sum(
        1 for d in data
        for tok, lbl in zip(d["tokens"], d["labels"])
        if tok == "and" and lbl != "O"
    )

    print(f"\n[{label}]")
    print(f"  Total samples  : {total}")
    print(f"  With food tags : {has_food} ({has_food/total*100:.1f}%)")
    print(f"  No-food (O-only): {empty} ({empty/total*100:.1f}%)")
    print(f"  'and' mis-tagged: {bad_and}")

# -------------------------
# SAVE
# -------------------------
def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    print("Generating dataset...")
    data = generate_dataset()

    train, val, test = split(data)

    check_dataset(train, "TRAIN")
    check_dataset(val,   "VAL")
    check_dataset(test,  "TEST")

    save(os.path.join(DATASET_DIR, "train.json"), train)
    save(os.path.join(DATASET_DIR, "val.json"),   val)
    save(os.path.join(DATASET_DIR, "test.json"),  test)

    print("\nSaved ✔")