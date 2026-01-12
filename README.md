# Propuesta de Proyecto: Smart Taxi - Optimización de Flotas y Movilidad Urbana
**Curso de Especialización en Inteligencia Artificial y Big Data**

---

## 1. Definición del Problema y Objetivos

### 1.1 Descripción del Problema
En el contexto de las *Smart Cities*, la gestión ineficiente de flotas de transporte urbano genera un aumento de emisiones de CO2, congestión de tráfico y pérdidas económicas significativas debid[...]

Actualmente, los sistemas tradicionales carecen de herramientas predictivas y de interfaces amigables para el conductor. **El problema central** a resolver es la incapacidad de anticipar la demanda en[...]

### 1.2 Objetivos Generales
Desarrollar un sistema integral "Smart Taxi" que procese flujos de datos geoespaciales (GPS) y meteorológicos en tiempo real para optimizar la operativa de la flota, utilizando técnicas de Big Data,[...]

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
* **Función:** Buffer de entrada para recibir miles de datos GPS por segundo desde el simulador Python y enviarlos al sistema de procesamiento.

### 3.2 Almacenamiento (Persistencia Políglota)
* **HDFS (Hadoop):** Almacenamiento "frío" para logs históricos masivos.
* **MongoDB (NoSQL):** Almacenamiento "caliente". Base de datos operacional para guardar los resultados procesados y servir datos a la Web App.

### 3.3 Procesamiento y Análisis
* **Tecnología:** **Apache Spark (PySpark)**.
* **Tareas:** Limpieza de coordenadas, cálculo de velocidad media y agregación de ventanas de tiempo para el modelo.

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
flowchart LR
  %% Fuentes
  subgraph Fuentes [Fuentes de datos]
    direction TB
    SIM[Simulador Python GPS<br/>(JSON Stream)]
    CLIM[APIs Clima<br/>(OpenWeatherMap / AEMET)]
    SIM -->|Stream JSON| KAF[Kakfa]
    CLIM -->|Enriquecimiento| ENR[Servicio de Enriquecimiento]
    ENR -->|Push / Pull| KAF
  end

  %% Procesamiento y ML
  subgraph Procesamiento [Big Data & IA]
    direction TB
    KAF --> SPK[Apache Spark (PySpark)]
    SPK -->|ETL / Limpieza / Agregación| SPK_PROC[Procesamiento (ventanas, features)]
    SPK_PROC --> ML[Modelo ML<br/>(Entrenamiento / Inferencia)]
  end

  %% Persistencia
  subgraph Persistencia [Persistencia]
    direction TB
    SPK_PROC -->|Raw data| HDFS[(HDFS - Data Lake)]
    SPK_PROC -->|Processed data / Features| MDB[(MongoDB - Operacional)]
    ML -->|Model results / Scores| MDB
  end

  %% Backend API
  subgraph Backend [API Backend]
    direction TB
    MDB --> API[API REST - FastAPI<br/>(/api/predict/demand)]
    ML -->|Modelo desplegado / artefactos| API
  end

  %% Consumidores / Frontend
  subgraph Consumidores [Frontend y Explotación]
    direction TB
    API --> WEB[Web App (React + Leaflet)]
    API --> PBI[Power BI Dashboards]
    API --> N8N[n8n - Orquestador de alertas]
    N8N -->|Alertas| TLG[Telegram / SMS]
  end

  %% Alineación visual
  classDef cluster fill:#f9f9f9,stroke:#ddd,stroke-width:1px;
  class Fuentes,Procesamiento,Persistencia,Backend,Consumidores cluster;
```
