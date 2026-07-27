from __future__ import annotations
import streamlit as st
import plotly.express as px
from core.metrics import kpis, monthly_summary, punctuality_distribution, punctuality_by_shift
from dashboard.common import pct, num


def render(df):
    m=kpis(df)
    cols=st.columns(8)
    cards=[
        ("Registros",m["records"]),
        ("Días",m["days"]),
        ("Usuarios",m["users"]),
        ("Puntualidad general",pct(m["punctuality_official"])),
        ("Puntualidad mañana",pct(m["punctual_morning"])),
        ("Puntualidad tarde",pct(m["punctual_afternoon"])),
        ("Tiempo promedio",num(m["time_mean"],1," min")),
        ("P90",num(m["time_p90"],1," min")),
    ]
    for c,(label,value) in zip(cols,cards):
        c.metric(label,value)

    st.caption(
        f"Puntualidad calculada sobre {m['punctuality_valid']} registros válidos. "
        "En la mañana la salida es puntual únicamente a la hora programada; "
        "en la tarde se permiten hasta 5 minutos de espera y el retraso comienza en el minuto 6. "
        f"Los tiempos usan {m['time_valid']} recorridos efectivos con duración válida."
    )

    dist=punctuality_distribution(df)
    c1,c2=st.columns(2)
    with c1:
        fig=px.bar(dist,x="categoria",y="porcentaje",text=dist["porcentaje"].map(lambda x:f"{x:.1%}"),title="Distribución oficial de salidas")
        fig.update_yaxes(tickformat=".0%",title="Porcentaje")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        by_shift=punctuality_by_shift(df)
        fig=px.bar(by_shift,x="jornada",y="puntualidad",text=by_shift["puntualidad"].map(lambda x:f"{x:.1%}" if x==x else "N/D"),title="Puntualidad por jornada")
        fig.update_yaxes(tickformat=".0%",range=[0,1],title="Puntualidad")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig,use_container_width=True)

    monthly=monthly_summary(df)
    if not monthly.empty:
        fig=px.line(monthly,x="mes_etiqueta",y="punctuality_official",markers=True,title="Puntualidad general por mes")
        fig.update_yaxes(tickformat=".0%",range=[0,1],title="Puntualidad")
        st.plotly_chart(fig,use_container_width=True)

    st.markdown("### Lectura sencilla")
    if m["punctuality_valid"]:
        st.write(
            f"De cada 100 salidas válidas, aproximadamente **{m['punctuality_official']*100:.1f}** cumplen la regla aplicable a su jornada; "
            f"**{m['early']*100:.1f}** salen antes de la hora programada y **{m['late']*100:.1f}** salen retrasadas. "
            "Para la mañana, cualquier salida después de la hora programada cuenta como retraso. "
            "Para la tarde, solo cuenta como retraso cuando supera los 5 minutos de espera autorizada."
        )
    else:
        st.write("No hay registros válidos para calcular puntualidad.")
