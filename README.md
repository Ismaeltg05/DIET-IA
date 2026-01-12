# Propuesta de Proyecto: Smart Taxi - Optimización de Flotas y Movilidad Urbana
**Curso de Especialización en Inteligencia Artificial y Big Data**

---

## 1. Definición del Problema y Objetivos

### 1.1 Descripción del Problema
En el contexto de las *Smart Cities*, la gestión ineficiente de flotas de transporte urbano genera un aumento de emisiones de CO2, congestión de tráfico y pérdidas económicas significativas debido a taxis que circulan vacíos buscando clientes sin rumbo fijo.

Actualmente, los sistemas tradicionales carecen de herramientas predictivas y de interfaces amigables para el conductor. **El problema central** a resolver es la incapacidad de anticipar la demanda en tiempo real y comunicarla eficazmente a la flota. Este proyecto propone un sistema capaz de predecir zonas de alta demanda y visualizarlas en una aplicación web interactiva para los conductores.

### 1.2 Objetivos Generales
Desarrollar un sistema integral "Smart Taxi" que procese flujos de datos geoespaciales (GPS) y meteorológicos en tiempo real para optimizar la operativa de la flota, utilizando técnicas de Big Data, Inteligencia Artificial, desarrollo Web y automatización.

### 1.3 Objetivos Específicos
1.  **Ingesta y Procesamiento Masivo:** Implementar una arquitectura capaz de procesar miles de registros por minuto (simulación IoT) mediante ingestión continua.
2.  **Predicción de Demanda (IA):** Entrenar un modelo de Regresión que cruce variables temporales y climáticas para estimar la probabilidad de clientes por zona.
3.  **Desarrollo Full Stack (Web App):** Crear una interfaz web interactiva (Frontend) que consuma una API propia para guiar a los conductores mediante mapas en tiempo real.
4.  **Almacenamiento Híbrido:** Gestionar datos históricos en HDFS (Data Lake) y datos operacionales en MongoDB.

---

## 2. Exploración del Estado del Arte

### 2.1 Contexto Actual de la Movilidad Urbana
La movilidad en las ciudades modernas atraviesa un cambio de paradigma impulsado por el IoT y la analítica de datos. Tradicionalmente, la operación de taxis se ha basado en la experiencia empírica del conductor, resultando en una alta tasa de kilómetros recorridos en vacío (40-50% del tiempo operativo según estudios del sector).

### 2.2 Soluciones Existentes y Competencia
El mercado está dominado por plataformas VTC (Uber, Cabify) que utilizan algoritmos propietarios de "Surge Pricing" y asignación inteligente. Estas soluciones son "Cajas Negras". Las flotas de taxis tradicionales carecen de herramientas abiertas que les permitan competir en eficiencia tecnológica.

### 2.3 Tecnologías Habilitadoras
El estado del arte permite ahora procesar flujos masivos a bajo coste mediante:
* **Procesamiento en Stream:** Herramientas como **Apache Kafka** y **Spark Streaming** han democratizado el procesamiento en tiempo real.
* **Machine Learning Geoespacial:** Modelos de regresión y Clustering se aplican para segmentar ciudades en zonas de demanda dinámica.

---

## 3. Alcance del Proyecto

### 3.1 Alcance Funcional (MVP)
El proyecto desarrollará un Producto Mínimo Viable que cubra:
1.  **Simulación de Entorno:** Generación de escenario con 100 taxis emitiendo datos GPS cada 2-5 segundos.
2.  **Motor de Predicción:** Inferencia de demanda futura (30 min) basada en histórico y clima.
3.  **Interfaz Operativa (Frontend):** Visualización de flota y "Zonas Calientes" (Heatmaps) en mapa real.
4.  **Alertas:** Notificaciones automáticas ante anomalías de servicio.

### 3.2 Alcance Técnico
* **Big Data:** Ingesta y procesamiento distribuido (Kafka, Spark).
* **Almacenamiento:** Arquitectura Lambda (HDFS + MongoDB).
* **Desarrollo Web:** API RESTful (FastAPI) y Cliente SPA (React).
* **DevOps:** Despliegue contenerizado (Docker).

### 3.3 Exclusiones y Limitaciones
* No se utilizará hardware real (sensores OBD/GPS) ni vehículos físicos; se usarán datos sintéticos.
* No se desarrollará la App de pasajero (usuario final), solo la del conductor/gestor.
* No se incluye pasarela de pagos ni navegación "turn-by-turn".

---

## 4. Fuentes de Datos Previstas

### A. Telemetría de Flota (Simulación IoT)
Script en Python (generador de logs sintéticos) que simula el comportamiento de 100 taxis.
* **Formato:** JSON semiestructurado.
* **Variables:** `ID_Taxi`, `Latitud`, `Longitud`, `Estado` (Libre/Ocupado), `Velocidad`, `Timestamp`.
* **Velocidad:** Streaming continuo simulando tiempo real.

### B. Datos Meteorológicos (APIs Públicas)
Integración con APIs externas (ej. **OpenWeatherMap** o **AEMET**) para enriquecer el modelo.
* **Justificación:** La lluvia o temperatura extrema afectan directamente a la demanda.
* **Variables:** `Temperatura`, `Precipitación`, `Humedad`.

---

## 5. Arquitectura Técnica Detallada

La solución cubre todas las capas tecnológicas, desde el dato crudo hasta la interfaz de usuario:

### 5.1 Ingesta y Streaming
* **Tecnología:** **Apache Kafka**.
* **Función:** Buffer de entrada de alta velocidad para recibir los datos GPS del simulador.

### 5.2 Almacenamiento (Persistencia Políglota)
* **HDFS (Hadoop):** Almacenamiento "frío" para logs históricos masivos (Data Lake).
* **MongoDB (NoSQL):** Almacenamiento "caliente". Base de datos operacional para servir datos a la Web App y guardar resultados procesados.

### 5.3 Procesamiento y Análisis
* **Tecnología:** **Apache Spark (PySpark)**.
* **Tareas:** Limpieza de coordenadas, cálculo de velocidad media y agregación de ventanas de tiempo para alimentar el modelo.

### 5.4 Inteligencia Artificial (Backend IA)
* **Modelo:** Regresión/Clustering con **Scikit-learn** o **Spark MLlib**.
* **API de Inferencia:** Se encapsulará el modelo en una **API REST con FastAPI (Python)**.
    * *Endpoint:* `/api/predict/demand`.
    * *Función:* Recibe coordenadas/hora -> Devuelve probabilidad de demanda.

### 5.5 Frontend y Experiencia de Usuario (Web App)
Se desarrollará una **Single Page Application (SPA)**:
* **Tecnología:** **React.js** + **Vite**.
* **Mapas:** Librería **Leaflet.js** para visualizar la flota y zonas calientes.
* **Estilos:** **Tailwind CSS**.
* **Funcionalidad:** Vista para el conductor (mapa con zonas rojas de alta demanda) y vista de control para el gestor.

### 5.6 Analítica de Negocio y Automatización
* **Power BI:** Dashboards estratégicos conectados a MongoDB.
* **n8n:** Orquestador de alertas (ej. Telegram si demanda > 90% y faltan coches).

---

## 6. Diagrama de Arquitectura

El flujo de datos completo, desde el sensor simulado hasta la pantalla del usuario:

```mermaid
graph LR
    subgraph Fuentes
        A["Simulador Python GPS"] -->|"JSON Stream"| B("Apache Kafka")
        W["API Clima"] -.->|"Enriquecimiento"| C
    end

    subgraph BigDataIA ["Big Data & IA"]
        B -->|"Ingesta"| C{"Apache Spark"}
        C -->|"ETL & Limpieza"| C
        C -->|"Modelo ML"| C
    end

    subgraph Persistencia
        C -->|"Raw Data"| D[("HDFS")]
        C -->|"Datos Procesados"| E[("MongoDB")]
    end

    subgraph BackendAPI ["Backend API"]
        E -->|"Query"| F["API REST (FastAPI)"]
    end

    subgraph Frontend ["Frontend & Explotación"]
        F -->|"JSON"| G["Web App (React + Leaflet)"]
        F -->|"JSON"| H["Power BI Dashboard"]
        F -->|"Trigger"| I["n8n Alertas"]
    end
```

---

# 7. Planificación y Fases de Desarrollo

Para garantizar el éxito del proyecto, el desarrollo se divide en **5 fases incrementales**, asegurando entregables funcionales en cada etapa.

---

## Fase 1: Infraestructura y Datos (Semanas 1-3)
**Objetivo:** Tener el entorno listo y los datos fluyendo.

* **Configuración de entorno:** Repositorio Git y `docker-compose` (Zookeeper, Kafka, Mongo, HDFS).
* **Simulación IoT:** Desarrollo del script Python (IoT Mock) para generar coordenadas aleatorias realistas.
* **Ingesta:** Creación del Topic Kafka y conexión del Producer.

## Fase 2: Procesamiento Big Data (Semanas 4-6)
**Objetivo:** Capturar los datos, limpiarlos y guardarlos.

* **Streaming:** Configuración de Spark Streaming para leer de Kafka.
* **Data Lake:** Guardado de histórico en HDFS (formato Parquet).
* **Pipeline ETL:** Limpieza y guardado de "Estado Actual" en MongoDB.

## Fase 3: Inteligencia Artificial (Semanas 7-9)
**Objetivo:** Darle capacidad predictiva al sistema.

* **Análisis:** Análisis Exploratorio (EDA) en Jupyter Notebooks.
* **Entrenamiento:** Modelo de Regresión con Scikit-learn/SparkML.
* **Despliegue de Modelo:** Serialización del modelo (`.pkl`) y pruebas de precisión.

## Fase 4: Desarrollo Full Stack (Semanas 10-12)
**Objetivo:** Hacer el sistema utilizable mediante la Web App.

* **Backend:** Crear API con FastAPI que cargue el modelo y exponga endpoints.
* **Frontend:** Configurar React + Vite e integrar Leaflet (Mapas).
* **Integración:** Conectar Frontend con API para visualizar marcadores y zonas de calor.

## Fase 5: Automatización y Cierre (Semanas 13-14)
**Objetivo:** Pulir el producto final.

* **Alertas:** Configurar n8n para alertas automáticas (Telegram).
* **Business Intelligence:** Crear Dashboard de KPIs en Power BI.
* **Documentación:** Redacción de memoria técnica y defensa.

---

## Cronograma del Proyecto (Gantt)

```mermaid
gantt
    title Cronograma - Smart Taxi (14 Semanas)
    dateFormat  YYYY-MM-DD
    axisFormat  Sem %W
    
    section Infraestructura
    Docker & Git                     :done,    d1, 2024-01-01, 7d
    Simulador Python                 :active,  d2, after d1, 7d
    Kafka & Ingesta                  :         d3, after d2, 7d
    
    %% ... resto del código igual ...
    section Big Data & ETL
    Spark & HDFS                     :         d4, after d3, 7d
    Pipeline ETL (Kafka->Mongo)      :         d5, after d4, 14d

    section IA & Modelo
    Análisis & Jupyter               :         d6, after d5, 7d
    Entrenamiento & API              :         d7, after d6, 14d

    section Web App
    Backend FastAPI                  :         d8, after d6, 10d
    Frontend React                   :         d9, after d8, 14d

    section Cierre
    Automatización & BI              :         d10, after d9, 7d
    Memoria & Defensa                :         d11, after d10, 7d
```
