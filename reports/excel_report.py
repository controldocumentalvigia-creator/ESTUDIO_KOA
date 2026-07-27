from __future__ import annotations
from io import BytesIO
import pandas as pd
from core.metrics import kpis, monthly_summary, weekly_summary, punctuality_distribution, punctuality_by_shift, stop_frequency
from core.validator import audit_table


def build_excel(df: pd.DataFrame) -> bytes:
    out=BytesIO()
    with pd.ExcelWriter(out,engine="xlsxwriter") as writer:
        pd.DataFrame([kpis(df)]).to_excel(writer,sheet_name="KPIs",index=False)
        monthly_summary(df).to_excel(writer,sheet_name="Mensual",index=False)
        weekly_summary(df).to_excel(writer,sheet_name="Semanal",index=False)
        punctuality_distribution(df).to_excel(writer,sheet_name="Puntualidad",index=False)
        punctuality_by_shift(df).to_excel(writer,sheet_name="Puntualidad_jornada",index=False)
        stop_frequency(df).to_excel(writer,sheet_name="Paraderos",index=False)
        audit_table(df).to_excel(writer,sheet_name="Auditoria",index=False)
        df.to_excel(writer,sheet_name="Base_filtrada",index=False)
    return out.getvalue()
