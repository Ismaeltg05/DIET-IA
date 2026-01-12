# Propuesta de Proyecto: Smart Taxi - Optimización de Flotas y Movilidad Urbana
**Curso de Especialización en Inteligencia Artificial y Big Data**

---

## 1. Definición del Problema y Objetivos

### 1.1 Descripción del Problema
En el contexto de las *Smart Cities*, la gestión ineficiente de flotas de transporte urbano genera un aumento de emisiones de CO2, congestión de tráfico y pérdidas económicas significativas debido a taxis que circulan vacíos buscando clientes sin rumbo fijo.

Actualmente, los sistemas tradicionales carecen de herramientas predictivas. **El problema central** a resolver es la incapacidad de anticipar la demanda en tiempo real. Este proyecto propone un sistema capaz de predecir en qué zonas de la ciudad habrá alta demanda en los próximos **30 minutos**, dirigiendo a los taxis hacia allí antes de que se genere la cola de espera.

### 1.2 Objetivos Generales
Desarrollar un sistema integral "Smart Taxi" que procese flujos de datos geoespaciales (GPS) y meteorológicos en tiempo real para optimizar la operativa de la flota, utilizando técnicas de Big Data, Inteligencia Artificial y automatización de procesos.

### 1.3 Objetivos Específicos
1.  **Ingesta y Procesamiento Masivo (Big Data):** Implementar una arquitectura capaz de procesar miles de registros por minuto (simulación IoT) mediante ingestión continua.
2.  **Predicción de Demanda (IA):** Entrenar y desplegar un Modelo de Regresión (Machine Learning) que cruce variables temporales y climáticas para estimar la probabilidad de clientes por zona.
3.  **Almacenamiento Híbrido (Cloud/NoSQL):** Gestionar grandes volúmenes de datos históricos (Data Lake) y utilizar bases de datos NoSQL para la operativa ágil.
4.  **Automatización y Visualización:** Crear mapas de calor en tiempo real y configurar alertas automáticas a conductores cuando se detecten picos de demanda.

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
* **Justificación:** La lluvia o el frío extremo son factores determinantes en el aumento de la demanda de taxis.
* **Datos extraídos:** `Temperatura`, `Precipitación`, `Humedad`.

---

## 3. Arquitectura Técnica Detallada

La solución sigue un enfoque de procesamiento distribuido para manejar la velocidad y volumen del dato, cubriendo todas las capas tecnológicas del curso:

### 3.1 Ingesta y Streaming
* **Tecnología:** **Apache Kafka** o **Apache Flume**.
* **Función:** Actúan como *buffer* de entrada para recibir miles de datos GPS por segundo desde el simulador Python y enviarlos al sistema sin pérdida de información.

### 3.2 Almacenamiento (Persistencia Políglota)
* **HDFS (Hadoop):** Almacenamiento "frío". Aquí se guardan los datos crudos (logs históricos de meses) para futuros reentrenamientos del modelo.
* **MongoDB (NoSQL):** Almacenamiento "caliente". Base de datos operacional para guardar la información de "Viajes Finalizados" (`Cliente`, `Tarifa`, `Origen`, `Destino`).
    * *Cumplimiento:* Satisface el requisito de base de datos documental para datos semiestructurados.
    * *Despliegue:* Preferiblemente en **AWS/Cloud** para justificar arquitecturas en la nube.

### 3.3 Procesamiento y Análisis
* **Tecnología:** **Apache Spark (PySpark)**.
* **Tareas:**
    * Limpieza de coordenadas erróneas o nulas.
    * Cálculo de velocidad media por calle para detectar congestión.
    * Agregación de datos (ej. *"Recuento de viajes iniciados en Zona Centro entre las 18:00 y 19:00"*).

### 3.4 Inteligencia Artificial (El cerebro del sistema)
* **Desarrollo del Modelo:** Uso de **Scikit-learn** o **Spark MLlib**.
    * *Tipo:* Modelo de Regresión.
    * *Input:* Hora, Día de la semana, Clima, Eventos locales.
    * *Output:* Predicción numérica de demanda por distrito.
* **Despliegue (Inferencia):** El modelo se expone a través de una API REST en Python (**FastAPI** o **Flask**).
    * *Caso de uso:* La app del taxista consulta la API y recibe: *"Vete a la zona Centro, probabilidad de cliente: Alta"*.

### 3.5 Visualización y Automatización (Explotación)
* **Dashboard:** Uso de **Power BI** o **Grafana** conectado a MongoDB.
    * Visualización de Mapas de Calor (Heatmaps) de zonas con alta demanda.
    * Gráficos de ingresos por franja horaria.
* **Automatización con n8n:**
    * *Flujo:* Si la predicción de demanda en una zona supera el **90%** y hay pocos taxis libres allí → **n8n** envía una alerta automática a un canal de Telegram de los conductores o un email al gestor de flota.

---

## 4. Diagrama de Arquitectura

El siguiente diagrama ilustra el flujo de datos desde la generación hasta la explotación final:

```mermaid
graph LR
    subgraph Fuentes
    A[Simulador Python GPS] -->|JSON Stream| B(Apache Kafka)
    W[API Clima] -.->|Enriquecimiento| C
    end

    subgraph Big Data & IA
    B -->|Ingesta| C{Apache Spark}
    C -->|ETL & Limpieza| C
    C -->|Modelo ML| C
    end

    subgraph Persistencia
    C -->|Raw Data| D[(HDFS)]
    C -->|Datos Procesados| E[(MongoDB)]
    end

    subgraph Explotación
    E -->|API Rest| F[Backend Python/FastAPI]
    F --> G[Power BI Dashboard]
    F --> H[n8n Automatización]
    end
