import json
import re
import os
import random

# -------------------------
# INGREDIENTS
# -------------------------
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "../datasets")
with open(os.path.join(DATASET_DIR, "ALL_INGREDIENTS.json"), encoding="utf-8-sig") as f:
    ingredients = json.load(f)

# -------------------------
# CONFIG
# -------------------------
N_SAMPLES      = 100000   # more data → better generalization
NEGATIVE_RATIO = 0.20

# -------------------------
# STOP WORDS — never tag these
# -------------------------
STOP_WORDS = {
    "and", "or", "with", "some", "a", "an", "the", "like", "of", "for",
    "maybe", "i", "think", "not", "sure", "honestly", "kind", "idk",
    "probably", "guess", "bro", "yo", "hey", "so", "well", "basically",
    "whit", "using", "use", "make", "cook", "recipe", "meal", "dinner",
    "lunch", "breakfast", "food", "dish", "idea", "ideas", "what", "can",
    "do", "is", "that", "ok", "would", "help", "any", "just", "found",
    "have", "has", "my", "fridge", "home", "want", "need", "quick", "give",
    "me", "something", "enough", "lot", "lots", "bit", "few", "today",
    "random", "hungry", "but", "no", "know", "totally", "grabbed", "also",
    "perhaps", "definitely", "whatever", "because", "then", "if", "was",
    "thinking", "great", "too", "be", "you", "stuff", "things", "left",
    "only", "actually", "really", "very", "quite", "much", "eat", "eating",
    "y", "e", "con", "de", "la", "el", "en", "please", "tonight", "at",
    "in", "on", "up", "out", "get", "got", "put", "take", "let", "go",
    "work", "works", "end", "why", "grab", "there", "here", "could",
    "should", "might", "will", "also", "still", "even", "though",
}

# -------------------------
# INTRUDERS
# -------------------------
INTRUDERS = [
    "ismael", "carlos", "pedro", "john", "maria", "luis", "anna", "jorge",
    "sofia", "david", "laura", "miguel", "sara", "pablo", "elena",
    "table", "chair", "phone", "laptop", "book", "car", "house", "dog",
    "cat", "tree", "window", "door", "pen", "bag", "shirt", "shoe",
    "something", "somewhere", "whatever", "nothing", "everything", "stuff",
    "happy", "sad", "tired", "bored", "cool", "nice", "weird", "old",
    "monday", "friday", "python", "music", "game", "word", "idea",
]

# -------------------------
# CONTEXTS — the key fix
# Each context wraps a single ingredient or list.
# We massively expand these so each ingredient appears in many contexts.
# -------------------------

# Contexts for a SINGLE ingredient {ing}
SINGLE_CONTEXTS = [
    # found/have
    "I found some {ing}",
    "I found {ing} in my fridge",
    "I found {ing} at home",
    "I have some {ing}",
    "I have {ing}",
    "I have {ing} left",
    "I have some {ing} left",
    "there is some {ing}",
    "there is {ing} in the fridge",
    "there's {ing} left",
    "there's some {ing} at home",
    # want/need
    "I want to use {ing}",
    "I want some {ing}",
    "I need {ing}",
    "I need some {ing}",
    "I feel like using {ing}",
    "I feel like eating {ing}",
    # thinking/maybe
    "I was thinking maybe {ing}",
    "I was thinking of using {ing}",
    "I was thinking {ing} would be good",
    "maybe {ing}",
    "maybe some {ing}",
    "maybe I could use {ing}",
    "perhaps {ing}",
    "perhaps some {ing}",
    "perhaps I could add {ing}",
    "probably {ing}",
    "probably some {ing}",
    # recipe context
    "a recipe with {ing}",
    "recipe with {ing}",
    "a recipe using {ing}",
    "cook something with {ing}",
    "cook with {ing}",
    "make something with {ing}",
    "make a dish with {ing}",
    "dinner with {ing}",
    "meal with {ing}",
    "lunch with {ing}",
    # grab/use
    "I grabbed some {ing}",
    "I grabbed {ing}",
    "I could use {ing}",
    "I should use {ing}",
    "using {ing}",
    "use {ing}",
    # like/love
    "I like {ing}",
    "I love {ing}",
    "I enjoy {ing}",
    # idk/guess
    "{ing} idk",
    "{ing} I guess",
    "{ing} maybe",
    "{ing} would be great",
    "{ing} would work",
    "{ing} could work",
    # at end of sentence
    "and definitely {ing}",
    "and also {ing}",
    "and {ing} too",
    "and some {ing}",
    "and {ing}",
    "plus {ing}",
    "also {ing}",
    "with {ing} too",
    # natural snippets
    "some {ing} maybe",
    "a bit of {ing}",
    "a little {ing}",
    "a lot of {ing}",
    "lots of {ing}",
]

# Contexts for a LIST of ingredients {ings}
LIST_CONTEXTS = [
    "I want something with {ings}",
    "I need a quick meal using {ings}",
    "What can I cook with {ings}?",
    "Give me dinner ideas with {ings}",
    "I have {ings}, what should I make?",
    "Can I cook something with {ings}?",
    "I found {ings} in my fridge",
    "I found some {ings} at home",
    "Make me something with {ings}",
    "My fridge has {ings}",
    "I just found {ings} at home",
    "I'd like a recipe with {ings}",
    "I want to use {ings}",
    "Recipe with {ings} please",
    "Tonight I have {ings}",
    "I only have {ings} left",
    "I wish I could cook something with {ings}",
    "I want a recipe using {ings}",
    "Could you suggest something with {ings}?",
    "Help me cook with {ings}",
    "Any ideas with {ings}?",
    "I like to eat {ings}",
    "I want to eat {ings}",
    "I feel like eating {ings}",
    "I was thinking maybe {ings}",
    "I was thinking of using {ings}",
    "maybe I could use {ings}",
    "perhaps I could cook with {ings}",
    "I have {ings} and I don't know what to make",
    "I found {ings} and need recipe ideas",
    "I grabbed {ings} from the store",
    "I bought {ings} today",
    "using {ings} what can I make?",
    "what do I cook with {ings}?",
    "any recipe with {ings}?",
    "dinner ideas using {ings}?",
]

# Filler words between ingredient sub-phrases in long sentences
FILLERS = [
    "and honestly", "like maybe", "probably", "idk also", "or something",
    "and also like", "and perhaps", "I think also", "and definitely",
    "plus like", "and maybe", "I guess also", "and well", "or whatever",
    "bro also", "and basically", "and obviously", "I mean also",
    "and totally", "or perhaps", "and actually", "and you know",
    "and", "and also", "plus", "also",
]

SENTENCE_STARTERS = [
    "So basically", "Hey so", "I was thinking", "Bro I was wondering",
    "Well I think", "Honestly", "I kind of want to cook something",
    "Yo I just found some stuff", "I mean", "So",
    "Well honestly", "Bro", "Hey", "", "", "",
]

SENTENCE_ENDERS = [
    "what do you think?", "any ideas?", "help me out", "is that enough?",
    "would that work?", "please", "thanks", "I don't know lol",
    "not sure though", "idk", "I guess", "", "", "", "",
]

# -------------------------
# TOKENIZER
# -------------------------
def tokenize(text):
    return re.sub(r"[^a-zA-Z\s]", "", text.lower()).split()

# -------------------------
# BIO TAGGING
# -------------------------
def bio_tag(tokens, ings):
    labels = ["O"] * len(tokens)
    for ing in ings:
        ing_tokens = re.sub(r"[^a-zA-Z\s]", "", ing.lower()).split()
        if not ing_tokens or any(t in STOP_WORDS for t in ing_tokens):
            continue
        for i in range(len(tokens) - len(ing_tokens) + 1):
            if tokens[i:i + len(ing_tokens)] == ing_tokens:
                labels[i] = "B-FOOD"
                for j in range(1, len(ing_tokens)):
                    labels[i + j] = "I-FOOD"
    return labels

# -------------------------
# FORMAT INGREDIENT LIST
# -------------------------
def format_list(ings):
    if len(ings) == 1:
        return ings[0]
    elif len(ings) == 2:
        sep = random.choice([" and ", ", "])
        return f"{ings[0]}{sep}{ings[1]}"
    else:
        # vary separators: comma-only, comma+and, all-and
        style = random.random()
        if style < 0.4:
            return ", ".join(ings[:-1]) + f" and {ings[-1]}"
        elif style < 0.7:
            return ", ".join(ings)
        else:
            return " and ".join(ings)

# -------------------------
# GENERATORS
# -------------------------

def generate_simple(ings):
    """Short direct sentence with a list of ingredients."""
    return random.choice(LIST_CONTEXTS).format(ings=format_list(ings))


def generate_long_noisy(ings):
    """
    Long sentence where each ingredient appears in its own sub-phrase,
    separated by fillers. This covers cases like:
    'I found some tomato ... and maybe garlic ... and definitely olive oil'
    """
    parts   = []
    starter = random.choice(SENTENCE_STARTERS)
    if starter:
        parts.append(starter)

    random.shuffle(ings)
    for i, ing in enumerate(ings):
        ctx = random.choice(SINGLE_CONTEXTS).format(ing=ing)
        parts.append(ctx)
        if i < len(ings) - 1:
            parts.append(random.choice(FILLERS))

    ender = random.choice(SENTENCE_ENDERS)
    if ender:
        parts.append(ender)

    return " ".join(parts)


def generate_list_with_intruders(ings):
    """
    Mixes real ingredients with non-food intruder words in a list.
    Teaches: not every word in a list is food.
    """
    n_intruders  = random.randint(1, 2)
    intruder_words = random.sample(INTRUDERS, n_intruders)
    all_items    = ings + intruder_words
    random.shuffle(all_items)
    return random.choice(LIST_CONTEXTS).format(ings=format_list(all_items))


def generate_mixed_contexts(ings):
    """
    Each ingredient gets its OWN varied context within one sentence.
    Covers cases where the same ingredient appears after different triggers.
    Example: 'I found some tomato and I was thinking garlic and maybe olive oil'
    """
    parts = []
    random.shuffle(ings)
    for i, ing in enumerate(ings):
        parts.append(random.choice(SINGLE_CONTEXTS).format(ing=ing))
        if i < len(ings) - 1:
            parts.append(random.choice(["and", "also", "plus", "and also", "and maybe"]))
    return " ".join(parts)


# -------------------------
# NEGATIVE TEMPLATES
# -------------------------
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
    "I like cooking but I'm not sure what to make",
    "What are some popular dishes?",
    "I want to eat something but I have no ingredients",
    "Help me plan my meals for the week",
    "What is a good recipe for beginners?",
    "I want to try something new tonight",
    "Any vegetarian meal ideas?",
    "Hola me llamo Luis",
    "Hello my name is John",
    "Bonjour je m appelle Pierre",
    "Ciao mi chiamo Marco",
    "Hola que tal como estas",
    "Me llamo Carlos y tengo hambre",
    "Buenos dias como te llamas",
    "Helo mi nome is Pedro",
    "Salut je suis Antoine",
    "asdf qwerty zxcv blah blah",
    "foo bar baz qux lorem ipsum",
    "blah blah blah something random here",
    "random words that mean nothing at all",
    "helo mi nome tomato please help",
    "nope nada zilch nothing here folks",
    "What's the weather like today?",
    "Tell me a joke",
    "How do I learn Python programming?",
    "What is the capital of France?",
    "Who won the football match yesterday?",
    "Can you help me write an email?",
    "What movies are popular right now?",
    "How do I fix my computer?",
    "I like ismael and carlos and pedro",
    "tomato y lettuce",
    "lettuce pussy meet",
    "I found some stuff at home",
    "I was thinking about something",
    "maybe I could try something new",
    "there is nothing in my fridge",
    "I have no idea what to cook",
]

# -------------------------
# SAMPLE GENERATOR
# -------------------------
def sample_ingredients():
    k = random.choices([1, 2, 3, 4, 5], weights=[0.15, 0.25, 0.30, 0.20, 0.10])[0]
    return random.sample(ingredients, k)

def generate_example():
    if random.random() < NEGATIVE_RATIO:
        text   = random.choice(NEGATIVE_TEMPLATES)
        tokens = tokenize(text)
        return {"tokens": tokens, "labels": ["O"] * len(tokens)}

    ings  = sample_ingredients()

    # 4 styles — each one teaches different context patterns
    style = random.random()
    if style < 0.25:
        text = generate_simple(ings)           # short list
    elif style < 0.50:
        text = generate_long_noisy(ings)       # long scattered sentence
    elif style < 0.75:
        text = generate_mixed_contexts(ings)   # each ing in own context
    else:
        text = generate_list_with_intruders(ings)  # intruder words in list

    tokens = tokenize(text)
    labels = bio_tag(tokens, ings)
    return {"tokens": tokens, "labels": labels}

# -------------------------
# DATASET
# -------------------------
def generate_dataset(n=N_SAMPLES):
    data = [generate_example() for _ in range(n)]
    random.shuffle(data)
    return data

def split(data):
    n     = len(data)
    train = data[:int(0.8 * n)]
    val   = data[int(0.8 * n):int(0.9 * n)]
    test  = data[int(0.9 * n):]
    return train, val, test

# -------------------------
# VALIDATION
# -------------------------
def check_dataset(data, label="dataset"):
    total    = len(data)
    empty    = sum(1 for d in data if all(l == "O" for l in d["labels"]))
    has_food = total - empty
    bad_and  = sum(
        1 for d in data
        for tok, lbl in zip(d["tokens"], d["labels"])
        if tok == "and" and lbl != "O"
    )
    print(f"\n[{label}]")
    print(f"  Total           : {total}")
    print(f"  With food tags  : {has_food} ({has_food/total*100:.1f}%)")
    print(f"  No-food (O)     : {empty}  ({empty/total*100:.1f}%)")
    print(f"  'and' mis-tagged: {bad_and}")

    long_samples = [d for d in data if len(d["tokens"]) > 8]
    print(f"\n  Sample examples:")
    for d in random.sample(long_samples, min(6, len(long_samples))):
        pairs = list(zip(d["tokens"], d["labels"]))
        print("  ", " ".join(
            f"\033[92m{t}\033[0m" if l == "B-FOOD" else
            f"\033[96m{t}\033[0m" if l == "I-FOOD" else t
            for t, l in pairs
        ))

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