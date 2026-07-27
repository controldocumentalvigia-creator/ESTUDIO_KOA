from __future__ import annotations
import streamlit as st
import pandas as pd
from core.filters import apply_filters
from core.metrics import comparison


def render(base_df):
    st.subheader("Comparación antes y después de un cambio de horarios")
    dmin=base_df["DIA DEL SERVICIO"].min().date(); dmax=base_df["DIA DEL SERVICIO"].max().date()
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Periodo anterior**")
        a1=st.date_input("Desde (antes)",dmin,key="a1")
        a2=st.date_input("Hasta (antes)",dmax,key="a2")
    with c2:
        st.markdown("**Periodo posterior**")
        b1=st.date_input("Desde (después)",dmin,key="b1")
        b2=st.date_input("Hasta (después)",dmax,key="b2")
    before=base_df[base_df["DIA DEL SERVICIO"].between(pd.Timestamp(a1),pd.Timestamp(a2))]
    after=base_df[base_df["DIA DEL SERVICIO"].between(pd.Timestamp(b1),pd.Timestamp(b2))]
    result=comparison(before,after)
    st.dataframe(result,use_container_width=True,hide_index=True)
