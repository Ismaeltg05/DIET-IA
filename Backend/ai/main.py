from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from recipe_ai import RecipeSimilarityAI

app = FastAPI()

ai = RecipeSimilarityAI()


class IngredientsRequest(BaseModel):
    ingredients: List[str]


@app.get("/")
def root():
    return {"message": "IA recetas funcionando"}


@app.post("/recommend")
def recommend(data: IngredientsRequest):
    try:
        recipe = ai.recommend_best_recipe(data.ingredients)
        return recipe
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))