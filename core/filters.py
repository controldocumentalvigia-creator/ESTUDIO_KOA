from __future__ import annotations
import pandas as pd
from config import COL_DATE, COL_SHIFT, COL_ROUTE


def apply_filters(df: pd.DataFrame, start_date, end_date, months, shifts, routes) -> pd.DataFrame:
    mask = df[COL_DATE].between(pd.Timestamp(start_date), pd.Timestamp(end_date), inclusive="both")
    if months:
        mask &= df["month"].astype(str).isin(months)
    if shifts:
        mask &= df[COL_SHIFT].isin(shifts)
    if routes:
        mask &= df[COL_ROUTE].isin(routes)
    return df.loc[mask].copy()
