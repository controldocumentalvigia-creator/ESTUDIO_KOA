from __future__ import annotations
import pandas as pd
from config import *


def audit_table(df: pd.DataFrame) -> pd.DataFrame:
    checks = [
        ("Registros totales", len(df)),
        ("Fechas inválidas", df[COL_DATE].isna().sum()),
        ("Jornadas no reconocidas", (~df[COL_SHIFT].isin(VALID_SHIFTS)).sum()),
        ("Recorridos no reconocidos", (~df[COL_ROUTE].isin(VALID_ROUTES)).sum()),
        ("Horas programadas inválidas", df["scheduled_min"].isna().sum()),
        ("Horas reales inválidas", df["actual_min"].isna().sum()),
        ("Registros válidos de puntualidad", df["valid_punctuality"].sum()),
        ("Tiempos efectivos válidos", df["valid_time"].sum()),
        ("Usuarios nulos", df[COL_USERS].isna().sum()),
    ]
    return pd.DataFrame(checks, columns=["validacion","cantidad"])
