from __future__ import annotations

import math
import pandas as pd
import pydeck as pdk
import streamlit as st


DEFAULT_KOA = {"name": "KOA", "lat": 4.6761, "lon": -74.0571}

# Coordenadas operativas de referencia. Deben validarse en campo antes de adoptar cambios.
CURRENT_STOPS = [
    {"name": "OXXO HÉROES", "type": "Paradero actual", "lat": 4.6693, "lon": -74.0597},
    {"name": "VIRREY", "type": "Paradero actual", "lat": 4.6758, "lon": -74.0557},
    {"name": "HÉROES", "type": "Paradero actual", "lat": 4.6690, "lon": -74.0594},
    {"name": "POLO", "type": "Paradero actual", "lat": 4.6657, "lon": -74.0670},
]

TRANSMILENIO_STATIONS = [
    {"name": "Virrey", "type": "Estación TransMilenio", "lat": 4.6745, "lon": -74.0564},
    {"name": "Calle 100", "type": "Estación TransMilenio", "lat": 4.6841, "lon": -74.0528},
    {"name": "Calle 85", "type": "Estación TransMilenio", "lat": 4.6709, "lon": -74.0581},
    {"name": "Héroes", "type": "Estación TransMilenio", "lat": 4.6687, "lon": -74.0601},
    {"name": "Polo", "type": "Estación TransMilenio", "lat": 4.6615, "lon": -74.0666},
]

PROPOSALS = [
    {"name": "Propuesta 1 · Virrey", "type": "Paradero propuesto", "lat": 4.6745, "lon": -74.0564},
    {"name": "Propuesta 2 · Calle 85", "type": "Paradero propuesto", "lat": 4.6709, "lon": -74.0581},
    {"name": "Propuesta 3 · Calle 100", "type": "Paradero propuesto", "lat": 4.6841, "lon": -74.0528},
]


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia de gran círculo en metros."""
    radius = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _table(points: list[dict], koa_lat: float, koa_lon: float) -> pd.DataFrame:
    rows = []
    for point in points:
        distance = _distance_m(koa_lat, koa_lon, point["lat"], point["lon"])
        rows.append(
            {
                "Alternativa": point["name"],
                "Tipo": point["type"],
                "Distancia lineal a KOA (m)": round(distance),
                "Caminata estimada (min)": max(1, round(distance / 75)),
                "Latitud": point["lat"],
                "Longitud": point["lon"],
            }
        )
    return pd.DataFrame(rows).sort_values("Distancia lineal a KOA (m)")


def render(_: pd.DataFrame | None = None) -> None:
    st.subheader("Mapa estratégico de paraderos y TransMilenio")
    st.caption(
        "Visualización exploratoria para comparar la ubicación de KOA, los puntos actuales, "
        "estaciones cercanas y posibles alternativas. Las coordenadas deben validarse con visita de campo."
    )

    with st.expander("Ubicación de KOA", expanded=False):
        col1, col2 = st.columns(2)
        koa_lat = col1.number_input("Latitud KOA", value=float(DEFAULT_KOA["lat"]), format="%.6f")
        koa_lon = col2.number_input("Longitud KOA", value=float(DEFAULT_KOA["lon"]), format="%.6f")
    if "koa_lat" not in locals():
        koa_lat, koa_lon = DEFAULT_KOA["lat"], DEFAULT_KOA["lon"]

    show_current = st.checkbox("Paraderos actuales", value=True)
    show_tm = st.checkbox("Estaciones de TransMilenio", value=True)
    show_proposals = st.checkbox("Propuestas", value=True)
    radius = st.select_slider("Radio de referencia alrededor de KOA", options=[300, 500, 800, 1000], value=500)

    layers = []
    koa_df = pd.DataFrame([{"name": "KOA", "lat": koa_lat, "lon": koa_lon}])
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=koa_df,
            get_position="[lon, lat]",
            get_radius=90,
            get_fill_color=[18, 61, 118, 230],
            pickable=True,
        )
    )
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=koa_df,
            get_position="[lon, lat]",
            get_radius=radius,
            stroked=True,
            filled=False,
            get_line_color=[18, 61, 118, 120],
            line_width_min_pixels=2,
        )
    )

    if show_current:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame(CURRENT_STOPS),
                get_position="[lon, lat]",
                get_radius=65,
                get_fill_color=[245, 158, 11, 220],
                pickable=True,
            )
        )
    if show_tm:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame(TRANSMILENIO_STATIONS),
                get_position="[lon, lat]",
                get_radius=65,
                get_fill_color=[220, 38, 38, 220],
                pickable=True,
            )
        )
    if show_proposals:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame(PROPOSALS),
                get_position="[lon, lat]",
                get_radius=75,
                get_fill_color=[22, 163, 74, 230],
                pickable=True,
            )
        )

    deck = pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(latitude=koa_lat, longitude=koa_lon, zoom=13.7, pitch=0),
        layers=layers,
        tooltip={"html": "<b>{name}</b><br/>{type}", "style": {"backgroundColor": "#123d76", "color": "white"}},
    )
    st.pydeck_chart(deck, use_container_width=True)

    st.markdown("### Alternativas cercanas")
    proposal_table = _table(PROPOSALS, koa_lat, koa_lon)
    st.dataframe(proposal_table, hide_index=True, use_container_width=True)

    st.info(
        "La distancia mostrada es lineal. Antes de definir un paradero deben verificarse el recorrido peatonal real, "
        "la seguridad del punto, la facilidad de ascenso y descenso, las restricciones viales y el impacto en el tiempo de ruta."
    )
