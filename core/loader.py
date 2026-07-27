from __future__ import annotations
from pathlib import Path
from typing import BinaryIO
import pandas as pd

from config import *
from core.utils import normalize_text, time_to_minutes, duration_to_minutes

REQUIRED_COLUMNS = [COL_DATE, COL_ROUTE, COL_SHIFT, COL_SCHEDULED, COL_ACTUAL, COL_USERS, COL_STOPS, COL_EFFECTIVE_TIME]


def load_data(source: str | Path | BinaryIO) -> pd.DataFrame:
    try:
        df = pd.read_excel(source, sheet_name=DATA_SHEET, engine="openpyxl")
    except ValueError as exc:
        raise ValueError(f"No se encontró la hoja obligatoria '{DATA_SHEET}'.") from exc
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Faltan columnas obligatorias: " + ", ".join(missing))

    out = df.copy()
    out[COL_DATE] = pd.to_datetime(out[COL_DATE], errors="coerce").dt.normalize()
    out[COL_ROUTE] = out[COL_ROUTE].map(normalize_text)
    out[COL_SHIFT] = out[COL_SHIFT].map(normalize_text)
    out[COL_STOPS] = out[COL_STOPS].map(normalize_text)
    out[COL_USERS] = pd.to_numeric(out[COL_USERS], errors="coerce")
    out["scheduled_min"] = out[COL_SCHEDULED].map(time_to_minutes)
    out["actual_min"] = out[COL_ACTUAL].map(time_to_minutes)
    out["deviation_min"] = out["actual_min"] - out["scheduled_min"]
    # Desviaciones absurdas son errores de captura, no anticipos reales.
    out.loc[out["deviation_min"].abs() > 180, "deviation_min"] = pd.NA
    out["effective_time_min"] = out[COL_EFFECTIVE_TIME].map(duration_to_minutes)
    out["month"] = out[COL_DATE].dt.to_period("M")
    out["week_start"] = out[COL_DATE] - pd.to_timedelta(out[COL_DATE].dt.weekday, unit="D")
    out["valid_punctuality"] = out["deviation_min"].notna()
    out["valid_time"] = out["effective_time_min"].notna()
    out["effective_trip"] = (out[COL_USERS].fillna(0) > 0) & out["actual_min"].notna()
    return out
