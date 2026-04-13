import random
import json
import re
from collections import Counter

# -------------------------
# INGREDIENTES
# -------------------------
# (usa tu lista completa aquí)
ingredients = [
  "fat buttermilk", "low-fat milk", "bean soup mix", 
  "milk", "cream", "fat cottage cheese", "lean ground beef", "steak sauce", "absinthe", 
  "active dry yeast", "adobo sauce", "adobo seasoning", "agar-agar", "agave nectar", 
  "aged cheddar cheese", "ajwain seed", "albacore tuna", "alcohol", "ale", 
  "alfalfa sprouts", "alfredo sauce", "all-purpose flour", "allspice", "almond extract", 
  "almond flour", "almond milk", "almonds", "amaranth flour", "amaretto liqueur", 
  "american cheese", "anchovy paste", "andes mints", "andouille sausage", "angel hair pasta", 
  "anise seed", "apple butter", "apple cider vinegar", "apple juice", "apple pie filling", 
  "apples", "applesauce", "apricot jam", "apricot preserves", "arborio rice", 
  "arctic char", "arrowroot", "artichoke hearts", "arugula", "asiago cheese", 
  "asparagus", "avocado", "avocado oil", "bacon", "bagel", "baguette", 
  "baked beans", "baking powder", "baking soda", "balsamic vinegar", "banana", 
  "barbecue sauce", "barley", "basil", "basmati rice", "bass fillets", 
  "bay leaf", "bay scallops", "bean sprouts", "beef", "beef broth", 
  "beef chuck roast", "beef gravy", "beef roast", "beef stock", "beef tenderloin", 
  "beer", "beets", "bell pepper", "bell peppers", "berries", "biscuits", 
  "black beans", "black pepper", "blackberries", "blackberries", "black-eyed peas", 
  "blue cheese", "blueberries", "blueberry pie filling", "bok choy", "bologna", 
  "boneless chicken breast", "boneless pork chops", "boneless skinless chicken breasts", 
  "boston lettuce", "bouillon cube", "bourbon", "bow tie pasta", "brandy", 
  "bratwurst", "breadcrumbs", "bread flour", "breeze almond milk", "brie cheese", 
  "brisket", "broccoli", "broccoli florets", "brown rice", "brown sugar", 
  "brussels sprouts", "buckwheat flour", "bulgur wheat", "butter", "buttermilk", 
  "butternut squash", "butterscotch chips", "cabbage", "caesar dressing", "cake flour", 
  "cake mix", "calamari", "candy melts", "canned pumpkin", "canned tomatoes", 
  "capers", "caramel sauce", "cardamom", "carrot", "cashews", "cauliflower", 
  "cayenne pepper", "celery", "celery seed", "cereal", "cheddar cheese", 
  "cheese", "cheez whiz", "cherries", "cherry pie filling", "chestnuts", 
  "chia seeds", "chicken", "chicken broth", "chicken breast", "chicken stock", 
  "chicken thighs", "chickpeas", "chile powder", "chili powder", "chili sauce", 
  "chives", "chocolate", "chocolate chips", "chocolate syrup", "chorizo", 
  "chow mein noodles", "cilantro", "cinnamon", "clams", "cocoa powder", 
  "coconut", "coconut milk", "cod fillets", "coffee", "cola", "colby cheese", 
  "condensed milk", "confectioners sugar", "cookies", "corn tortillas", "cornbread mix", 
  "corned beef", "cornflakes", "cornmeal", "cornstarch", "corn syrup", "couscous", 
  "crabmeat", "cranberries", "cranberry juice", "cranberry sauce", "cream", 
  "cream cheese", "creamy peanut butter", "crescent rolls", "crimini mushrooms", 
  "croissants", "crushed tomatoes", "cucumbers", "cumin", "cumin seed", "currants", 
  "curry powder", "custard powder", "dates", "delicata squash", "diced tomatoes", 
  "dijon mustard", "dill", "dill pickle", "ditalini pasta", "doughnuts", 
  "dry mustard", "dry sherry", "egg noodles", "egg substitute", "egg whites", 
  "eggplant", "eggs", "elbow macaroni", "english muffins", "enoki mushrooms", 
  "espresso", "evaporated milk", "extra virgin olive oil", "fennel", "feta cheese", 
  "fettuccine", "fiddlehead ferns", "figs", "filet mignon", "fish fillets", 
  "fish sauce", "flank steak", "flax seeds", "flour tortillas", "fontina cheese", 
  "french fries", "french onion soup mix", "fudge brownie mix", "fusilli pasta", 
  "garbanzo beans", "garlic", "garlic powder", "gelatin", "ginger", "ginger ale", 
  "gingersnaps", "gnocchi", "goat cheese", "gouda cheese", "grape jelly", 
  "grape leaves", "grapefruit", "gravy mix", "green beans", "green bell pepper", 
  "green chilies", "green onions", "green peas", "green tea", "ground beef", 
  "ground chicken", "ground cinnamon", "ground cumin", "ground ginger", "ground pork", 
  "ground turkey", "gruyere cheese", "guacamole", "halibut fillets", "ham", 
  "hamburger buns", "harissa", "hash browns", "hazelnuts", "heavy cream", 
  "heirloom tomatoes", "herbes de provence", "honey", "horseradish", "hot sauce", 
  "iceberg lettuce", "instant coffee", "instant pudding mix", "italian dressing", 
  "italian parsley", "italian sausage", "jalapeno peppers", "jams", "jasmine rice", 
  "jell-o", "juniper berries", "kale", "ketchup", "kidney beans", "kielbasa", 
  "kiwi fruit", "lasagna noodles", "leeks", "lemon juice", "lemongrass", 
  "lentils", "lettuce", "licorice", "lime juice", "linguine", "liquid smoke", 
  "lump crabmeat", "macaroni", "mango", "maple syrup", "marinara sauce", 
  "marsala wine", "marshmallows", "masa harina", "mayonnaise", "meatballs", 
  "meringue powder", "milk", "mirin", "molasses", "monterey jack cheese", 
  "mozzarella cheese", "mushrooms", "mustard", "navy beans", "noodles", 
  "nutmeg", "oatmeal", "oats", "okra", "olives", "onion", "onion powder", 
  "onions", "orange juice", "oreo cookies", "oregano", "orzo pasta", "oysters", 
  "pancake mix", "pancetta", "paprika", "parmesan cheese", "parsley", "pasta", 
  "peaches", "peanut butter", "peanuts", "pear", "peas", "pecans", "penne pasta", 
  "pepper", "peppercorns", "peppers", "pesto", "pickle relish", "pie crust", 
  "pineapple", "pineapple juice", "pinto beans", "pistachios", "pita bread", 
  "pizza crust", "plantains", "polenta", "pomegranate", "popcorn", "poppy seeds", 
  "pork chops", "pork loin", "pork ribs", "pork sausage", "pork shoulder", 
  "potato", "potatoes", "pretzels", "prosciutto", "prunes", "pumpkin puree", 
  "quinoa", "radishes", "raisins", "raspberries", "refried beans", "rhubarb", 
  "rice", "rice noodles", "ricotta cheese", "rigatoni", "ritz crackers", "romaine lettuce", 
  "rosemary", "rum", "russet potatoes", "rye bread", "saffron", "sage", 
  "salad greens", "salami", "salmon", "salsa", "salt", "sardines", "sausage", 
  "scallions", "scallops", "sea salt", "seafood stock", "sesame oil", "sesame seeds", 
  "shallots", "shellfish", "sherry", "shortbread cookies", "shortening", "shrimp", 
  "snow peas", "soda crackers", "sour cream", "soy sauce", "soybeans", "spinach", 
  "split peas", "spring onions", "squash", "squid", "steak", "strawberries", 
  "string beans", "stuffing mix", "sugar", "sun-dried tomatoes", "sundried tomato paste", 
  "sweet potatoes", "sweetened condensed milk", "swiss chard", "swiss cheese", 
  "syrup", "taco seasoning", "taco shells", "tahini", "tapioca", "tarragon", 
  "tea bags", "teriyaki sauce", "thyme", "tilapia fillets", "toffee bits", 
  "tofu", "tomato paste", "tomato sauce", "tomato soup", "tomatoes", "tortilla chips", 
  "tortillas", "trout", "tuna", "turkey", "turkey breast", "turnips", "vanilla extract", 
  "veal", "vegetable broth", "vegetable oil", "vinegar", "waffles", "walnuts", 
  "wasabi", "water chestnuts", "watercress", "wheat bread", "whipped cream", 
  "whipping cream", "white bread", "white chocolate", "white fish", "white rice", 
  "white vinegar", "white wine", "whole wheat flour", "whole wheat pasta", 
  "whole wheat tortillas", "wine", "wine vinegar", "worcestershire sauce", "yeast", 
  "yellow squash", "yogurt", "zucchini", "zucchini squash"
]

# -------------------------
# CONFIG
# -------------------------
N_SAMPLES = 60000
NEGATIVE_RATIO = 0.15   # 15% frases sin ingredientes (MUY IMPORTANTE)
MAX_INGS_PER_SAMPLE = 3

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
# BIO LABELING (ROBUSTO)
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

    # NEGATIVE SAMPLE (IMPORTANTE PARA F1 REAL)
    if not use_ingredients:
        text = random.choice(NEGATIVE_TEMPLATES)
        tokens = tokenize(text)
        labels = ["O"] * len(tokens)

        return {
            "tokens": tokens,
            "labels": labels
        }

    # POSITIVE SAMPLE
    ings = sample_ingredients()
    ing_text = format_ingredients(ings)

    template = random.choice(TEMPLATES)
    text = template.format(ings=ing_text)

    # ruido natural
    if random.random() < 0.7:
        text = add_noise(text)

    text = maybe_slang(text)

    tokens = tokenize(text)
    labels = bio_tag(tokens, ings)

    return {
        "tokens": tokens,
        "labels": labels
    }

# -------------------------
# DATASET
# -------------------------
def generate_dataset(n=N_SAMPLES):
    data = []

    for _ in range(n):
        data.append(generate_example())

    random.shuffle(data)
    return data

# -------------------------
# SPLIT MEJORADO
# -------------------------
def split(data):
    # shuffle ya hecho
    n = len(data)

    train_end = int(0.8 * n)
    val_end = int(0.9 * n)

    train = data[:train_end]
    val = data[train_end:val_end]
    test = data[val_end:]

    return train, val, test

# -------------------------
# VALIDACIÓN RÁPIDA
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