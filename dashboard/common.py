from __future__ import annotations
import math
import pandas as pd


def pct(value):
    return "—" if pd.isna(value) else f"{value:.1%}"

def num(value, digits=1, suffix=""):
    return "—" if pd.isna(value) else f"{value:.{digits}f}{suffix}"
