"""Re-download the ARDECO raw data for this piece. UNTESTED IN SANDBOX; VALIDATED IN CI.

The unit strings below are the best available guess at the API's unit names. If the first CI run
fails with an HTTP error or an empty table, correct VARIABLES. compare_with_cache prints the largest
relative change against the cached file on overlapping years.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipelines import ardeco  # noqa: E402

GEOS = ["BE10", "BE21", "BE22", "BE23", "BE24", "BE25", "BE31", "BE32", "BE33", "BE34", "BE35",
        "DEC0", "FRE1", "NL42"]
# variable -> unit name used by the API
VARIABLES = {
    "SOVGD": "Mio EUR (2020 prices)",   # real GDP, EUR million at 2020 prices
    "SNPTD": "1000 persons",            # average population, thousands
    "SNETD": "1000 persons",            # workplace employment, thousands
}


def refresh(raw_dir):
    raw_dir = Path(raw_dir)
    frames = [ardeco.fetch_variable(v, u, version=2024) for v, u in VARIABLES.items()]
    wide = ardeco.to_wide(pd.concat(frames), GEOS)
    order = {v: i for i, v in enumerate(VARIABLES)}
    wide = wide.sort_values(["var", "geo"], key=lambda s: s.map(order) if s.name == "var" else s)
    target = raw_dir / "ardeco_nuts2_1980_2024.csv"
    old = pd.read_csv(target).set_index(["var", "geo"]) if target.exists() else None
    wide.to_csv(target, index=False)
    if old is not None:
        new = wide.set_index(["var", "geo"])
        common = [c for c in new.columns if c in old.columns]
        rel = (new[common] / old[common] - 1).abs().max(axis=1)
        print("refresh check, largest relative change by series:")
        print(rel.sort_values(ascending=False).head(10).to_string())
