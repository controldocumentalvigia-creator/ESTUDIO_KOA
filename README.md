# KOA Analytics V4.1

Aplicación Streamlit para análisis operacional de KOA, con filtros por rango de fechas, meses, jornada y recorrido.

## Puntualidad oficial

- Mañana: salida puntual únicamente a la hora programada.
- Tarde: salida puntual entre la hora programada y 5 minutos después; el retraso inicia en el minuto 6.
- La puntualidad general se calcula de forma ponderada sobre los registros válidos.

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```
