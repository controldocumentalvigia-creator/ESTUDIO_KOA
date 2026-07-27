from __future__ import annotations
import numpy as np
import pandas as pd
from config import *
from core.utils import normalize_text, strip_accents, month_label


def _punctuality_masks(df: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Clasifica cada salida válida con la regla oficial por jornada.

    MAÑANA: puntual solo si la desviación es exactamente 0 minutos.
    TARDE: puntual si la desviación está entre 0 y 5 minutos, inclusive.
    En ambas jornadas, salir antes de la hora programada es anticipado.
    El retraso comienza >0 en la mañana y >5 en la tarde.
    """
    valid = df["valid_punctuality"].fillna(False)
    shift = df[COL_SHIFT].fillna("").astype(str).str.upper()
    dev = pd.to_numeric(df["deviation_min"], errors="coerce")

    morning = valid & shift.eq("MAÑANA")
    afternoon = valid & shift.eq("TARDE")
    considered = morning | afternoon

    punctual = (morning & dev.eq(0)) | (afternoon & dev.between(0, 5, inclusive="both"))
    early = considered & dev.lt(0)
    late = (morning & dev.gt(0)) | (afternoon & dev.gt(5))
    return considered, punctual, early, late


def kpis(df: pd.DataFrame) -> dict:
    considered, punctual, early, late = _punctuality_masks(df)
    valid_t = df.loc[df["effective_trip"] & df["valid_time"], "effective_time_min"]
    den = int(considered.sum())

    morning_valid = considered & df[COL_SHIFT].eq("MAÑANA")
    afternoon_valid = considered & df[COL_SHIFT].eq("TARDE")
    morning_punctual = punctual & df[COL_SHIFT].eq("MAÑANA")
    afternoon_punctual = punctual & df[COL_SHIFT].eq("TARDE")

    def ratio(n: int, d: int) -> float:
        return n / d if d else np.nan

    return {
        "records": int(len(df)),
        "days": int(df[COL_DATE].nunique()),
        "users": int(df[COL_USERS].fillna(0).sum()),
        "effective_trips": int(df["effective_trip"].sum()),
        "punctuality_valid": den,
        "punctual_n": int(punctual.sum()),
        "punctuality_official": ratio(int(punctual.sum()), den),
        # Alias conservado para compatibilidad con módulos anteriores.
        "punctual_0_5_n": int(punctual.sum()),
        "punctual_0_5": ratio(int(punctual.sum()), den),
        "punctual_morning_n": int(morning_punctual.sum()),
        "punctual_morning_valid": int(morning_valid.sum()),
        "punctual_morning": ratio(int(morning_punctual.sum()), int(morning_valid.sum())),
        "punctual_afternoon_n": int(afternoon_punctual.sum()),
        "punctual_afternoon_valid": int(afternoon_valid.sum()),
        "punctual_afternoon": ratio(int(afternoon_punctual.sum()), int(afternoon_valid.sum())),
        "early": ratio(int(early.sum()), den),
        "early_n": int(early.sum()),
        "late": ratio(int(late.sum()), den),
        "late_n": int(late.sum()),
        # Alias para compatibilidad: aquí representa retraso según jornada.
        "late_gt5": ratio(int(late.sum()), den),
        "late_gt5_n": int(late.sum()),
        "time_mean": valid_t.mean() if len(valid_t) else np.nan,
        "time_median": valid_t.median() if len(valid_t) else np.nan,
        "time_p90": valid_t.quantile(.90) if len(valid_t) else np.nan,
        "time_p95": valid_t.quantile(.95) if len(valid_t) else np.nan,
        "time_valid": int(len(valid_t)),
    }


def punctuality_distribution(df: pd.DataFrame) -> pd.DataFrame:
    considered, punctual, early, late = _punctuality_masks(df)
    den = int(considered.sum())
    categories = [
        ("Anticipadas", early),
        ("Puntuales según jornada", punctual),
        ("Retrasadas según jornada", late),
    ]
    return pd.DataFrame({
        "categoria": [label for label, _ in categories],
        "cantidad": [int(mask.sum()) for _, mask in categories],
        "porcentaje": [int(mask.sum()) / den if den else 0 for _, mask in categories],
    })


def punctuality_by_shift(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for shift in VALID_SHIFTS:
        group = df[df[COL_SHIFT].eq(shift)]
        m = kpis(group)
        rule = "Exactamente a la hora programada" if shift == "MAÑANA" else "Entre 0 y 5 minutos después"
        rows.append({
            "jornada": shift,
            "regla": rule,
            "registros_validos": m["punctuality_valid"],
            "puntuales": m["punctual_n"],
            "anticipadas": m["early_n"],
            "retrasadas": m["late_n"],
            "puntualidad": m["punctuality_official"],
        })
    return pd.DataFrame(rows)


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for period,g in df.groupby("month", observed=True):
        m=kpis(g)
        rows.append({"mes":str(period),"mes_etiqueta":month_label(period),**m})
    return pd.DataFrame(rows).sort_values("mes") if rows else pd.DataFrame()


def weekly_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for week,g in df.groupby("week_start", dropna=True):
        m=kpis(g)
        rows.append({"semana":pd.Timestamp(week),**m})
    return pd.DataFrame(rows).sort_values("semana") if rows else pd.DataFrame()


def stop_frequency(df: pd.DataFrame) -> pd.DataFrame:
    counts={}
    effective=df[df["effective_trip"]].copy()
    for _,row in effective.iterrows():
        shift=row[COL_SHIFT]
        raw=normalize_text(row[COL_STOPS])
        if shift=="MAÑANA":
            if strip_accents(raw).replace(" ","")=="OXXOHEROES":
                counts[(shift,"OXXO HÉROES")]=counts.get((shift,"OXXO HÉROES"),0)+1
        elif shift=="TARDE":
            plain=strip_accents(raw)
            for stop in OFFICIAL_STOPS["TARDE"]:
                if strip_accents(stop) in plain:
                    counts[(shift,stop)]=counts.get((shift,stop),0)+1
    rows=[{"jornada":j,"paradero":p,"usos_efectivos":n} for (j,p),n in counts.items()]
    return pd.DataFrame(rows).sort_values(["jornada","usos_efectivos"],ascending=[True,False]) if rows else pd.DataFrame(columns=["jornada","paradero","usos_efectivos"])


def comparison(df_before: pd.DataFrame, df_after: pd.DataFrame) -> pd.DataFrame:
    b,a=kpis(df_before),kpis(df_after)
    specs=[("Usuarios","users","n"),("Recorridos efectivos","effective_trips","n"),("Puntualidad oficial ponderada","punctuality_official","pct"),("Tiempo promedio","time_mean","min"),("P90","time_p90","min")]
    rows=[]
    for label,key,unit in specs:
        bv,av=b[key],a[key]
        delta=av-bv if pd.notna(bv) and pd.notna(av) else np.nan
        rows.append({"indicador":label,"antes":bv,"despues":av,"variacion":delta,"unidad":unit})
    return pd.DataFrame(rows)
