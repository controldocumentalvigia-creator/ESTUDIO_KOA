from __future__ import annotations
import re
import unicodedata
import numpy as np
import pandas as pd


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().upper()
    text = " ".join(text.split())
    return text


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def time_to_minutes(value: object) -> float:
    """Convierte hora Excel/Python/texto a minutos después de medianoche.

    Devuelve NaN para vacíos, 00:00 usados como marcador, fechas Excel corruptas
    y valores fuera del rango de un día.
    """
    if pd.isna(value):
        return np.nan
    try:
        if hasattr(value, "hour"):
            # Fechas anómalas como 1902-01-05 00:00:00 no son horas válidas.
            if hasattr(value, "year") and int(getattr(value, "year", 1899)) > 1900:
                return np.nan
            minutes = value.hour * 60 + value.minute + value.second / 60
        elif isinstance(value, (int, float, np.number)):
            number = float(value)
            if not np.isfinite(number):
                return np.nan
            # Fracción de día de Excel.
            minutes = (number % 1) * 1440
        else:
            text = str(value).strip()
            if not text:
                return np.nan
            parsed = pd.to_datetime(text, errors="coerce")
            if pd.isna(parsed):
                return np.nan
            minutes = parsed.hour * 60 + parsed.minute + parsed.second / 60
        if minutes <= 0 or minutes >= 1440:
            return np.nan
        return float(minutes)
    except Exception:
        return np.nan


def duration_to_minutes(value: object) -> float:
    if pd.isna(value):
        return np.nan
    try:
        if hasattr(value, "hour"):
            minutes = value.hour * 60 + value.minute + value.second / 60
        elif isinstance(value, (int, float, np.number)):
            minutes = float(value) * 1440
        else:
            td = pd.to_timedelta(str(value), errors="coerce")
            if pd.isna(td):
                return np.nan
            minutes = td.total_seconds() / 60
        if not np.isfinite(minutes) or minutes < 0 or minutes > 240:
            return np.nan
        return float(minutes)
    except Exception:
        return np.nan


def month_label(period: pd.Period) -> str:
    names = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
    return f"{names[period.month]} {period.year}"
