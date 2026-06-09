from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from ai.recipe_ai import RecipeSimilarityAI

app = FastAPI(
    title="Diet-IA Backend",
    description="API de recomendación de recetas con IA",
    version="1.0.0"
)

print("=" * 60)
print("🍳 Inicializando Diet-IA Backend")
print("=" * 60)

ai = RecipeSimilarityAI()

print("=" * 60)
print("✅ Backend inicializado correctamente")
print("=" * 60)
print()


class IngredientsRequest(BaseModel):
    ingredients: List[str]


@app.get("/")
def root():
    return {
        "message": "Diet-IA API funcionando",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health():
    """Verifica que el backend está activo"""
    return {"status": "healthy", "model": "loaded"}


@app.post("/recommend")
def recommend(data: IngredientsRequest):
    """
    Recomienda una receta basada en ingredientes
    
    Request:
    ```json
    {
        "ingredients": ["tomate", "cebolla", "ajo"]
    }
    ```
    """
    try:
        recipe = ai.recommend_best_recipe(data.ingredients)
        return recipe
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))