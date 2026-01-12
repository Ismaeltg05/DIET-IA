# Propuesta de Proyecto: Smart Taxi - Optimización de Flotas y Predicción de Demanda

> **Nota:** Esta es una excelente elección. Encaja perfectamente con el ejemplo del documento sobre "Sistema de análisis del transporte urbano", pero adaptándolo a taxis le das un enfoque más comercial y de "Smart City" (optimización de demanda).

A continuación, la propuesta detallada que cumple con todos los requisitos: **Big Data, IA, Cloud/NoSQL y Automatización**.

---

## 1. El Problema
En una ciudad inteligente, los taxis circulan vacíos mucho tiempo buscando clientes. 

* **El objetivo:** Predecir en qué zonas de la ciudad habrá alta demanda en los próximos **30 minutos** para dirigir a los taxis allí antes de que los clientes esperen, además de detectar rutas congestionadas en tiempo real.

---

## 2. Arquitectura Técnica
Desglose de las tecnologías requeridas por el documento para este caso específico:

### A. Ingesta y Big Data (El flujo de datos)
* **Fuente de Datos (Simulación):** Script en Python que genera datos GPS simulados de 100 taxis.
    * *Datos:* `ID_Taxi`, `Latitud`, `Longitud`, `Estado` (Libre/Ocupado), `Velocidad`, `Timestamp`.
* **Ingesta en Streaming:** Uso de **Apache Kafka** o **Apache Flume** para recibir miles de datos por segundo y enviarlos al sistema.
* **Almacenamiento Masivo:** Los datos crudos (logs históricos de meses) se guardan en **HDFS** (Hadoop Distributed File System).

### B. Base de Datos NoSQL y Cloud (Requisito de Sistemas)
* **Base de Datos Operacional:** Uso de **MongoDB** para guardar la información de los "Viajes Finalizados" (`Cliente`, `Tarifa`, `Origen`, `Destino`, `Puntuación`).
    * *Cumplimiento:* Satisface el requisito de NoSQL para datos semiestructurados (JSON).
* **Nube (Opcional/Recomendado):** Despliegue de MongoDB o la visualización en **AWS** para justificar el uso de arquitecturas Cloud.

### C. Procesamiento y Análisis (Spark)
* **Limpieza y Transformación:** Uso de **Apache Spark** para leer de HDFS/Kafka.
    * Limpieza de coordenadas erróneas.
    * Cálculo de velocidad media por calle.
    * **Agregación de datos:** Ejemplo: *"¿Cuántos viajes se iniciaron en la Zona A entre las 18:00 y 19:00?"*.

### D. Inteligencia Artificial (El cerebro del sistema)
* **Modelo de Predicción (Machine Learning):** Uso de **Scikit-learn** o **Spark MLlib** para crear un Modelo de Regresión.
    * **Input:** Hora, Día de la semana, Clima (cruzado con API externa), Eventos en la ciudad.
    * **Output:** Predicción del número de taxis necesarios en cada distrito.
* **Despliegue:** El modelo se expone a través de una API en Python (**FastAPI** o **Flask**).
    * *Funcionamiento:* La app del taxista consulta la API -> Respuesta: *"Vete a la zona Centro, probabilidad de cliente: Alta"*.

### E. Visualización y Automatización (Producto Final)
* **Dashboard:** Uso de **Power BI** o **Grafana** conectado a MongoDB/Hive.
    * Mapa de calor (Heatmap) de la ciudad con zonas de alta demanda.
    * Gráficos de ingresos por hora.
* **Automatización con n8n:**
    * *Flujo:* Si la predicción de demanda en una zona supera el **90%** y hay pocos taxis libres allí -> **n8n** envía una alerta automática a un canal de Telegram/Slack de los conductores o un email al gestor de flota.

---

## 3. ¿Por qué este proyecto es ideal para aprobar?

1.  **Cubre el Big Data:** Integras HDFS, Spark y Flume/Kafka (ingesta, almacenamiento y proceso).
2.  **Cubre la IA:** Implementas un modelo predictivo real (Regresión) y una API.
3.  **Cubre Sistemas:** Utilizas MongoDB (NoSQL) y n8n (Automatización).
4.  **Es Visual:** Los mapas de calor quedan excelentes en la defensa del proyecto.
5.  **Tiene Narrativa:** Es fácil de "vender" como solución para reducir la contaminación (menos vueltas en vacío) y mejorar el tráfico.

---

## 4. Siguiente paso recomendado
Para la entrega del **1 de febrero (Propuesta detallada)**, deberías empezar a redactar:

* **Objetivos:** Optimizar rutas y predecir demanda.
* **Fuentes de datos:** Generador de logs GPS sintéticos + API pública de clima (AEMET/OpenWeather).
* **Diagrama de arquitectura:** Dibujar cómo Kafka le pasa datos a Spark y este a MongoDB.
