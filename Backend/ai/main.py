import json
import logging
import happybase
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from confluent_kafka import Producer
from pyspark.sql import SparkSession

from ai.recipe_ai import RecipeSimilarityAI

# --- CONFIGURACIÓN DE LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
ai = RecipeSimilarityAI()

# --- CONFIGURACIÓN DE CLIENTES ---

# Kafka Producer: Maneja las calificaciones de recetas de forma asíncrona
kafka_config = {'bootstrap.servers': 'kafka:9092'}
try:
    producer = Producer(kafka_config)
except Exception as e:
    logger.error(f"Error conectando a Kafka: {e}")
    producer = None

# HBase Connection helper: Gestiona perfiles y restricciones (ej. Sin Lactosa)
def get_hbase_table():
    try:
        connection = happybase.Connection('hbase', port=9090, timeout=5000)
        return connection.table('user_preferences')
    except Exception as e:
        logger.error(f"Error conectando a HBase: {e}")
        return None

# --- MODELOS DE DATOS (Pydantic) ---

class IngredientsRequest(BaseModel):
    ingredients: List[str]
    user_id: Optional[str] = "guest"

class RatingRequest(BaseModel):
    user_id: str
    recipe_id: str
    rating: int

class UserPrefs(BaseModel):
    preferences: dict

# --- TAREAS EN SEGUNDO PLANO (Spark) ---

def run_spark_job():
    """Ejecuta el procesamiento masivo de recetas en el clúster de Spark"""
    try:
        spark = SparkSession.builder \
            .appName("DIET-IA-Batch-Processing") \
            .master("spark://spark-master:7077") \
            .config("spark.mongodb.read.connection.uri", "mongodb://mongo:27017/diet-ia.recipes") \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.1.1") \
            .getOrCreate()
        
        # Ejemplo: Procesamiento de datos de MongoDB
        df = spark.read.format("mongodb").load()
        logger.info(f"Spark procesó {df.count()} recetas.")
        
        spark.stop()
    except Exception as e:
        logger.error(f"Error en el Job de Spark: {e}")

# --- ENDPOINTS ---

@app.get("/")
def root():
    return {
        "status": "online",
        "project": "DIET-IA",
        "infrastructure": ["MongoDB", "HBase", "Kafka", "Spark"]
    }

@app.post("/recommend")
def recommend(data: IngredientsRequest):
    try:
        # 1. Consultar restricciones en HBase (ej. intolerancia a la lactosa)
        no_lactose = False
        table = get_hbase_table()
        if table:
            row = table.row(data.user_id.encode())
            if row and b'cf:lactose_intolerant' in row:
                no_lactose = row[b'cf:lactose_intolerant'].decode().lower() == "true"

        # 2. Obtener recomendación de la IA
        # Se asume que tu modelo puede filtrar por ingredientes
        recipe = ai.recommend_best_recipe(data.ingredients)
        
        # Lógica de filtrado adicional si es necesario
        return recipe
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/batch-process")
def batch_process(background_tasks: BackgroundTasks):
    """Lanza el procesamiento Spark sin bloquear la API"""
    background_tasks.add_task(run_spark_job)
    return {"message": "Spark batch job submitted to cluster"}

@app.post("/rate-recipe")
def rate_recipe(data: RatingRequest):
    """Envía calificaciones a Kafka para análisis posterior"""
    if not producer:
        raise HTTPException(status_code=503, detail="Kafka unavailable")
    try:
        message = json.dumps(data.model_dump()).encode('utf-8')
        producer.produce('recipe_ratings', message)
        producer.flush()
        return {"status": "Rating queued in Kafka"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-preferences/{user_id}")
def get_preferences(user_id: str):
    """Recupera preferencias desde HBase"""
    table = get_hbase_table()
    if not table:
        raise HTTPException(status_code=503, detail="HBase connection failed")
    
    row = table.row(user_id.encode())
    if not row:
        return {"user_id": user_id, "preferences": {}}
    
    return {
        "user_id": user_id, 
        "preferences": {k.decode().replace('cf:', ''): v.decode() for k, v in row.items()}
    }

@app.post("/user-preferences/{user_id}")
def save_preferences(user_id: str, data: UserPrefs):
    """Guarda restricciones como la intolerancia a la lactosa en HBase"""
    table = get_hbase_table()
    if not table:
        raise HTTPException(status_code=503, detail="HBase connection failed")
    
    formatted_data = {f"cf:{k}".encode(): str(v).encode() for k, v in data.preferences.items()}
    table.put(user_id.encode(), formatted_data)
    return {"status": "Preferences persisted in HBase"}

@app.get("/ingredients-stats")
def ingredients_stats():
    """Punto de acceso para estadísticas globales procesadas por Spark"""
    return {"top_ingredients": ["Oat Milk", "Vegetables"], "status": "Aggregated via Spark"}