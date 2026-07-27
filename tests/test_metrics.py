import pandas as pd
from core.metrics import kpis, punctuality_distribution


def _base_df(shifts, deviations):
    n=len(shifts)
    return pd.DataFrame({
        "valid_punctuality":[True]*n,
        "deviation_min":deviations,
        "effective_trip":[False]*n,
        "valid_time":[False]*n,
        "effective_time_min":[None]*n,
        "DIA DEL SERVICIO":pd.to_datetime(["2026-01-01"]*n),
        "usuarios":[0]*n,
        "JORNADA":shifts,
    })


def test_morning_requires_exact_departure():
    df=_base_df(["MAÑANA"]*5,[-1,0,1,5,6])
    m=kpis(df)
    assert m["punctual_n"]==1
    assert m["early_n"]==1
    assert m["late_n"]==3
    assert abs(m["punctual_morning"]-(1/5))<1e-9


def test_afternoon_has_five_minute_wait():
    df=_base_df(["TARDE"]*6,[-1,0,1,5,6,10])
    m=kpis(df)
    assert m["punctual_n"]==3
    assert m["early_n"]==1
    assert m["late_n"]==2
    assert abs(m["punctual_afternoon"]-(3/6))<1e-9


def test_general_punctuality_is_weighted():
    df=_base_df(["MAÑANA","MAÑANA","TARDE","TARDE"],[0,1,5,6])
    m=kpis(df)
    assert m["punctual_n"]==2
    assert abs(m["punctuality_official"]-.5)<1e-9
    dist=punctuality_distribution(df)
    assert int(dist["cantidad"].sum())==4
