**IES Zaidín Vergeles — Proyecto de IA - BD** fileciteturn0file0

**Autores:**
- Adrián Ruiz Sánchez
- Francisco José Salmerón Puig
- Ismael Torres González

---

## Índice

- [Definición del problema y objetivos](#definición-del-problema-y-objetivos)
  - [Objetivos principales](#objetivos-principales)
- [Estado del arte y alcance](#estado-del-arte-y-alcance)
- [Planificación del desarrollo](#planificación-del-desarrollo)
- [Herramientas y tecnologías](#herramientas-y-tecnologías)
  - [Inteligencia Artificial y Aprendizaje Automático (IA/ML)](#inteligencia-artificial-y-aprendizaje-automático-iaml)
  - [Big Data y gestión de datos](#big-data-y-gestión-de-datos)
  - [Backend y API](#backend-y-api)
  - [Frontend](#frontend)
  - [Visualización de datos](#visualización-de-datos)
  - [Otras herramientas](#otras-herramientas)
- [Fuentes de datos previstas](#fuentes-de-datos-previstas)
  - [Recetas y nutrición](#recetas-y-nutrición)
  - [Ingredientes y alergias](#ingredientes-y-alergias)
  - [Datos de usuarios](#datos-de-usuarios)
  - [Procesamiento inicial de los datos](#procesamiento-inicial-de-los-datos)

---

## Definición del problema y objetivos

En la actualidad, muchas personas experimentan serias dificultades a la hora de planificar sus comidas diarias de forma adecuada. Estas dificultades aumentan cuando deben tenerse en cuenta factores como alergias e intolerancias alimentarias (por ejemplo, al gluten o a la lactosa), preferencias personales o éticas (como dietas veganas, vegetarianas o la necesidad de comidas rápidas) y objetivos de salud específicos, tales como la pérdida de peso o el control de la ingesta calórica. Como consecuencia, estas personas suelen sentirse frustradas, terminan recurriendo a opciones poco saludables o abandonan sus dietas, lo que da lugar a hábitos alimenticios poco sostenibles a largo plazo. fileciteturn0file0

El problema principal radica en la ausencia de herramientas accesibles, intuitivas y personalizadas que integren de manera eficaz la recomendación inteligente de comidas con información nutricional precisa y fiable. Muchas soluciones actuales son demasiado genéricas, no contemplan múltiples restricciones simultáneamente o requieren un esfuerzo excesivo por parte del usuario para introducir y analizar los datos. Por ello, se hace necesario desarrollar una herramienta que facilite la planificación alimentaria diaria, adaptándose a las necesidades individuales y promoviendo hábitos saludables, equilibrados y sostenibles. fileciteturn0file0

El objetivo de este proyecto es diseñar una solución que permita a los usuarios planificar sus comidas de forma personalizada, teniendo en cuenta sus restricciones alimentarias, preferencias y metas nutricionales, proporcionando recomendaciones prácticas y basadas en datos nutricionales precisos, con el fin de mejorar su calidad de vida y favorecer una alimentación más consciente y saludable. fileciteturn0file0

---

## Objetivos principales

- Desarrollar un asistente basado en modelos de lenguaje de gran tamaño (LLM) que permita la generación, adaptación y recomendación de recetas personalizadas a través de una interfaz conversacional. Este asistente deberá ser capaz de excluir automáticamente alérgenos específicos, respetar preferencias alimentarias y ajustar los valores nutricionales, como macronutrientes y calorías, en función de los objetivos individuales de cada usuario. fileciteturn0file0

- Diseñar un sistema capaz de almacenar, gestionar y procesar grandes volúmenes de datos relacionados con recetas, ingredientes y valores nutricionales. Este sistema deberá permitir un filtrado eficiente y escalable, garantizando tiempos de respuesta adecuados incluso ante un alto número de consultas y combinaciones de restricciones alimentarias. fileciteturn0file0

- Desplegar una API funcional, segura y escalable que exponga los servicios de recomendación y personalización de recetas. Dicha API deberá integrarse con un dashboard de análisis que permita visualizar métricas de uso, rendimiento del sistema y patrones de consumo, facilitando tanto la monitorización del servicio como la toma de decisiones basadas en datos para futuras mejoras del asistente. fileciteturn0file0

---

## Estado del arte y alcance

En los últimos años han surgido diversas aplicaciones y plataformas comerciales orientadas a la generación y recomendación de recetas mediante inteligencia artificial. Herramientas como ChefGPT, DishGen o SuperCook emplean modelos avanzados para sugerir recetas en función de los ingredientes disponibles, el tipo de dieta (como keto, vegana o vegetariana) o restricciones específicas del usuario. Estas soluciones suelen incorporar funcionalidades adicionales como el seguimiento calórico, la planificación semanal de comidas y, en algunos casos, la estimación de macronutrientes, lo que facilita la adopción de hábitos alimentarios más estructurados. fileciteturn0file0

Desde el ámbito académico, se han desarrollado sistemas más orientados a la personalización y la explicabilidad de las recomendaciones. Muchos de estos enfoques combinan modelos de lenguaje de gran tamaño (LLM) con sistemas basados en reglas expertas (Rule-Based Reasoning, RBR), permitiendo justificar las recomendaciones ofrecidas al usuario. Dichos sistemas suelen tener en cuenta variables como el metabolismo basal (BMR), el nivel de actividad física, objetivos de salud y la presencia de alergias o intolerancias alimentarias. A nivel tecnológico, es habitual el uso de bases de datos NoSQL como MongoDB para el almacenamiento de recetas e ingredientes, junto con APIs REST para la comunicación entre los distintos componentes del sistema. fileciteturn0file0

En cuanto al alcance del proyecto, este se centra en el desarrollo de un producto mínimo viable (MVP) que ofrezca una experiencia conversacional mediante chat, combinada con un perfil de usuario básico para almacenar preferencias, restricciones y objetivos nutricionales. El sistema procesará un conjunto inicial de más de 1.000 recetas, permitiendo aplicar filtros estrictos por alergias, dietas y preferencias alimentarias, así como mostrar métricas nutricionales relevantes (calorías y macronutrientes). fileciteturn0file0

Quedan fuera del alcance del proyecto el entrenamiento de modelos LLM desde cero, optándose por el uso de APIs de modelos preentrenados, cuya elección será debidamente justificada. Asimismo, no se abordará el escalado industrial del sistema ni su despliegue en entornos de producción de alta demanda, centrándose el trabajo en la validación funcional y técnica del enfoque propuesto. fileciteturn0file0

---

## Planificación del desarrollo

| Fase | Tareas principales | Duración | Fecha estimada |
|------|--------------------|----------|----------------|
| 1. Investigación y datos | Recopilar datasets, diseñar esquema BD, prototipo prompts LLM. | 2 semanas | 22 ene - 5 feb |
| 2. Desarrollo core | Implementar recomendador (filtros, RAG), API backend, modelo ML básico. | 4 semanas | 6 feb - 5 mar |
| 3. Integración Big Data | Procesar datasets con Spark/MongoDB, dashboard Power BI. | 2 semanas | 6 - 20 mar |
| 4. Frontend y pruebas | Chat UI, tests usuarios (10 perfiles simulados), refinamiento. | 3 semanas | 21 mar - 11 abr |
| 5. Documentación y defensa | GitHub repo, video demo (20 min), informe técnico. | 1 semana | 12 - 22 abr |

---

## Herramientas y tecnologías

### Inteligencia Artificial y Aprendizaje Automático (IA/ML)

El desarrollo del sistema de recomendación se realizará principalmente en Python, utilizando librerías ampliamente adoptadas en el ámbito del análisis de datos y el aprendizaje automático. Pandas se empleará para la manipulación y limpieza de datos nutricionales y de recetas, mientras que scikit-learn permitirá implementar un recomendador *content-based*, basado en la similitud entre ingredientes, perfiles nutricionales y preferencias del usuario. fileciteturn0file0

Para la generación y adaptación de recetas en lenguaje natural, se integrarán APIs de modelos LLM preentrenados, como OpenAI o Groq, cuya elección se justifica por su eficiencia, calidad de resultados y reducción de costes computacionales frente al entrenamiento de modelos propios. fileciteturn0file0

---

### Big Data y gestión de datos

La persistencia de la información se realizará mediante MongoDB, una base de datos NoSQL adecuada para almacenar perfiles de usuario, recetas y estructuras de datos semiestructuradas de forma flexible. fileciteturn0file0

Para el procesamiento de grandes volúmenes de datos se utilizará Apache Spark, permitiendo el tratamiento eficiente de datasets extensos de ingredientes y valores nutricionales. De forma opcional, se contempla el uso de HDFS (Hadoop Distributed File System) para el almacenamiento distribuido en caso de trabajar con volúmenes de datos significativamente grandes. fileciteturn0file0

---

### Backend y API

El backend del sistema se desarrollará utilizando FastAPI o Flask, exponiendo una API REST que gestione las peticiones del frontend, la lógica de recomendación y la comunicación con los servicios de IA. fileciteturn0file0

Para facilitar el despliegue, la portabilidad y la reproducibilidad del entorno, se empleará Docker, encapsulando la aplicación y sus dependencias en contenedores. fileciteturn0file0

---

### Frontend

La interfaz de usuario se implementará mediante React Native con Tailwind CSS, permitiendo el desarrollo rápido de una aplicación móvil multiplataforma (iOS/Android/web) que incluye un chat conversacional con el asistente y un panel de control (dashboard) para la visualización de recomendaciones y métricas básicas del usuario. fileciteturn0file0

---

### Visualización de datos

Para la generación de informes y la visualización de información nutricional se utilizarán herramientas como Matplotlib para gráficos integrados en la aplicación, así como Power BI para la elaboración de dashboards más avanzados orientados al análisis y la presentación de resultados. fileciteturn0file0

---

### Otras herramientas

El control de versiones y la gestión del código se realizarán a través de GitHub, manteniendo un repositorio público del proyecto. fileciteturn0file0

Además, se empleará n8n como herramienta de automatización para los procesos ETL (extracción, transformación y carga de datos), facilitando la actualización y mantenimiento de los datasets utilizados por el sistema. fileciteturn0file0

---

## Fuentes de datos previstas

### Recetas y nutrición

Para la obtención de información nutricional fiable se utilizará la Base Española de Datos de Composición de Alimentos (BEDCA), que incluye información detallada de más de 800 alimentos, como valores calóricos y macronutrientes. Esta fuente resulta especialmente relevante por su carácter oficial y su adecuación al contexto alimentario español. fileciteturn0file0

Adicionalmente, se integrará la API de Edamam, que proporciona acceso a más de 200.000 recetas etiquetadas con información sobre ingredientes, alérgenos, tipos de dieta y valores nutricionales, lo que permitirá enriquecer el sistema de recomendación y ampliar la diversidad de recetas disponibles. fileciteturn0file0

---

### Ingredientes y alergias

Para complementar la información sobre ingredientes y restricciones alimentarias, se emplearán bases de datos internacionales como INFOODS, promovida por la FAO, que ofrece datos estandarizados sobre composición de alimentos a nivel global. fileciteturn0file0

Asimismo, se recurrirá a datasets disponibles en Kaggle, como conjuntos de datos del tipo **“Recipe Ingredients”**, útiles para el etiquetado de ingredientes, la detección de alérgenos y la categorización de recetas según distintos criterios dietéticos. fileciteturn0file0

---

### Datos de usuarios

Dado que el proyecto se limita a un entorno de prueba, los datos de usuario se basarán en perfiles simulados, generando más de 100 perfiles sintéticos que incluyan alergias, preferencias alimentarias y objetivos nutricionales. fileciteturn0file0

Estos perfiles permitirán validar el funcionamiento del sistema de recomendación y servirán como base para la recogida de feedback histórico, utilizado posteriormente para la mejora del modelo de recomendación mediante técnicas de aprendizaje automático. fileciteturn0file0

---

### Procesamiento inicial de los datos

Los datos se obtendrán inicialmente en formatos CSV y JSON, siendo procesados mediante Apache Spark para llevar a cabo tareas de limpieza, normalización y agregación. fileciteturn0file0

Una vez procesados, los datos se cargarán en MongoDB, facilitando un acceso eficiente y flexible a la información durante la ejecución del sistema y el desarrollo de las funcionalidades del asistente conversacional. fileciteturn0file0
"""
