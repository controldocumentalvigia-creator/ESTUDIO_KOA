from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from config import APP_TITLE, DEFAULT_FILE, VALID_ROUTES, VALID_SHIFTS
from core.filters import apply_filters
from core.loader import load_data
from dashboard.audit import render as render_audit
from dashboard.comparison import render as render_comparison
from dashboard.executive import render as render_executive
from dashboard.stops import render as render_stops
from dashboard.strategic_map import render as render_strategic_map
from dashboard.trends import render as render_trends
from reports.report_center import render as render_reports

st.set_page_config(page_title=APP_TITLE, page_icon="🚌", layout="wide")

st.markdown(
    """
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    [data-testid="stSidebar"] {background:#eef3f9;}
    .koa-title {background:linear-gradient(90deg,#123d76,#1d5da7);color:white;
    padding:18px 22px;border-radius:12px;margin-bottom:14px;}
    .koa-title h1 {margin:0;font-size:29px;}
    .koa-title p {margin:4px 0 0 0;opacity:.92;}
    div[data-testid="stMetric"] {background:white;border:1px solid #dce4ed;border-radius:10px;padding:10px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="koa-title"><h1>{APP_TITLE}</h1><p>Análisis operativo, puntualidad por jornada y evaluación estratégica de paraderos</p></div>',
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def cached_load(source):
    return load_data(source)


with st.sidebar:
    st.header("Filtros")
    upload = st.file_uploader("Cargar base KOA (.xlsx)", type=["xlsx"])

source = upload if upload is not None else Path(DEFAULT_FILE)
if upload is None and not source.exists():
    alternative = Path("data") / DEFAULT_FILE
    source = alternative if alternative.exists() else source

try:
    base = cached_load(source)
except Exception as exc:
    st.error(f"No fue posible cargar la base: {exc}")
    st.stop()

valid_dates = base["DIA DEL SERVICIO"].dropna()
if valid_dates.empty:
    st.error("La base no contiene fechas válidas.")
    st.stop()

with st.sidebar:
    min_date, max_date = valid_dates.min().date(), valid_dates.max().date()
    date_range = st.date_input(
        "Rango exacto de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    available_months = sorted(base["month"].dropna().astype(str).unique().tolist())
    months = st.multiselect("Meses", available_months, default=available_months)
    shifts = st.multiselect("Jornada", VALID_SHIFTS, default=VALID_SHIFTS)
    routes = st.multiselect("Recorrido", VALID_ROUTES, default=VALID_ROUTES)

filtered = apply_filters(base, start_date, end_date, months, shifts, routes)
st.caption(
    f"Periodo filtrado: {pd.Timestamp(start_date):%d/%m/%Y} a {pd.Timestamp(end_date):%d/%m/%Y} · "
    f"{len(filtered):,} registros"
)

if filtered.empty:
    st.warning("No hay registros para la combinación de filtros seleccionada.")
    st.stop()

st.info(
    "Regla de puntualidad: en la mañana el vehículo debe salir exactamente a la hora programada. "
    "En la tarde se permiten hasta 5 minutos de espera para los usuarios; el retraso comienza desde el minuto 6."
)

tabs = st.tabs(
    [
        "Resumen ejecutivo",
        "Mensual y semanal",
        "Paraderos",
        "Mapa estratégico",
        "Antes vs. después",
        "Auditoría",
        "Reportes",
    ]
)

with tabs[0]:
    render_executive(filtered)
with tabs[1]:
    render_trends(filtered)
with tabs[2]:
    render_stops(filtered)
with tabs[3]:
    render_strategic_map(filtered)
with tabs[4]:
    render_comparison(base)
with tabs[5]:
    render_audit(filtered)
with tabs[6]:
    render_reports(filtered)
