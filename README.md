
Este proyecto tiene como objetivo analizar las mediciones de temperatura y vibración de sensores monitoreados en cuatro plantas industriales para identificar comportamientos anómalos, detectar alertas de sobrecalentamiento y generar reportes procesables.

Los datos utilizados en este proyecto son simulados (`sensores_industriales.csv` con 100,000 registros).

```text
├── data/
│   └── sensores_industriales.csv   # Dataset de mediciones
├── resultados/
│   └── alertas.csv                 # Alertas generadas (> 85 °C)
├── .gitignore                      # Archivos excluidos del control de versiones
├── analisis.py                     # Script principal de análisis
├── requirements.txt                # Dependencias del proyecto
└── README.md                       # Documentación del proyecto
