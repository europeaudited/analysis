"""JRC ARDECO regional data (CSV export).

fetch_variable() needs internet. UNTESTED IN SANDBOX; VALIDATED IN CI.
parse_csv() is pure and is unit-tested offline.
"""
import io

import pandas as pd
import requests

URL = "https://territorial.ec.europa.eu/ardeco-api-v2/rest/export/{var}?version={version}&unit={unit}&level_id=2"
COLUMNS = ["NAME_HTML", "TERRITORY_ID", "LEVEL_ID", "DATE", "VERSIONS", "UNIT", "VALUE", "YEAR"]


def parse_csv(text):
    """Parse the export. Region names can contain commas, so split from the right:
    the last seven fields are fixed and everything before them is the name."""
    rows = []
    lines = [ln for ln in io.StringIO(text).read().splitlines() if ln.strip()]
    for ln in lines[1:]:
        parts = ln.rsplit(",", 7)
        if len(parts) != 8:
            raise ValueError(f"Unexpected ARDECO row: {ln[:80]}")
        parts = [p.strip().strip('"') for p in parts]
        rows.append(parts)
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
    df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce").astype("Int64")
    return df


def fetch_variable(var, unit, version=2024, timeout=180):
    """Download one variable at NUTS2. Untested in sandbox; validated in CI."""
    r = requests.get(URL.format(var=var, version=version, unit=requests.utils.quote(unit)), timeout=timeout)
    r.raise_for_status()
    df = parse_csv(r.text)
    df.insert(0, "var", var)
    return df


def to_wide(df, geos):
    """Long frame (var, TERRITORY_ID, YEAR, VALUE) -> wide frame var,geo,1980,1981,..."""
    d = df[df["TERRITORY_ID"].isin(geos)]
    w = d.pivot_table(index=["var", "TERRITORY_ID"], columns="YEAR", values="VALUE", aggfunc="first")
    w = w.reset_index().rename(columns={"TERRITORY_ID": "geo"})
    w.columns = [str(c) for c in w.columns]
    return w
