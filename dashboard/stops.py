from __future__ import annotations
import streamlit as st
import plotly.express as px
from core.metrics import stop_frequency


def render(df):
    st.subheader("Paraderos oficiales")
    st.info("La mañana usa un único paradero: OXXO HÉROES. La tarde usa únicamente VIRREY, HÉROES y POLO. La fuente exclusiva es la columna PARADAS.")
    freq=stop_frequency(df)
    if freq.empty:
        st.warning("No hay recorridos efectivos con paraderos reconocidos para los filtros seleccionados.")
        return
    fig=px.bar(freq,x="paradero",y="usos_efectivos",color="jornada",barmode="group",text_auto=True,title="Uso efectivo de paraderos oficiales")
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(freq,use_container_width=True,hide_index=True)
