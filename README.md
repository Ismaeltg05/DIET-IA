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

## 2. Fuentes de Datos Previstas

Para cumplir con los requisitos de variedad y volumen del dato, el sistema se alimentará de dos fuentes principales:

### A. Telemetría de Flota (Simulación IoT)
Se desarrollará un script en Python (generador de logs sintéticos) que simula el comportamiento de 100 taxis en circulación continua.
* **Formato:** JSON semiestructurado.
* **Datos generados:** `ID_Taxi`, `Latitud`, `Longitud`, `Estado` (Libre/Ocupado), `Velocidad`, `Timestamp`.
* **Velocidad:** Streaming continuo simulando tiempo real.

### B. Datos Meteorológicos (APIs Públicas)
Integración con APIs externas (ej. **OpenWeatherMap** o **AEMET**) para enriquecer el modelo.
* **Variables:** `Temperatura`, `Precipitación`, `Humedad`.

---

## 3. Arquitectura Técnica Detallada

La solución cubre todas las capas tecnológicas, desde el dato crudo hasta la interfaz de usuario:

### 3.1 Ingesta y Streaming
* **Tecnología:** **Apache Kafka**.
* **Función:** Buffer de entrada para recibir miles de datos GPS por segundo desde el simulador Python y enviarlos al sistema de procesamiento sin pérdida de información.

### 3.2 Almacenamiento (Persistencia Políglota)
* **HDFS (Hadoop):** Almacenamiento "frío" para logs históricos masivos (Data Lake).
* **MongoDB (NoSQL):** Almacenamiento "caliente". Base de datos operacional para guardar los resultados procesados y servir datos a la Web App.

### 3.3 Procesamiento y Análisis
* **Tecnología:** **Apache Spark (PySpark)**.
* **Tareas:** Limpieza de coordenadas, cálculo de velocidad media por calle y agregación de ventanas de tiempo para alimentar el modelo de IA.

### 3.4 Inteligencia Artificial (Backend IA)
* **Modelo:** Regresión/Clustering con **Scikit-learn** o **Spark MLlib**.
* **API de Inferencia:** Se encapsulará el modelo en una **API REST con FastAPI (Python)**.
    * *Endpoint:* `/api/predict/demand`.
    * *Función:* Recibe coordenadas y hora -> Devuelve probabilidad de demanda (0-100%).

### 3.5 Frontend y Experiencia de Usuario (Web App)
Se desarrollará una **Single Page Application (SPA)** para la interacción final:
* **Tecnología:** **React.js** (o Vue.js) + **Vite**.
* **Mapas:** Librería **Leaflet.js** (OpenStreetMap) para visualizar la flota y las zonas calientes.
* **Estilos:** **Tailwind CSS** para diseño responsivo (Mobile First).
* **Funcionalidad:**
    * *Vista Conductor:* Mapa con su ubicación y marcadores rojos en zonas de alta probabilidad de clientes.
    * *Vista Control:* Panel general con la ubicación de toda la flota.

### 3.6 Analítica de Negocio y Automatización
* **Power BI:** Conectado a MongoDB para dashboards estratégicos (ingresos mensuales, KPIs históricos).
* **n8n:** Orquestador de alertas. Si la demanda > 90% en una zona vacía, envía notificación a Telegram.

---

## 4. Diagrama de Arquitectura

El flujo de datos completo, desde el sensor hasta la pantalla del usuario:

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
