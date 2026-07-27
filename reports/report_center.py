from __future__ import annotations
import streamlit as st
from reports.excel_report import build_excel


def render(df):
    st.subheader("Centro de reportes")
    st.download_button("Descargar Excel auditado",data=build_excel(df),file_name="KOA_Analisis_Auditado.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.caption("El Excel utiliza exactamente los mismos filtros y cálculos del dashboard.")
