import json
import logging
import os
import threading
import time
from typing import Dict, List, Optional

import happybase
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient
from pyspark.sql import SparkSession

# Import your AI model (ensure ai/recipe_ai.py exists)
try:
    from ai.recipe_ai import RecipeSimilarityAI
except ImportError as e:
    logging.error(f"Failed to import RecipeSimilarityAI: {e}")
    RecipeSimilarityAI = None


"""
Backend AI service (FastAPI)
----------------------------
Proporciona endpoints que integran:
- Un motor AI (`RecipeSimilarityAI`) para recomendaciones.
- Almacenamiento de preferencias (HBase con fallback local).
- Envío de ratings mediante Kafka.
- Ejecución asíncrona de jobs Spark.

El servicio intenta cargar el AI model en background para evitar bloqueos
during startup; además incluye funciones de verificación de dependencias
y helpers para robustez en entornos distribuidos.

Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
"""

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

# Initialize AI model placeholder (actual initialization done on startup)
ai = None
ai_load_lock = threading.Lock()

# Fallback storage for user preferences when HBase is unavailable.
PREFERENCES_FALLBACK_STORE: Dict[str, Dict[str, str]] = {}

import asyncio

async def _init_ai_background():
    """Initialize the AI model in a background thread to avoid blocking import/startup.

    Usa `run_in_executor` para llamar al constructor de `RecipeSimilarityAI` sin
    bloquear el event loop. Esto es útil cuando el costoso `__init__` carga
    artefactos grandes desde disco.
    """
    global ai
    if not RecipeSimilarityAI:
        logger.warning("RecipeSimilarityAI not available")
        return
    try:
        loop = asyncio.get_running_loop()
        ai_instance = await loop.run_in_executor(None, RecipeSimilarityAI)
        ai = ai_instance
        logger.info("✓ RecipeSimilarityAI loaded successfully (background)")
    except Exception as e:
        logger.error(f"✗ Error initializing RecipeSimilarityAI: {e}")


def ensure_ai_loaded() -> bool:
    """Load AI model on-demand if it is not ready yet.

    Esto previene respuestas 503 temporales si la primera petición llega antes
    de que la inicialización en background haya terminado.
    """
    global ai

    if ai is not None:
        return True

    if not RecipeSimilarityAI:
        logger.error("RecipeSimilarityAI class is not available")
        return False

    with ai_load_lock:
        if ai is not None:
            return True

        try:
            logger.info("Loading RecipeSimilarityAI on-demand...")
            ai = RecipeSimilarityAI()
            logger.info("✓ RecipeSimilarityAI loaded successfully (on-demand)")
            return True
        except Exception as e:
            logger.error(f"✗ On-demand AI model load failed: {e}")
            return False


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

producer = None  # Kafka producer inicializado en el evento de arranque del servicio.

@app.on_event("startup")
async def startup_event():
    """Inicializa dependencias críticas cuando se inicia la aplicación."""
    global producer

    # 1. Verificamos que Kafka esté accesible antes de crear el productor.
    #    Si no lo está, el servicio sigue en marcha pero la ruta de ratings
    #    devolverá error 503 hasta que Kafka vuelva a estar disponible.
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

    # 2. Cargar el modelo AI en background para que la primera petición
    #    no sufra un bloqueo de cold start en el loop principal.
    try:
        await _init_ai_background()
    except Exception as e:
        logger.error(f"✗ Failed to schedule AI model initialization: {e}")

# --- HBASE CONNECTION HELPER ---

def get_hbase_table(table_name='user_preferences'):
    """Obtiene la conexión a la tabla de HBase y crea la tabla si no existe."""
    try:
        connection = happybase.Connection(
            HBASE_HOST,
            port=HBASE_PORT,
            timeout=5000
        )
        connection.open()

        existing_tables = {name.decode() for name in connection.tables()}
        if table_name not in existing_tables:
            connection.create_table(table_name, {'cf': dict()})
            logger.info(f"✓ HBase table created: {table_name}")

        table = connection.table(table_name)
        return table
    except Exception as e:
        logger.error(f"✗ HBase connection error ({HBASE_HOST}:{HBASE_PORT}): {e}")
        return None


def load_user_preferences(user_id: str) -> Dict[str, str]:
    """Lee las preferencias dietéticas del usuario desde HBase o fallback local."""
    table = get_hbase_table()

    if table:
        try:
            row = table.row(user_id.encode())
            if row:
                return {
                    k.decode().replace('cf:', ''): v.decode()
                    for k, v in row.items()
                }
        except Exception as e:
            logger.warning(f"Could not fetch HBase preferences for {user_id}: {e}")

    # Si HBase falla, devolvemos un fallback en memoria para mantener la funcionalidad.
    return PREFERENCES_FALLBACK_STORE.get(user_id, {})

# --- PYDANTIC MODELS ---

class IngredientsRequest(BaseModel):
    """Request model for recipe recommendation"""
    ingredients: List[str]
    user_id: Optional[str] = "guest"

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
        "docs": "/docs"
    }

@app.post("/api/ai/recommend")
def recommend(data: IngredientsRequest):
    """
    Recommend recipes based on ingredients.
    
    Checks user dietary restrictions from HBase (e.g., lactose intolerance),
    then uses AI model to find best matching recipe.
    """
    try:
        if not ai and not ensure_ai_loaded():
            raise HTTPException(
                status_code=503, 
                detail="AI model not loaded yet. Retry in a few seconds."
            )
        
        # 1. Check user dietary restrictions from HBase
        no_lactose = False
        lactose_free = False
        
        preferences = load_user_preferences(data.user_id)
        if preferences:
            no_lactose = str(preferences.get('lactose_intolerant', 'false')).lower() == "true"
            lactose_free = str(preferences.get('lactose_free', 'false')).lower() == "true"

            if no_lactose or lactose_free:
                logger.info(f"User {data.user_id} has lactose restrictions")
        
        # 2. Get AI recommendation
        recipe = ai.recommend_best_recipe(data.ingredients)
        
        # 3. Add metadata
        recipe['user_id'] = data.user_id
        recipe['lactose_free_required'] = no_lactose or lactose_free
        
        logger.info(f"✓ Recommended recipe: {recipe.get('recipe_id', 'unknown')} for user {data.user_id}")
        return recipe
        
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
    Returns lactose intolerance, allergies, etc.
    """
    try:
        preferences = load_user_preferences(user_id)

        return {
            "user_id": user_id,
            "preferences": preferences,
            "found": bool(preferences)
        }
    except Exception as e:
        logger.error(f"✗ Failed to fetch preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/user-preferences/{user_id}")
def save_preferences(user_id: str, data: UserPrefs):
    """
    Save user dietary preferences and restrictions to HBase.
    Example: {"preferences": {"lactose_intolerant": "true", "vegan": "false"}}
    """
    try:
        # Format data for HBase (column family: cf)
        formatted_data = {
            f"cf:{k}".encode(): str(v).encode() 
            for k, v in data.preferences.items()
        }

        # Keep a local fallback copy regardless of HBase status.
        PREFERENCES_FALLBACK_STORE[user_id] = {
            str(k): str(v) for k, v in data.preferences.items()
        }

        table = get_hbase_table()
        if table:
            try:
                table.put(user_id.encode(), formatted_data)
                logger.info(f"✓ Preferences saved for user {user_id} in HBase")
                return {
                    "status": "success",
                    "message": "Preferences persisted in HBase",
                    "user_id": user_id,
                    "storage": "hbase"
                }
            except Exception as hbase_error:
                logger.warning(f"HBase put failed for user {user_id}, using fallback: {hbase_error}")

        return {
            "status": "success",
            "message": "Preferences persisted in fallback storage",
            "user_id": user_id,
            "storage": "fallback"
        }
    except Exception as e:
        logger.error(f"✗ Failed to save preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/ingredients-stats")
def ingredients_stats():
    """
    Get global ingredient statistics aggregated by Spark.
    Returns top ingredients across all recipes.
    """
    try:
        # This would normally come from Spark processing results
        return {
            "status": "success",
            "top_ingredients": [
                {"name": "Oat Milk", "frequency": 342},
                {"name": "Spinach", "frequency": 298},
                {"name": "Tomato", "frequency": 267},
                {"name": "Chickpeas", "frequency": 245}
            ],
            "aggregation_method": "Spark batch processing",
            "last_update": "2024-01-15T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"✗ Failed to fetch stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional health check endpoint
@app.get("/api/ai/health")
def health_check():
    """Detailed health check of all dependencies"""
    health_status = {
        "overall": "healthy",
        "services": {}
    }
    
    # Check AI model
    health_status["services"]["ai_model"] = "loaded" if ai else "not_loaded"
    
    # Check Kafka
    health_status["services"]["kafka"] = "ready" if producer else "unavailable"
    
    # Check HBase
    try:
        table = get_hbase_table()
        health_status["services"]["hbase"] = "connected" if table else "failed"
    except:
        health_status["services"]["hbase"] = "unavailable"
    
    # Set overall status
    if not all(v == "available" or v == "connected" or v == "loaded" or v == "ready" 
               for v in health_status["services"].values()):
        health_status["overall"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)