from __future__ import annotations
import streamlit as st
import plotly.express as px
from core.metrics import monthly_summary, weekly_summary


def render(df):
    monthly=monthly_summary(df)
    st.subheader("Comportamiento mensual")
    if monthly.empty:
        st.info("No hay datos.")
        return
    c1,c2=st.columns(2)
    with c1:
        fig=px.bar(monthly,x="mes_etiqueta",y="users",text_auto=True,title="Usuarios por mes")
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        fig=px.line(monthly,x="mes_etiqueta",y=["time_mean","time_p90"],markers=True,title="Tiempo promedio y P90 por mes")
        fig.update_yaxes(title="Minutos")
        st.plotly_chart(fig,use_container_width=True)

    columns=["mes_etiqueta","records","users","effective_trips","punctuality_official","punctual_morning","punctual_afternoon","time_mean","time_median","time_p90","time_p95"]
    st.dataframe(monthly[columns],use_container_width=True,hide_index=True)

    with st.expander("Ver detalle semanal"):
        weekly=weekly_summary(df)
        if weekly.empty:
            st.info("No hay datos semanales.")
        else:
            fig=px.line(weekly,x="semana",y="punctuality_official",markers=True,title="Puntualidad semanal del periodo filtrado")
            fig.update_yaxes(tickformat=".0%",range=[0,1])
            st.plotly_chart(fig,use_container_width=True)
