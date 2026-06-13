import ast
import re
import math
import os
from typing import Iterable, List, Optional, Sequence

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
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []

    if "|" in text:
        return [p.strip() for p in text.split("|") if p.strip()]
    if "\n" in text:
        return [p.strip() for p in text.splitlines() if p.strip()]

    if re.search(r"\d+\s*(cup|tablespoon|teaspoon|tbsp|tsp|ounce|oz|gram|g|kg|ml|liter|l)", text, re.IGNORECASE):
        return [p.strip() for p in re.split(r",\s*(?=[^,])", text) if p.strip()]

    return [text]


def _split_into_steps(text: str) -> List[str]:
    if not text:
        return []
    s = str(text).strip()

    if "|" in s:
        parts = [p.strip() for p in s.split("|") if p.strip()]
        if len(parts) > 1:
            return parts

    numbered = re.split(r"\n\s*\d+[\.)]\s+", "\n" + s)
    numbered = [p.strip() for p in numbered if p.strip()]
    if len(numbered) > 1:
        return numbered

    if "\n" in s:
        parts = [p.strip() for p in s.splitlines() if p.strip()]
        if len(parts) > 1:
            return parts

    sentences = re.split(r"(?<=[.!?])\s+", s)
    sentences = [p.strip() for p in sentences if len(p.strip()) > 10]
    if len(sentences) > 1:
        return sentences

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
            os.path.join(self.base_dir, "datasets", "RAW_recipes.csv"),
            os.path.join(os.path.dirname(__file__), "..", "datasets", "RAW_recipes.csv"),
        ]
        for candidate in processed_candidates:
            if os.path.exists(candidate):
                return candidate
        raise FileNotFoundError("No se encontró un dataset de recetas en datasets/RAW_recipes.csv")

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

        # Normalizar nombres de columnas (quitar espacios y pasar a minúsculas)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Mapeo de nombres posibles a los nombres que espera la lógica de la clase
        # Mapeo de nombres posibles a los nombres que espera la lógica de la clase
        rename_map = {
            "nvmname": "Title",     # <--- AÑADE ESTA LÍNEA
            "title": "Title",
            "name": "Title",
            "ingredients": "Ingredients",
            "recipe_ingredients": "Ingredients",
            "steps": "Instructions",
            "directions": "Instructions",
            "instructions": "Instructions",
            "categories": "Category",
            "tags": "Category"
        }
        
        df = df.rename(columns=rename_map)

        # Validación obligatoria
        if "Title" not in df.columns or "Ingredients" not in df.columns:
            found_cols = df.columns.tolist()
            raise ValueError(
                f"El dataset no contiene las columnas necesarias. "
                f"Esperaba 'Title' e 'Ingredients', pero encontré: {found_cols}"
            )

        # Rellenar opcionales
        if "Instructions" not in df.columns:
            df["Instructions"] = ""
        if "Category" not in df.columns:
            df["Category"] = ""

        # Guardar versiones crudas para el payload
        df["IngredientsRaw"] = df["Ingredients"]
        df["InstructionsRaw"] = df["Instructions"]
        df["CategoryRaw"] = df["Category"]

        # Procesamiento de datos
        df["Title"] = df["Title"].astype(str)
        df["Ingredients"] = df["Ingredients"].apply(_to_list).apply(_join_ingredients)
        df["Instructions"] = df["Instructions"].apply(_to_list).apply(
            lambda value: " | ".join(value) if isinstance(value, list) else str(value)
        )

        # Generar Features para el embedding si no existen
        if "features" in df.columns:
             df = df.rename(columns={"features": "Features"})
        
        if "Features" not in df.columns:
            df["Features"] = df["Ingredients"]
        else:
            df["Features"] = df["Features"].fillna("").astype(str)
            empty_features = df["Features"].str.strip() == ""
            df.loc[empty_features, "Features"] = df.loc[empty_features, "Ingredients"]

        # Limpiar filas vacías
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
            text = str(ingredient).strip().lower()
            if text:
                normalized.append(text)
        
        unique = []
        seen = set()
        for item in normalized:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return unique

    def _build_recipe_payload(self, row: pd.Series, score: float) -> dict:
        recipe = row.to_dict()
        
        # Procesar ingredientes y pasos
        ingredients_raw = recipe.get("IngredientsRaw", recipe.get("Ingredients", ""))
        ingredients_list = self._normalize_ingredients(_split_ingredients_text(ingredients_raw))
        
        tags = _split_pipe_values(recipe.get("CategoryRaw", recipe.get("Category", "")))
        steps = _split_into_steps(recipe.get("InstructionsRaw", recipe.get("Instructions", "")))

        recipe["IngredientsList"] = ingredients_list
        recipe["Tags"] = tags
        recipe["SimilarityScore"] = float(score)
        recipe["SimilarityPercent"] = round(max(0.0, float(score)) * 100.0, 2)
        recipe["Steps"] = steps

        # Heurísticas dietéticas
        joined_ings = " ".join(ingredients_list).lower()
        tags_lower = [t.lower() for t in tags]

        lactose_kw = {"milk", "cream", "butter", "cheese", "yogurt", "sour cream", "ricotta"}
        gluten_kw = {"flour", "wheat", "bread", "pasta", "barley", "rye"}
        meat_kw = {"chicken", "beef", "pork", "lamb", "bacon", "ham", "fish", "seafood"}

        recipe["contains_lactose"] = any(k in joined_ings for k in lactose_kw) or any("dairy" in t for t in tags_lower)
        recipe["contains_gluten"] = any(k in joined_ings for k in gluten_kw) or any("gluten" in t for t in tags_lower)

        def _safe_float(v):
            try: return float(v)
            except: return None

        calories = _safe_float(recipe.get("calories"))
        fat = _safe_float(recipe.get("fat"))

        recipe["low_calories"] = calories <= 300 if calories is not None else False
        recipe["low_fat"] = fat <= 10 if fat is not None else False
        recipe["is_vegetarian"] = not any(m in joined_ings for m in meat_kw) and not any(m in " ".join(tags_lower) for m in meat_kw)

        # Resumen corto
        dietary = []
        dietary.append("lactose" if recipe["contains_lactose"] else "no-lactose")
        dietary.append("gluten" if recipe["contains_gluten"] else "no-gluten")
        if recipe["low_calories"]: dietary.append("low-calories")
        if recipe["is_vegetarian"]: dietary.append("vegetarian")
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
            recommendations.append({
                "Title": row.get("Title", ""),
                "Ingredients": recipe_payload["IngredientsList"],
                "Tags": recipe_payload["Tags"],
                "Instructions": row.get("Instructions", ""),
                "similarity": score,
                "similarity_percent": recipe_payload["SimilarityPercent"],
                "recipe": recipe_payload,
            })

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