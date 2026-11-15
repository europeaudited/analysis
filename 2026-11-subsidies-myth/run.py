"""Subsidies myth piece: did EU Objective 1 money (Hainaut, 1994-2006) change Hainaut's path?

    python 2026-11-subsidies-myth/run.py            # rerun from cached data (default)
    python 2026-11-subsidies-myth/run.py --refresh  # re-download raw data first (needs internet)

Compares real GDP per head and jobs per head of Hainaut (BE32) with Liege (BE33, closest industrial
neighbour, Objective 2), the rest of Wallonia excluding Walloon Brabant (BE33+BE34+BE35), Flanders and
Belgium. Periods: before 1980-1993, during 1993-2006, after 2006-2024.
This is a descriptive comparison, not a causal estimate: there is one treated region, the comparison
regions also received EU money, and other policies changed. It can rule out a large effect. It cannot
say how much worse Hainaut would have done without the money.
Pre-1995 ARDECO values are back-casts, not official ESA 2010 data.
"""
import argparse
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from lib import style  # noqa: E402
from pipelines import cache  # noqa: E402

RAW = HERE / "data" / "raw"
OUT = HERE / "outputs"
CHARTS = HERE / "charts"

GROUPS = {
    "Hainaut": ["BE32"],
    "Liege": ["BE33"],
    "Rest of Wallonia ex BW": ["BE33", "BE34", "BE35"],
    "Flanders": ["BE21", "BE22", "BE23", "BE24", "BE25"],
    "Belgium": ["BE10", "BE21", "BE22", "BE23", "BE24", "BE25", "BE31", "BE32", "BE33", "BE34", "BE35"],
    "Limburg BE (Obj.2)": ["BE22"],
    "Saarland": ["DEC0"],
    "Nord-Pas-de-Calais": ["FRE1"],
}
PERIODS = [(1980, 1993), (1993, 2006), (2006, 2019), (2006, 2024)]


class Regions:
    def __init__(self):
        d = cache.load_csv(RAW / "ardeco_nuts2_1980_2024.csv")
        d = d.set_index(["var", "geo"])
        d.columns = d.columns.astype(int)
        self.d = d

    def _sum(self, var, geos):
        return self.d.loc[[(var, g) for g in geos]].sum()

    def gdp_ph(self, geos):      # real GDP per head, EUR thousand (2020 prices)
        return self._sum("SOVGD", geos) / self._sum("SNPTD", geos)

    def jobs_ph(self, geos):     # workplace jobs per head
        return self._sum("SNETD", geos) / self._sum("SNPTD", geos)


def hainaut_test(R):
    rows = []
    be = R.gdp_ph(GROUPS["Belgium"])
    for name, gs in GROUPS.items():
        x, j = R.gdp_ph(gs), R.jobs_ph(gs)
        r = {"region": name}
        for a, b in PERIODS:
            r[f"gdp_ph_growth_pa_{a}_{b}"] = round(((x[b] / x[a]) ** (1 / (b - a)) - 1) * 100, 2)
            r[f"jobs_ph_change_pts_{a}_{b}"] = round((j[b] - j[a]) * 100, 1)
        for y in (1980, 1993, 2006, 2024):
            r[f"gdp_ph_vs_BE_{y}"] = round(x[y] / be[y] * 100, 1)
        rows.append(r)
    T = pd.DataFrame(rows)
    T.to_csv(OUT / "hainaut_objective1_test.csv", index=False)
    idx = pd.DataFrame({n: R.gdp_ph(gs) / be * 100 for n, gs in GROUPS.items()
                        if n in ["Hainaut", "Liege", "Rest of Wallonia ex BW", "Flanders"]})
    idx.to_csv(OUT / "relative_gdp_per_head_index.csv")
    return T, idx


def growth_gaps(R):
    """Annual gap in GDP per head growth (log points a year), Hainaut minus each comparator,
    before, during and after Objective 1, plus the change in Hainaut's index against Belgium."""
    def g(gs, a, b):
        x = R.gdp_ph(gs)
        return math.log(x[b] / x[a]) / (b - a) * 100

    rows = []
    for comp in ["Liege", "Rest of Wallonia ex BW", "Flanders", "Belgium"]:
        gap = lambda a, b, comp=comp: g(GROUPS["Hainaut"], a, b) - g(GROUPS[comp], a, b)  # noqa: E731
        rows.append(dict(comparator=comp, window="before 1980-1993, during 1993-2006, after 2006-2024",
                         gap_before=round(gap(1980, 1993), 2), gap_during=round(gap(1993, 2006), 2),
                         gap_after=round(gap(2006, 2024), 2),
                         did_during_minus_before=round(gap(1993, 2006) - gap(1980, 1993), 2)))
    for a0 in (1985, 1989):    # shift the start of the "before" window
        gap = lambda a, b: g(GROUPS["Hainaut"], a, b) - g(GROUPS["Rest of Wallonia ex BW"], a, b)  # noqa: E731
        rows.append(dict(comparator="Rest of Wallonia ex BW", window=f"before starts {a0}",
                         gap_before=round(gap(a0, 1993), 2), gap_during=round(gap(1993, 2006), 2),
                         gap_after=round(gap(2006, 2024), 2),
                         did_during_minus_before=round(gap(1993, 2006) - gap(a0, 1993), 2)))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "hainaut_growth_gaps.csv", index=False)
    return out


def chart_hainaut(idx):
    fig = style.frame("Aid came, the gap stayed", "Hainaut GDP per person, Belgium = 100",
                      "Sources: JRC ARDECO; authors' calculations. Shaded: EU top-tier regional aid, 1994-2006. "
                      "Before 1995: back-cast data.")
    ax = style.main_axes(fig, (0.08, 0.12, 0.86, 0.62))
    ax.axvspan(1994, 2006, color=style.PALE_ACCENT)
    h = idx["Hainaut"]
    ax.plot(h.index, h, color=style.ACCENT, lw=3.5)
    for y in (1980, 1993, 2006, 2024):
        v = h.loc[y]
        ax.scatter(y, v, color=style.ACCENT, zorder=3)
        ax.text(y, v + 1.2, f"{v:.0f}", ha="center", fontsize=12, fontweight="bold")
    ax.text(2000, 77.5, "EU aid", ha="center", fontsize=10.5, color=style.ACCENT)
    ax.set_ylim(55, 80); ax.grid(axis="y", color=style.GRID); ax.tick_params(labelsize=10)
    style.save(fig, CHARTS / "04_hainaut.png")


def chart_vs_neighbours(idx):
    fig = style.frame("Hainaut against its neighbours, 1980-2024",
                      "Real GDP per head, Belgium = 100",
                      "JRC ARDECO (2024 vintage), NUTS2 real GDP and population. Before 1995: back-casts.\n"
                      "Rest of Wallonia = Liege, Luxembourg, Namur. Shaded: EU Objective 1 for Hainaut, 1994-2006.",
                      figsize=(10, 6))
    ax = style.main_axes(fig, (0.08, 0.14, 0.88, 0.60))
    ax.axvspan(1994, 2006, color=style.PALE_ACCENT)
    for c, col, lab in [("Flanders", style.SECOND, "Flanders"), ("Liege", "#5b9a5b", "Liege"),
                        ("Rest of Wallonia ex BW", style.GREY, "Rest of Wallonia"), ("Hainaut", style.ACCENT, "Hainaut")]:
        ax.plot(idx.index, idx[c], color=col, lw=3 if c == "Hainaut" else 1.8, label=lab)
    ax.axhline(100, color=style.DARK, lw=0.6)
    ax.grid(axis="y", color=style.GRID); ax.tick_params(labelsize=10)
    ax.legend(frameon=False, fontsize=10, loc="lower left")
    style.save(fig, CHARTS / "hainaut_vs_neighbours.png")


def check_key_numbers(T):
    h = T[T.region == "Hainaut"].iloc[0]
    got = [h.gdp_ph_vs_BE_1980, h.gdp_ph_vs_BE_1993, h.gdp_ph_vs_BE_2006, h.gdp_ph_vs_BE_2024]
    want = [74.5, 69.4, 64.8, 61.2]
    for y, a, b in zip((1980, 1993, 2006, 2024), got, want):
        print(f"Hainaut GDP per head vs Belgium {y}: {a} (expected {b}) {'ok' if abs(a - b) < 0.05 else 'MISMATCH'}")
    if any(abs(a - b) >= 0.05 for a, b in zip(got, want)):
        raise SystemExit("Key numbers changed")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true", help="re-download raw data first (needs internet)")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True); CHARTS.mkdir(exist_ok=True)
    if args.refresh:
        import refresh  # untested in sandbox; validated in CI
        refresh.refresh(RAW)
        cache.write_manifest(HERE / "data")
    R = Regions()
    T, idx = hainaut_test(R)
    gaps = growth_gaps(R)
    chart_hainaut(idx)
    chart_vs_neighbours(idx)
    pd.set_option("display.width", 250)
    print(T.T.to_string(header=False))
    print(gaps.to_string(index=False))
    if not args.refresh:
        check_key_numbers(T)
    print("done: outputs/ and charts/ written")


if __name__ == "__main__":
    main()
