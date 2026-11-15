"""Eurostat dissemination API (JSON-stat 2.0) into a tidy DataFrame.

fetch_dataset() needs internet. UNTESTED IN SANDBOX; VALIDATED IN CI.
parse_jsonstat() is pure and is unit-tested offline (tests/test_pipelines.py).
"""
import itertools

import pandas as pd
import requests

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"


def parse_jsonstat(obj):
    """JSON-stat 2.0 dataset -> tidy DataFrame: one column per dimension, plus 'value'."""
    ids = obj["id"]
    sizes = obj["size"]
    cats = []
    for d in ids:
        index = obj["dimension"][d]["category"]["index"]
        if isinstance(index, dict):
            codes = [c for c, _ in sorted(index.items(), key=lambda kv: kv[1])]
        else:
            codes = list(index)
        cats.append(codes)
    values = obj.get("value", {})
    if isinstance(values, list):
        values = {i: v for i, v in enumerate(values) if v is not None}
    else:
        values = {int(k): v for k, v in values.items()}
    rows = []
    for pos, combo in enumerate(itertools.product(*cats)):
        if pos in values:
            rows.append((*combo, values[pos]))
    assert [len(c) for c in cats] == list(sizes)
    return pd.DataFrame(rows, columns=[*ids, "value"])


def fetch_dataset(dataset, since=None, timeout=120, **filters):
    """Download one dataset. Filters are dimension=value (value may be a list), e.g.
    fetch_dataset('nama_10_gdp', geo=['BE','NL'], na_item='B1GQ', unit='CLV10_MEUR', since=2009).
    Untested in sandbox; validated in CI."""
    params = [("format", "JSON"), ("lang", "EN")]
    if since is not None:
        params.append(("sinceTimePeriod", str(since)))
    for k, v in filters.items():
        for item in (v if isinstance(v, (list, tuple)) else [v]):
            params.append((k, item))
    r = requests.get(BASE + dataset, params=params, timeout=timeout)
    r.raise_for_status()
    return parse_jsonstat(r.json())


def to_series_by_geo(df, time_col="time", geo_col="geo"):
    """Tidy frame filtered to one series per geo -> {geo: {year: value}}."""
    out = {}
    for geo, g in df.groupby(geo_col):
        out[geo] = {int(str(t)[:4]): v for t, v in zip(g[time_col], g["value"])}
    return out
