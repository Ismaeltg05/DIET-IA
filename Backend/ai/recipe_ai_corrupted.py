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

# Import your actual AI model
try:
    from ai.recipe_ai import RecipeSimilarityAI
except ImportError as e:
    logging.error(f"Failed to import RecipeSimilarityAI: {e}")
    RecipeSimilarityAI = None

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables with defaults
KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
HBASE_HOST = os.getenv('HBASE_HOST', 'hbase')
HBASE_PORT = int(os.getenv('HBASE_PORT', 9090))
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017/diet-ia')
SPARK_MASTER = os.getenv('SPARK_MASTER', 'spark://spark-master:7077')

# FastAPI app with route prefix
app = FastAPI(
    title="DIET-IA Backend",
    description="AI-powered recipe recommendation with Kafka, HBase, and Spark",
    version="1.0.0"
)

# Initialize AI model with actual implementation
if RecipeSimilarityAI:
    try:
        ai = RecipeSimilarityAI()
        logger.info("✓ RecipeSimilarityAI loaded successfully with real model")
    except Exception as e:
        logger.error(f"✗ Error initializing RecipeSimilarityAI: {e}")
        ai = None
else:
    ai = None
    logger.warning("RecipeSimilarityAI not available")

# --- KAFKA PRODUCER INITIALIZATION ---

def wait_for_kafka(bootstrap_servers, max_retries=10, retry_delay=2):
    """Wait for Kafka broker to be available"""
    admin = AdminClient({'bootstrap.servers': bootstrap_servers})
    for attempt in range(max_retries):
        try:
            # Try to list topics - this verifies Kafka is ready
            admin.list_topics(timeout=5)
            logger.info("✓ Kafka is ready")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Kafka not ready (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {retry_delay}s... {str(e)[:50]}"
                )
                time.sleep(retry_delay)
    logger.error("✗ Kafka failed to initialize after max retries")
    return False

producer = None

@app.on_event("startup")
async def startup_event():
    """Initialize Kafka producer on startup"""
    global producer
    
    # Wait for Kafka to be ready
    if wait_for_kafka(KAFKA_BOOTSTRAP):
        try:
            kafka_config = {
                'bootstrap.servers': KAFKA_BOOTSTRAP,
                'client.id': 'diet-ia-backend'
            }
            producer = Producer(kafka_config)
            logger.info("✓ Kafka Producer initialized")
        except Exception as e:
            logger.error(f"✗ Failed to create Kafka Producer: {e}")
            producer = None
    else:
        logger.error("✗ Skipping Kafka Producer initialization - broker unavailable")
        producer = None

# --- HBASE CONNECTION HELPER ---

def get_hbase_table(table_name='user_preferences'):
    """Get HBase table connection with error handling"""
    try:
        connection = happybase.Connection(
            HBASE_HOST, 
            port=HBASE_PORT, 
            timeout=5000
        )
        table = connection.table(table_name)
        return table
    except Exception as e:
        logger.error(f"✗ HBase connection error ({HBASE_HOST}:{HBASE_PORT}): {e}")
        return None

# --- PYDANTIC MODELS ---

class IngredientsRequest(BaseModel):
    """Request model for recipe recommendation"""
    ingredients: List[str]
    user_id: Optional[str] = "guest"
    top_k: Optional[int] = 1

class RatingRequest(BaseModel):
    """Request model for recipe rating"""
    user_id: str
    recipe_id: str
    rating: int

class UserPrefs(BaseModel):
    """Request model for user preferences"""
    preferences: dict

# --- SPARK BACKGROUND JOB ---

def run_spark_job():
    """Execute batch processing of recipes on Spark cluster"""
    try:
        spark = SparkSession.builder \
            .appName("DIET-IA-Batch-Processing") \
            .master(SPARK_MASTER) \
            .config("spark.mongodb.read.connection.uri", f"{MONGO_URI}") \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.1.1") \
            .getOrCreate()
        
        # Example: Process recipes from MongoDB
        df = spark.read.format("mongodb").load()
        recipe_count = df.count()
        logger.info(f"✓ Spark processed {recipe_count} recipes")
        
        spark.stop()
    except Exception as e:
        logger.error(f"✗ Spark job error: {e}")

# --- API ENDPOINTS ---

@app.get("/")
def root():
    """Health check and service info"""
    return {
        "status": "online",
        "project": "DIET-IA",
        "version": "1.0.0",
        "infrastructure": ["MongoDB", "HBase", "Kafka", "Spark"],
        "ai_model": "RecipeSimilarityAI (Real)",
        "docs": "/docs"
    }

@app.post("/api/ai/recommend")
def recommend(data: IngredientsRequest):
    """
    Recommend recipes based on ingredients using your actual AI model.
    
    Your RecipeSimilarityAI will:
    1. Normalize ingredients
    2. Create embeddings
    3. Find similar recipes in the dataset
    4. Return top recommendations with similarity scores
    
    Checks user dietary restrictions from HBase (e.g., lactose intolerance),
    then uses AI model to find best matching recipes.
    """
    try:
        if not ai:
            raise HTTPException(
                status_code=503, 
                detail="AI model not loaded. Check recipe_ai.py and dataset are available"
            )
        
        if not data.ingredients:
            raise HTTPException(
                status_code=400,
                detail="At least one ingredient is required"
            )
        
        # 1. Check user dietary restrictions from HBase
        dietary_restrictions = {}
        table = get_hbase_table()
        if table:
            try:
                row = table.row(data.user_id.encode())
                if row:
                    dietary_restrictions = {
                        k.decode().replace('cf:', ''): v.decode() 
                        for k, v in row.items()
                    }
                    logger.info(f"User {data.user_id} dietary restrictions: {dietary_restrictions}")
            except Exception as e:
                logger.warning(f"Could not fetch HBase preferences: {e}")
        
        # 2. Get AI recommendations using your real model
        try:
            recommendations = ai.recommend_best_recipe(
                ingredients=data.ingredients,
                top_k=data.top_k or 1
            )
            
            # Handle both single recipe and list responses
            if isinstance(recommendations, list):
                recipes = recommendations
            else:
                recipes = [recommendations]
            
            # 3. Filter by dietary restrictions if specified
            filtered_recipes = []
            for recipe in recipes:
                # Check dietary restrictions
                if dietary_restrictions:
                    # Example: if user is lactose intolerant
                    if dietary_restrictions.get('lactose_intolerant') == 'true':
                        if recipe.get('recipe', {}).get('contains_lactose', False):
                            logger.info(f"Skipping {recipe.get('Title')} - contains lactose")
                            continue
                    
                    # Check for other dietary restrictions
                    if dietary_restrictions.get('gluten_free') == 'true':
                        if recipe.get('recipe', {}).get('contains_gluten', False):
                            logger.info(f"Skipping {recipe.get('Title')} - contains gluten")
                            continue
                    
                    if dietary_restrictions.get('vegetarian') == 'true':
                        if not recipe.get('recipe', {}).get('is_vegetarian', False):
                            logger.info(f"Skipping {recipe.get('Title')} - not vegetarian")
                            continue
                
                filtered_recipes.append(recipe)
            
            # If all recipes were filtered, return best match with warning
            if not filtered_recipes and recipes:
                logger.warning(f"No recipes matched dietary restrictions, returning best match")
                filtered_recipes = recipes[:1]
            
            if not filtered_recipes:
                raise HTTPException(
                    status_code=404,
                    detail="No recipes found matching the ingredients and dietary restrictions"
                )
            
            # 4. Format response
            if data.top_k == 1:
                recipe = filtered_recipes[0]
                response = {
                    "status": "success",
                    "recipe_id": recipe.get('Title', 'unknown'),
                    "title": recipe.get('Title', ''),
                    "ingredients": recipe.get('Ingredients', []),
                    "tags": recipe.get('Tags', []),
                    "instructions": recipe.get('Instructions', ''),
                    "similarity_score": recipe.get('similarity', 0.0),
                    "similarity_percent": recipe.get('similarity_percent', 0.0),
                    "dietary_info": recipe.get('recipe', {}).get('dietary_summary', []),
                    "contains_lactose": recipe.get('recipe', {}).get('contains_lactose', False),
                    "contains_gluten": recipe.get('recipe', {}).get('contains_gluten', False),
                    "is_vegetarian": recipe.get('recipe', {}).get('is_vegetarian', False),
                    "user_id": data.user_id,
                    "matched_dietary_restrictions": bool(dietary_restrictions)
                }
            else:
                response = {
                    "status": "success",
                    "recommendations": [
                        {
                            "recipe_id": r.get('Title', 'unknown'),
                            "title": r.get('Title', ''),
                            "ingredients": r.get('Ingredients', []),
                            "tags": r.get('Tags', []),
                            "similarity_score": r.get('similarity', 0.0),
                            "similarity_percent": r.get('similarity_percent', 0.0),
                            "dietary_info": r.get('recipe', {}).get('dietary_summary', []),
                        }
                        for r in filtered_recipes
                    ],
                    "total_recommendations": len(filtered_recipes),
                    "user_id": data.user_id,
                    "matched_dietary_restrictions": bool(dietary_restrictions)
                }
            
            logger.info(f"✓ Recommendation(s) provided for user {data.user_id} with ingredients: {data.ingredients}")
            return response
        
        except ValueError as e:
            logger.error(f"AI model error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@app.post("/api/ai/batch-process")
def batch_process(background_tasks: BackgroundTasks):
    """
    Submit Spark batch job without blocking the API.
    Processes all recipes in MongoDB asynchronously.
    """
    try:
        background_tasks.add_task(run_spark_job)
        return {
            "status": "success",
            "message": "Spark batch job submitted to cluster",
            "job_id": "batch-spark-async"
        }
    except Exception as e:
        logger.error(f"✗ Failed to submit batch job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/rate-recipe")
def rate_recipe(data: RatingRequest):
    """
    Submit recipe rating to Kafka for asynchronous processing.
    Ratings are collected for model retraining and analytics.
    """
    if not producer:
        raise HTTPException(
            status_code=503, 
            detail="Kafka is unavailable. Ratings cannot be processed."
        )
    
    try:
        message = json.dumps(data.model_dump()).encode('utf-8')
        producer.produce('recipe_ratings', message)
        producer.flush(timeout=5)
        
        logger.info(f"✓ Rating submitted: user={data.user_id}, recipe={data.recipe_id}, rating={data.rating}")
        return {
            "status": "success",
            "message": "Rating queued in Kafka",
            "recipe_id": data.recipe_id
        }
    except Exception as e:
        logger.error(f"✗ Rating submission error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit rating: {str(e)}")

@app.get("/api/ai/user-preferences/{user_id}")
def get_preferences(user_id: str):
    """
    Retrieve user dietary preferences and restrictions from HBase.
    Returns lactose intolerance, allergies, vegetarian status, etc.
    """
    table = get_hbase_table()
    if not table:
        raise HTTPException(status_code=503, detail="HBase connection failed")
    
    try:
        row = table.row(user_id.encode())
        if not row:
            return {"user_id": user_id, "preferences": {}, "found": False}
        
        preferences = {
            k.decode().replace('cf:', ''): v.decode() 
            for k, v in row.items()
        }
        
        return {
            "user_id": user_id, 
            "preferences": preferences,
            "found": True
        }
    except Exception as e:
        logger.error(f"✗ Failed to fetch preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/user-preferences/{user_id}")
def save_preferences(user_id: str, data: UserPrefs):
    """
    Save user dietary preferences and restrictions to HBase.
    
    Example request body:
    {
        "preferences": {
            "lactose_intolerant": "true",
            "gluten_free": "false",
            "vegetarian": "true",
            "vegan": "false"
        }
    }
    """
    table = get_hbase_table()
    if not table:
        raise HTTPException(status_code=503, detail="HBase connection failed")
    
    try:
        # Format data for HBase (column family: cf)
        formatted_data = {
            f"cf:{k}".encode(): str(v).encode() 
            for k, v in data.preferences.items()
        }
        
        table.put(user_id.encode(), formatted_data)
        logger.info(f"✓ Preferences saved for user {user_id}: {data.preferences}")
        
        return {
            "status": "success",
            "message": "Preferences persisted in HBase",
            "user_id": user_id,
            "preferences_saved": data.preferences
        }
    except Exception as e:
        logger.error(f"✗ Failed to save preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/ingredients-stats")
def ingredients_stats():
    """
    Get global ingredient statistics.
    Returns top ingredients from your dataset.
    """
    try:
        if not ai or not ai.recipes is not None:
            return {
                "status": "success",
                "message": "Statistics not available",
                "total_recipes": 0
            }
        
        # Count ingredient frequency from loaded recipes
        ingredient_freq = {}
        for ingredients_str in ai.recipes.get("Features", []):
            if ingredients_str:
                for ing in str(ingredients_str).split():
                    ingredient_freq[ing] = ingredient_freq.get(ing, 0) + 1
        
        # Get top 10 ingredients
        top_ingredients = sorted(
            ingredient_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "status": "success",
            "total_recipes": len(ai.recipes),
            "top_ingredients": [
                {"ingredient": ing, "frequency": freq}
                for ing, freq in top_ingredients
            ],
            "aggregation_method": "Dataset analysis",
            "last_update": "On application startup"
        }
    except Exception as e:
        logger.error(f"✗ Failed to fetch stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/explain/{recipe_title}")
def explain_match(recipe_title: str):
    """
    Get explanation of why a recipe matches certain ingredients.
    Uses your AI model's explain_match method.
    """
    try:
        if not ai:
            raise HTTPException(status_code=503, detail="AI model not loaded")
        
        # Search for recipe with similar title
        matching_recipes = ai.recipes[
            ai.recipes['Title'].str.lower().str.contains(recipe_title.lower(), na=False)
        ]
        
        if matching_recipes.empty:
            raise HTTPException(status_code=404, detail=f"Recipe '{recipe_title}' not found")
        
        recipe = matching_recipes.iloc[0]
        
        return {
            "status": "success",
            "recipe_title": recipe.get('Title', ''),
            "ingredients": recipe.get('Ingredients', '') if isinstance(recipe.get('Ingredients'), str) else ' '.join(recipe.get('Ingredients', [])),
            "tags": recipe.get('Category', '') if isinstance(recipe.get('Category'), str) else ' '.join(recipe.get('Category', [])),
            "instructions": recipe.get('Instructions', ''),
            "dietary_info": recipe.get('dietary_summary', []) if 'dietary_summary' in recipe else []
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Failed to explain match: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional health check endpoint
@app.get("/api/ai/health")
def health_check():
    """Detailed health check of all dependencies"""
    health_status = {
        "overall": "healthy",
        "services": {},
        "ai_model": "not_loaded"
    }
    
    # Check AI model
    if ai:
        try:
            # Test that the model has loaded recipes
            recipe_count = len(ai.recipes) if hasattr(ai, 'recipes') else 0
            if recipe_count > 0:
                health_status["ai_model"] = f"loaded ({recipe_count} recipes)"
            else:
                health_status["ai_model"] = "loaded (0 recipes)"
        except:
            health_status["ai_model"] = "error"
    
    # Check Kafka
    health_status["services"]["kafka"] = "ready" if producer else "unavailable"
    
    # Check HBase
    try:
        table = get_hbase_table()
        health_status["services"]["hbase"] = "connected" if table else "failed"
    except:
        health_status["services"]["hbase"] = "unavailable"
    
    # Set overall status
    service_statuses = [
        health_status["ai_model"] in ["loaded (0 recipes)", "loaded ("] or health_status["ai_model"].startswith("loaded"),
        health_status["services"]["kafka"] == "ready",
        health_status["services"]["hbase"] == "connected"
    ]
    
    if not any(service_statuses):
        health_status["overall"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
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