# Informe de Aplicación a Big Data

## 5. Las 5 V aplicadas al proyecto

| Dimension (V) | Relación con el sistema de sensores | Ejemplo concreto | Ubicación (CSV Actual vs. Futura Ampliación) |
| :--- | :--- | :--- | :--- |
| **Volumen** | Se refiere a la cantidad masiva de datos generados por la red de sensores a lo largo del tiempo. | Acumular 100,000 filas en el archivo CSV actual (alrededor de unos cuantos Megabytes). En una ampliación, escalar a millones de lecturas diarias por cada planta. | **CSV Actual** (para los 100,000 registros) y **Futura Ampliación** (al escalar a Petabytes). |
| **Velocidad** | Representa la rapidez con la que se generan y procesan los datos del monitoreo en tiempo real. | Transmisión por streaming (ej. cada segundo) de telemetría mediante protocolos como MQTT o Kafka para detectar sobrecalentamiento instantáneamente. | **Futura Ampliación** (El CSV actual es un lote/batch estático cargado en memoria). |
| **Variedad** | Abarca los distintos formatos y fuentes de datos recopilados del entorno industrial. | Integración de registros tabulares (CSV), logs JSON del IoT, termografías infrarrojas (imágenes) y texto de reportes técnicos. | **Futura Ampliación** (El CSV actual contiene únicamente datos estructurados planos). |
| **Veracidad** | Corresponde a la calidad, exactitud y confiabilidad de las lecturas para evitar falsas alarmas. | Filtrado de ruidez, valores nulos, fallas de calibración o lecturas anómalas por pérdida de señal en la red de sensores. | **CSV Actual** (Manejado mediante limpieza de datos con Pandas) y **Futura Ampliación**. |
| **Valor** | Es la utilidad de negocio obtenida al transformar los datos crudos en decisiones estratégicas. | Identificar qué planta registra más alertas de temperatura (>85 °C) para realizar mantenimiento preventivo antes de una falla crítica. | **CSV Actual** (Análisis realizado en `analisis.py`) y **Futura Ampliación**. |

---

## 6. Tipos de datos y procesamiento tradicional

### Clasificación de Elementos

* **El CSV de sensores:** **Estructurado.** Posee un esquema fijo definido por filas y columnas bien delimitadas (`id_sensor`, `fecha_hora`, `planta`, `temperatura_c`).
* **Un mensaje JSON enviado por un sensor:** **Semiestructurado.** No requiere una tabla estricta pero contiene etiquetas y pares clave-valor que le otorgan organización interna.
* **Una fotografía de una máquina:** **No estructurado.** Datos binarios/visuales sin un esquema conceptual predefinido.
* **El texto libre de un reporte de mantenimiento:** **No estructurado.** Cadena de texto en lenguaje natural sin un formato rígido ni campos prefijados.

### ¿Por qué 100,000 registros no convierten automáticamente al archivo en Big Data?

Un conjunto de datos de 100,000 registros no se considera Big Data porque cabe fácilmente en la memoria RAM de cualquier computadora personal estándar (ocupa apenas unos pocos megabytes) y puede procesarse en segundos utilizando herramientas de procesamiento tradicional centralizado como Python y la librería Pandas. 

El término **Big Data** se aplica cuando el volumen, la velocidad o la variedad de los datos superan las capacidades del almacenamiento y procesamiento en una sola máquina, requiriendo arquitecturas distribuidas (como Apache Spark, Hadoop o clústeres en la nube).

### Limitaciones que podrían aparecer al aumentar la escala

1. **Agotamiento de Memoria (RAM Out-of-Memory):** Al subir la escala a cientos de millones de filas, intentar cargar el archivo completo con `pd.read_csv()` provocará un colapso por falta de memoria RAM.
2. **Cuellos de Botella en I/O y Cómputo:** Los archivos CSV planos son ineficientes para lectura masiva. Procesar secuencialmente en un solo hilo de CPU volvería las consultas y agregaciones extremadamente lentas.
3. **Latencia de Procesamiento:** Si la velocidad de entrada de datos es continua (streaming), el modelo en lote tradicional no podrá responder a las alertas en tiempo real.
---

## 7. Batch y Streaming

### Tipo de procesamiento realizado y justificación
El programa ejecutado (`analisis.py`) utiliza **procesamiento por lotes (Batch Processing)**. Se justifica porque opera sobre un conjunto de datos estático y delimitado (un archivo CSV cargado previamente en disco con 100,000 registros), procesando toda la información de manera secuencial en un solo bloque de tiempo sin entrada de eventos continuos en tiempo real.

### Enfoque para emitir una alerta a pocos segundos de una lectura > 85 °C
Para este caso de uso se requiere un enfoque de **procesamiento en tiempo real (Streaming Processing)**.
* **Justificación de tiempo:** Un sobrecalentamiento (>85 °C) requiere una acción inmediata (latencia de milisegundos a pocos segundos) para prevenir fallas catastróficas o paradas no planificadas de maquinaria.
* **Tecnologías sugeridas:** Un gestor de mensajería como **Apache Kafka** o **RabbitMQ** para capturar el evento en transmisión, combinado con un motor de streaming como **Apache Flink** o **Spark Streaming** que analice el flujo y dispare alertas instantáneas.

### Enfoque para generar un resumen al terminar el día
Para el resumen diario se utiliza un enfoque de **procesamiento por lotes (Batch Processing)** scheduled (programado).
* **Justificación de tiempo:** Las métricas consolidadas (como promedios diarios, tendencias e historial) no requieren inmediatez. Es más eficiente acumular todas las lecturas del día y ejecutar una tarea programada (ej. un job nocturno) que agregue los datos con menor costo computacional.

---

## 8. Arquitecturas Lambda y Kappa

### Escenario A: Combinación de lote histórico y procesamiento rápido reciente
* **Arquitectura elegida:** **Arquitectura Lambda**.
* **Justificación:** La arquitectura Lambda se diseñó específicamente para equilibrar la precisión de datos históricos con la baja latencia de datos recientes. Divide el procesamiento en dos capas paralelas: la capa de lotes (*Batch Layer*) para recalcular con precisión todo el historial, y la capa de velocidad (*Speed Layer*) para procesar el flujo reciente en tiempo real.

#### Diagrama de la propuesta (Lambda)
```text
                     ┌───────────────────┐     ┌─────────────────┐
               ┌────>│  Capa de Lotes    │---->│ Vista de Lotes  │────┐
               │     │  (Batch Layer)    │     │  (Re-cálculo)   │    │
┌───────────┐  │     └───────────────────┘     └─────────────────┘    │    ┌─────────────────┐
│ Fuente de │──┤                                                      ├--->│ Vista Unificada │
│   Datos   │  │     ┌───────────────────┐     ┌─────────────────┐    │    │ (Serving Layer) │
└───────────┘  └────>│ Capa de Velocidad │---->│ Vista en Tiempo │────┘    └─────────────────┘
                     │   (Speed Layer)   │     │      Real       │
                     └───────────────────┘     └─────────────────┘
```


---

## 9. Analítica descriptiva, predictiva y prescriptiva

### Analítica Descriptiva (¿Qué sucedió?)
A partir del análisis de los 100,000 registros del dataset:
1. **Hallazgo 1:** Se detectaron **1,523 lecturas con temperatura crítica (> 85 °C)** en total.
2. **Hallazgo 2:** La **Planta Norte** registró el promedio de temperatura más elevado con **68.4 °C**, posicionándose además como la planta con mayor número de alertas acumuladas.

---

### Analítica Predictiva (¿Qué podría suceder?)
* **Pregunta de investigación:** *¿Tiene la máquina un riesgo inminente de sufrir una avería mecánica en las próximas 48 horas tras presentar patrones repetidos de sobrecalentamiento?*
* **Datos adicionales necesarios:**
  - Historial de mantenimiento preventivo y correctivo de cada equipo.
  - Horas de operación continuas y antigüedad del equipo.
  - Mediciones de vibración (RMS / picos) sincronizadas en el mismo intervalo de tiempo.
  - Registros de carga de trabajo o presión operativa durante la medición.

---

### Analítica Prescriptiva (¿Qué debemos hacer?)
* **Acción propuesta:** Implementar una inspección técnica prioritaria y la reprogramación preventiva de carga de trabajo para las máquinas que registren más de 3 alertas continuas en un periodo de 12 horas, derivando la producción temporalmente a líneas secundarias.
* **Información a revisar antes de decidir:**
  - Diagnóstico previo de sensores (para descartar fallas de calibración del sensor).
  - Disponibilidad de repuestos críticos en almacén.
  - Impacto económico de la pausa programada en la cadena de producción vs. el costo de una parada no no planeada por fallo catastrófico.
