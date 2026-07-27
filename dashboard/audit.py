from __future__ import annotations
import streamlit as st
from core.validator import audit_table
from core.metrics import punctuality_by_shift


def render(df):
    st.subheader("Auditoría de calidad de datos")
    st.dataframe(audit_table(df),use_container_width=True,hide_index=True)

    st.markdown("### Validación de puntualidad por jornada")
    shift_table=punctuality_by_shift(df)
    st.dataframe(
        shift_table.style.format({"puntualidad":"{:.1%}"}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("""
**Reglas matemáticas aplicadas**

- Desviación = hora real de salida − hora programada.
- **Mañana:** puntual únicamente cuando la desviación es exactamente 0 minutos.
- **Mañana:** anticipada si la desviación es menor que 0; retrasada si es mayor que 0.
- **Tarde:** puntual cuando la desviación está entre 0 y 5 minutos, incluyendo ambos límites.
- **Tarde:** anticipada si la desviación es menor que 0; retrasada cuando supera 5 minutos.
- La puntualidad general es ponderada: suma las salidas puntuales de ambas jornadas y las divide entre todos los registros válidos.
- Se excluyen horas vacías, `00:00`, fechas-hora corruptas y desviaciones mayores a 180 minutos.
- Los tiempos promedio, mediana, P90 y P95 usan únicamente recorridos efectivos con usuarios y duración válida.
""")
