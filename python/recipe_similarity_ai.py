import ast
import re
import math
import os
from typing import Iterable, List, Optional, Sequence
import math

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


def _to_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("[") or stripped.startswith("("):
            try:
                parsed = ast.literal_eval(stripped)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return [value]
    return []


def _join_ingredients(value) -> str:
    if isinstance(value, str):
        parts = [part.strip() for part in value.replace("|", ",").split(",") if part.strip()]
        return " ".join(parts)
    if isinstance(value, list):
        return " ".join(str(item).strip() for item in value if str(item).strip())
    return ""


def _split_pipe_values(value) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return []
    parts = [part.strip() for part in text.split("|") if part.strip()]
    return parts if parts else [text]


def _split_ingredients_text(value: str) -> List[str]:
    """Try to split an ingredients block into individual ingredient lines.

    Handles pipes, newlines, and commas (when they look like separators).
    """
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []

    # First split by pipe or newline
    if "|" in text:
        parts = [p.strip() for p in text.split("|") if p.strip()]
        return parts
    if "\n" in text:
        parts = [p.strip() for p in text.splitlines() if p.strip()]
        return parts

    # Fallback: split by commas but avoid splitting long sentences that are likely instructions
    # If there's a pattern like '1 cup' or measurement, it's likely an ingredient list using commas
    if re.search(r"\d+\s*(cup|tablespoon|teaspoon|tbsp|tsp|ounce|oz|gram|g|kg|ml|liter|l)", text, re.IGNORECASE):
        parts = [p.strip() for p in re.split(r",\s*(?=[^,])", text) if p.strip()]
        return parts

    # Last resort: return the whole text as single item
    return [text]


def _split_into_steps(text: str) -> List[str]:
    """Split instruction text into ordered steps.

    Tries, in order: pipe, numbered lists (1., 1)), newlines, sentence splitting.
    """
    if not text:
        return []
    s = str(text).strip()

    # 1) Pipe-separated
    if "|" in s:
        parts = [p.strip() for p in s.split("|") if p.strip()]
        if len(parts) > 1:
            return parts

    # 2) Numbered steps like '1. Do this 2. Do that' or '1) ...'
    numbered = re.split(r"\n\s*\d+[\.)]\s+", "\n" + s)
    numbered = [p.strip() for p in numbered if p.strip()]
    if len(numbered) > 1:
        return numbered

    # 3) Newlines
    if "\n" in s:
        parts = [p.strip() for p in s.splitlines() if p.strip()]
        if len(parts) > 1:
            return parts

    # 4) Split into sentences by punctuation, keep reasonably long sentences as steps
    sentences = re.split(r"(?<=[.!?])\s+", s)
    sentences = [p.strip() for p in sentences if len(p.strip()) > 10]
    if len(sentences) > 1:
        return sentences

    # otherwise return as single-step (trimmed)
    return [s]


class RecipeSimilarityAI:
    def __init__(
        self,
        base_dir: Optional[str] = None,
        model_dir: Optional[str] = None,
        dataset_path: Optional[str] = None,
    ) -> None:
        self.base_dir = base_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.model_dir = model_dir or os.path.join(self.base_dir, "models")
        self.dataset_path = dataset_path or self._resolve_dataset_path()

        self.embedder = self._load_embedder()
        self.recipes = self._load_recipes()
        self.recipe_embeddings = self._build_recipe_embeddings()

    def _resolve_dataset_path(self) -> str:
        processed_candidates = [
            os.path.join(self.model_dir, "df_recetas_processed.csv"),
            os.path.join(self.base_dir, "datasets", "df_recetas_processed.csv"),
            os.path.join(self.base_dir, "datasets", "RAW_recipes.csv"),
        ]
        for candidate in processed_candidates:
            if os.path.exists(candidate):
                return candidate
        raise FileNotFoundError("No se encontró un dataset de recetas procesado ni RAW_recipes.csv.")

    def _load_embedder(self) -> SentenceTransformer:
        embedder_candidates = [
            os.path.join(self.model_dir, "embedder"),
            os.path.join(self.base_dir, "models", "embedder"),
        ]
        for candidate in embedder_candidates:
            if os.path.exists(candidate):
                return SentenceTransformer(candidate)
        return SentenceTransformer("all-MiniLM-L6-v2")

    def _load_recipes(self) -> pd.DataFrame:
        df = pd.read_csv(self.dataset_path)

        rename_map = {
            "title": "Title",
            "name": "Title",
            "ingredients": "Ingredients",
            "steps": "Instructions",
            "directions": "Instructions",
            "categories": "Category",
        }
        df = df.rename(columns={key: value for key, value in rename_map.items() if key in df.columns})

        if "Title" not in df.columns or "Ingredients" not in df.columns:
            raise ValueError("El dataset no contiene las columnas necesarias: Title e Ingredients.")

        if "Instructions" not in df.columns:
            df["Instructions"] = ""

        if "Category" not in df.columns:
            df["Category"] = ""

        df["IngredientsRaw"] = df["Ingredients"]
        df["InstructionsRaw"] = df["Instructions"]
        df["CategoryRaw"] = df["Category"]

        df["Title"] = df["Title"].astype(str)
        df["Ingredients"] = df["Ingredients"].apply(_to_list).apply(_join_ingredients)
        df["Instructions"] = df["Instructions"].apply(_to_list).apply(
            lambda value: " | ".join(value) if isinstance(value, list) else str(value)
        )

        if "Features" not in df.columns:
            df["Features"] = df["Ingredients"]
        else:
            df["Features"] = df["Features"].fillna("").astype(str)
            empty_features = df["Features"].str.strip() == ""
            df.loc[empty_features, "Features"] = df.loc[empty_features, "Ingredients"]

        df = df.dropna(subset=["Title", "Features"]).reset_index(drop=True)
        df = df[df["Title"].str.strip() != ""]
        df = df[df["Features"].str.strip() != ""]
        return df

    def _build_recipe_embeddings(self) -> np.ndarray:
        features = self.recipes["Features"].tolist()
        embeddings = self.embedder.encode(
            features,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def _normalize_ingredients(self, ingredients: Sequence[str]) -> List[str]:
        normalized = []
        for ingredient in ingredients:
            if not ingredient:
                continue
            ingredient_text = str(ingredient).strip().lower()
            if ingredient_text:
                normalized.append(ingredient_text)
        seen = set()
        unique = []
        for ingredient in normalized:
            if ingredient not in seen:
                seen.add(ingredient)
                unique.append(ingredient)
        return unique

    def _build_recipe_payload(self, row: pd.Series, score: float) -> dict:
        recipe = row.to_dict()
        ingredients_raw = recipe.get("IngredientsRaw", recipe.get("Ingredients", ""))
        ingredients_lines = _split_ingredients_text(ingredients_raw)
        ingredients_list = self._normalize_ingredients(ingredients_lines)
        tags = _split_pipe_values(recipe.get("CategoryRaw", recipe.get("Category", "")))

        recipe["IngredientsList"] = ingredients_list
        recipe["Tags"] = tags
        recipe["SimilarityScore"] = float(score)
        recipe["SimilarityPercent"] = round(max(0.0, float(score)) * 100.0, 2)
        # Steps parsed from InstructionsRaw (pipe-separated) or Instructions
        steps_raw = recipe.get("InstructionsRaw", recipe.get("Instructions", ""))
        steps = _split_into_steps(steps_raw)
        recipe["Steps"] = steps

        # Dietary heuristics
        joined_ings = " ".join(ingredients_list).lower()
        tags_lower = [t.lower() for t in tags]

        lactose_kw = {"milk", "cream", "butter", "cheese", "yogurt", "sour cream", "ricotta", "parmesan", "mozzarella", "custard", "evaporated milk", "condensed milk", "buttermilk"}
        gluten_kw = {"flour", "wheat", "bread", "pasta", "barley", "rye", "breadcrumbs", "cracker", "cake", "biscuit", "muffin", "semolina", "spaghetti"}
        meat_kw = {"chicken", "beef", "pork", "lamb", "bacon", "ham", "salmon", "tuna", "shrimp", "fish", "seafood"}

        contains_lactose = any(k in joined_ings for k in lactose_kw) or any("dairy" in t or "milk" in t for t in tags_lower)
        contains_gluten = any(k in joined_ings for k in gluten_kw) or any("wheat" in t or "gluten" in t for t in tags_lower)

        # Calories / Fat heuristics
        def _safe_float(v):
            try:
                return float(v)
            except Exception:
                return None

        calories = _safe_float(recipe.get("Calories") or recipe.get("calories"))
        fat = _safe_float(recipe.get("Fat") or recipe.get("fat"))

        low_calories = False
        if calories is not None:
            low_calories = calories <= 300

        low_fat = False
        if fat is not None:
            low_fat = fat <= 10

        # Vegetarian: if no obvious meat keywords in ingredients or tags
        joined_tags = " ".join(tags_lower)
        is_vegetarian = not any(m in joined_ings for m in meat_kw) and not any(m in joined_tags for m in meat_kw)

        recipe["contains_lactose"] = bool(contains_lactose)
        recipe["contains_gluten"] = bool(contains_gluten)
        recipe["low_calories"] = bool(low_calories)
        recipe["low_fat"] = bool(low_fat)
        recipe["is_vegetarian"] = bool(is_vegetarian)

        # Short dietary summary
        dietary = []
        dietary.append("lactose" if recipe["contains_lactose"] else "no-lactose")
        dietary.append("gluten" if recipe["contains_gluten"] else "no-gluten")
        if recipe["low_calories"]:
            dietary.append("low-calories")
        if recipe["low_fat"]:
            dietary.append("low-fat")
        if recipe["is_vegetarian"]:
            dietary.append("vegetarian")

        recipe["dietary_summary"] = dietary

        return recipe

    def recommend_best_recipe(self, ingredients: Sequence[str], top_k: int = 1):
        normalized_ingredients = self._normalize_ingredients(ingredients)
        if not normalized_ingredients:
            raise ValueError("Se requieren ingredientes para buscar una receta.")

        query_text = " ".join(normalized_ingredients)
        query_embedding = self.embedder.encode(
            [query_text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        scores = np.dot(self.recipe_embeddings, query_embedding)
        best_indices = np.argsort(-scores)[: max(1, top_k)]

        recommendations = []
        for index in best_indices:
            row = self.recipes.iloc[int(index)]
            score = float(scores[int(index)])
            recipe_payload = self._build_recipe_payload(row, score)
            recommendations.append(
                {
                    "Title": row.get("Title", ""),
                    "Ingredients": recipe_payload["IngredientsList"],
                    "Tags": recipe_payload["Tags"],
                    "Instructions": row.get("Instructions", ""),
                    "similarity": score,
                    "similarity_percent": recipe_payload["SimilarityPercent"],
                    "recipe": recipe_payload,
                }
            )

        return recommendations[0] if top_k == 1 else recommendations

    def explain_match(self, ingredients: Sequence[str]) -> str:
        recipe = self.recommend_best_recipe(ingredients, top_k=1)
        return (
            f"{recipe['Title']}\n"
            f"Similitud: {recipe['similarity_percent']:.2f}%\n"
            f"Ingredientes: {', '.join(recipe['Ingredients'])}\n"
            f"Tags: {', '.join(recipe['Tags'])}\n"
            f"Instrucciones: {recipe['Instructions']}"
        )


def ingredients_from_ner_output(items: Iterable) -> List[str]:
    normalized = []
    for item in items:
        if isinstance(item, (list, tuple)) and item:
            normalized.append(str(item[0]))
        elif isinstance(item, str):
            normalized.append(item)
    return normalized


if __name__ == "__main__":
    sample_ingredients = ["tomato", "olive oil", "onion"]
    ai = RecipeSimilarityAI()
    print(ai.explain_match(sample_ingredients))