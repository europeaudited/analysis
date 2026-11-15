"""France deficit piece: record since 2009, spending and revenue, theme bridge 2010-2024 and charts.

    python 2026-11-france-deficit/run.py      # rerun from cached data

Reuses the theme-bridge method of 2026-11-belgium-deficit/run.py (same identity, same LMDI split),
applied to France. Reads data/raw/*.csv next to this file, checks them against data/MANIFEST.sha256,
writes outputs/*.csv and charts/*.png.
"""
import csv
import importlib.util
from decimal import Decimal, ROUND_HALF_UP
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from lib import style  # noqa: E402
from pipelines import cache  # noqa: E402

RAW = HERE / "data" / "raw"
OUT = HERE / "outputs"
CHARTS = HERE / "charts"

# the Belgium piece holds the bridge method; import it as a module
_spec = importlib.util.spec_from_file_location("bel", HERE.parent / "2026-11-belgium-deficit" / "run.py")
bel = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bel)
bel.CN["FR"] = "France"


def r1(v):
    """Round half away from zero to one decimal, as in the text."""
    return float(Decimal(str(round(v, 4))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def load_ameco(name):
    am = {}
    for r in csv.DictReader(open(cache.verified_path(RAW / name))):
        am[(r["code"], r["country"])] = {int(k[1:]): (float(v) if v else np.nan) for k, v in r.items() if k.startswith("y")}
    return am


def make_data():
    d = bel.Data.__new__(bel.Data)
    rows = {}
    for line in open(cache.verified_path(RAW / "eurostat_waterfall_inputs.csv")):
        p = line.strip().split(",")
        rows[(p[0], p[1])] = {int(p[2]) + i: (float(v) if v != "" else np.nan) for i, v in enumerate(p[3:])}
    d.rows = rows
    d.am = {**load_ameco("ameco_fiscal_cycle_BE_NL_DE.csv"), **load_ameco("ameco_fiscal_FR.csv")}
    return d


def bridge_tables(data):
    out, rob = [], []
    for geo in ["FR", "BE", "NL"]:
        for a, b in [(2010, 2019), (2019, 2024), (2010, 2024), (2012, 2024)]:
            th, c, m = data.bridge(geo, a, b)
            for k, v in th.items():
                out.append(dict(geo=geo, period=f"{a}-{b}", theme=k, pp_gdp=round(v, 2)))
            out.append(dict(geo=geo, period=f"{a}-{b}", theme="META d_balance", pp_gdp=round(m["d_balance"], 2)))
            sp_rate = sum(v for k, v in c.items() if k.endswith("per_benef"))
            sp_growth = sum(v for k, v in c.items() if k.startswith("sp_") and ("jobs_" in k or k.endswith("_prod")))
            rob.append(dict(geo=geo, period=f"{a}-{b}", d_balance=round(m["d_balance"], 2),
                            demography=round(th["1 Demography (ageing)"], 2),
                            spend_per_benef_vs_frozen_real=round(sp_rate, 2),
                            spend_per_benef_vs_income_per_head=round(sp_rate + sp_growth, 2),
                            labour_tax_ratio=round(c["rev_L_rate"], 2), consumption_tax_ratio=round(c["rev_C_rate"], 2),
                            interest=round(th["5 Interest"], 2)))
    tb = pd.DataFrame(out); tb.to_csv(OUT / "theme_bridge.csv", index=False)
    rb = pd.DataFrame(rob); rb.to_csv(OUT / "theme_bridge_robustness.csv", index=False)
    return tb, rb


def shares_and_record(data):
    out = []
    for geo in ("FR", "BE", "NL", "DE"):
        for y in range(2009, 2026):
            gdp = data.rows[("gdp_cp_meur", geo)][y]
            te, tr = data.rows[("gov_TE", geo)][y], data.rows[("gov_TR", geo)][y]
            pen = data.rows[("exp_old_age", geo)].get(y, np.nan) + data.rows[("exp_survivors", geo)].get(y, np.nan)
            out.append(dict(geo=geo, year=y, spending_pct_gdp=round(te / gdp * 100, 1),
                            revenue_pct_gdp=round(tr / gdp * 100, 1), balance_pct_gdp=round((tr - te) / gdp * 100, 2),
                            pensions_pct_gdp=round(pen / gdp * 100, 1),
                            share_65_plus=data.rows[("pc_65_plus", geo)].get(y, np.nan)))
    df = pd.DataFrame(out); df.to_csv(OUT / "spending_revenue.csv", index=False)
    rec = []
    for geo, g in df.groupby("geo"):
        above = g[g.balance_pct_gdp < -3.0].year.tolist()
        rec.append(dict(geo=geo, years_2009_2025=len(g), years_deficit_above_3pct=len(above),
                        years_under_3pct=" ".join(str(y) for y in g.year if y not in above)))
    rec = pd.DataFrame(rec); rec.to_csv(OUT / "years_above_3pct.csv", index=False)
    fr = df[df.geo == "FR"].set_index("year")
    assert rec.set_index("geo").loc["FR", "years_deficit_above_3pct"] == 15
    assert rec.set_index("geo").loc["FR", "years_under_3pct"] == "2018 2019"
    assert fr.loc[2010, "pensions_pct_gdp"] == 14.5 and fr.loc[2024, "pensions_pct_gdp"] == 14.7
    assert fr.loc[2010, "share_65_plus"] == 16.6 and fr.loc[2024, "share_65_plus"] == 21.5
    return df, rec


def chart_deficit_history():
    am = load_ameco("ameco_fiscal_FR.csv"); ab = load_ameco("ameco_fiscal_cycle_BE_NL_DE.csv")
    years = list(range(2009, 2026))
    fr = [am[("UBLG_pctGDP", "France")][y] for y in years]
    be = [ab[("UBLG_pctGDP", "Belgium")][y] for y in years]
    with open(OUT / "deficit_history.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["year", "france_balance_pct_gdp", "belgium_balance_pct_gdp", "forecast"])
        for y, a, b in zip(years, fr, be):
            w.writerow([y, a, b, int(y > 2025)])
    fig = style.frame("France met the 3% limit in 2 of 17 years",
                      "General government balance, % of GDP, 2009 to 2025",
                      "Source: European Commission, AMECO. Dashed line: the EU's 3% deficit limit.", figsize=(8, 6))
    ax = style.main_axes(fig, (0.09, 0.12, 0.86, 0.64))
    ax.axhline(-3, color=style.DARK, lw=1, ls="--"); ax.axhline(0, color=style.LIGHT, lw=1)
    ax.plot(years, be, color=style.SECOND, lw=2)
    ax.plot(years, fr, color=style.ACCENT, lw=3)
    ax.text(2025.5, fr[-1] - 0.3, "France", color=style.ACCENT, fontsize=12, fontweight="bold", va="center")
    ax.text(2025.5, be[-1] + 0.4, "Belgium", color=style.SECOND, fontsize=11, va="center")
    ax.text(2009.2, -2.7, "3% limit", fontsize=10, color=style.DARK)
    ax.set_xlim(2008.5, 2028); ax.set_ylim(-10, 3)
    ax.set_xticks([2009, 2012, 2015, 2018, 2021, 2024])
    ax.grid(axis="y", color=style.GRID); ax.tick_params(labelsize=10)
    style.save(fig, CHARTS / "01_deficit_history.png")


def chart_waterfall(tb, shares):
    """France only: from the 2010 balance to the 2024 balance, driver by driver (theme bridge)."""
    p = tb[(tb.geo == "FR") & (tb.period == "2010-2024")].set_index("theme").pp_gdp
    fr = shares[shares.geo == "FR"].set_index("year")
    start, end = float(fr.loc[2010, "balance_pct_gdp"]), float(fr.loc[2024, "balance_pct_gdp"])
    pick = lambda pre: float(sum(v for k, v in p.items() if k.startswith(pre)))  # noqa: E731
    steps = [
        ("Ageing", pick("1 ")),
        ("Spending per\nperson (rules\nand decisions)", pick("3 Spending per beneficiary")),
        ("Economic\ngrowth", pick("2 ")),
        ("Lower\ninterest", pick("5 ")),
        ("Taxes and\nother revenue", pick("3 Tax ratio") + pick("6 ")),
        ("Business\ncycle", pick("4 ")),
    ]
    from_steps = start + sum(v for _, v in steps)
    assert abs(from_steps - end) < 0.05, (from_steps, end)
    with open(OUT / "france_waterfall_2010_2024.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["step", "pp_gdp"]); w.writerow(["balance_2010", round(start, 2)])
        for k, v in steps:
            w.writerow([k.replace("\n", " "), round(v, 2)])
        w.writerow(["balance_2024", round(end, 2)])
    fig = style.frame("What moved France's budget, 2010 to 2024",
                      "Budget balance and what changed it, % of GDP (below zero = deficit; down = worse)",
                      "Sources: Eurostat, AMECO; authors' calculations. Spending per person is real, so it includes indexation\n"
                      "and other automatic rises as well as policy decisions. Results move with start and end years.",
                      figsize=(9, 6.4))
    ax = style.main_axes(fig, (0.08, 0.17, 0.88, 0.58))
    ax.set_axisbelow(True)
    n = len(steps) + 1
    ax.bar(0, start, color=style.SECOND, width=0.6)
    ax.text(0, start - 0.4, f"{r1(start):.1f}", ha="center", va="top", fontsize=11, fontweight="bold")
    level = start
    for i, (_, v) in enumerate(steps, start=1):
        bottom = level if v >= 0 else level + v
        ax.bar(i, abs(v), bottom=bottom, color=style.GREY if v >= 0 else style.ACCENT, width=0.6)
        ax.text(i, bottom + abs(v) + 0.3 if v >= 0 else bottom - 0.3, f"{r1(v):+.1f}",
                ha="center", va="bottom" if v >= 0 else "top", fontsize=11)
        ax.plot([i - 0.7, i + 0.3], [level, level], color=style.LIGHT, lw=1, zorder=0)
        level += v
    ax.plot([n - 0.7, n - 0.3], [level, level], color=style.LIGHT, lw=1, zorder=0)
    ax.bar(n, end, color=style.SECOND, width=0.6)
    ax.text(n, end - 0.4, f"{r1(end):.1f}", ha="center", va="top", fontsize=11, fontweight="bold")
    ax.axhline(0, color=style.DARK, lw=1); ax.axhline(-3, color=style.DARK, lw=1, ls="--")
    ax.text(n + 0.45, -2.8, "3% limit", fontsize=9, va="bottom")
    labels = ["2010\nbalance"] + [k for k, _ in steps] + ["2024\nbalance"]
    ax.set_xticks(range(n + 1)); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(-18, 2); ax.set_xlim(-0.6, n + 1.1)
    ax.grid(axis="y", color=style.GRID); ax.tick_params(axis="y", labelsize=10)
    style.save(fig, CHARTS / "02_france_waterfall.png")
    return steps


# Government figures, typed in with their sources (see data/raw/SOURCES.md):
# 2026 deficit estimate 5.4% and 2027 target 5.0% of GDP: Conseil des ministres communique, 1 Oct 2026.
# 2027 plan: EUR 54bn effort = EUR 43bn of new measures + EUR 11-12bn carried over from 2026 measures;
# without the new measures the deficit would worsen by about 1 point of GDP: 2027 budget press kit (Oct 2026).
# 3% target for 2029: finance minister, Oct 2026; EU Council path of 21 Jan 2025.
GOV = {"deficit_2026": 5.4, "deficit_2027": 5.0, "new_measures_bn": 43, "rise_without_new_measures": 1.0,
       "target_2029": 3.0}


def chart_effort():
    am = load_ameco("ameco_fiscal_FR.csv")
    gdp27 = am[("UVGD_gdp_cp_bn", "France")][2027]
    new_pct = r1(GOV["new_measures_bn"] / gdp27 * 100)
    check = r1(GOV["deficit_2026"] + GOV["rise_without_new_measures"] - new_pct)
    left = r1(GOV["deficit_2027"] - GOV["target_2029"])
    left_bn = left / 100 * gdp27
    with open(OUT / "france_2027_effort.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["item", "pct_gdp", "eur_bn", "note"])
        w.writerow(["deficit_2026_estimate", GOV["deficit_2026"], "", "government, 1 Oct 2026"])
        w.writerow(["rise_without_new_measures_2027", GOV["rise_without_new_measures"], "", "government press kit: about 1 point"])
        w.writerow(["new_measures_2027", -new_pct, GOV["new_measures_bn"], "government; % of 2027 GDP (AMECO)"])
        w.writerow(["deficit_2027_target", GOV["deficit_2027"], "", "government"])
        w.writerow(["still_to_find_by_2029_net", -left, round(left_bn), "2027 target minus 2029 target, at 2027 GDP (AMECO)"])
        w.writerow(["deficit_2029_target", GOV["target_2029"], "", "government"])
        w.writerow(["commission_forecast_2027", -am[("UBLG_pctGDP", "France")][2027], "", "AMECO (Commission forecast, before the 2027 plan)"])
        for y in (2024, 2025, 2026, 2027):
            w.writerow([f"interest_{y}_commission", am[("UYIGE_interest_pctGDP", "France")][y], "", "AMECO, % of GDP"])
    assert new_pct == 1.4 and check == GOV["deficit_2027"] and left == 2.0 and 60 < left_bn < 66, (new_pct, check, left_bn)
    steps = [("2026\nestimate", GOV["deficit_2026"], "total"),
             ("Rise without\nnew measures", GOV["rise_without_new_measures"], "up"),
             ("New measures\n(€43bn)", -new_pct, "down"), ("2027\ntarget", GOV["deficit_2027"], "total"),
             (f"Still to find\nby 2029 (net,\n~€{round(left_bn)}bn)", -left, "down"), ("2029\ntarget", GOV["target_2029"], "total")]
    fig = style.frame("€43bn of new measures buys 0.4 points",
                      "French budget deficit, % of GDP, government figures",
                      "Sources: French government (Conseil des ministres, 1 Oct 2026; 2027 budget press kit); AMECO for GDP.\n"
                      "The government also counts €11bn-12bn from 2026 measures, for a total effort of €54bn.",
                      figsize=(9, 6.2))
    ax = style.main_axes(fig, (0.08, 0.19, 0.88, 0.56)); ax.set_axisbelow(True)
    level = 0
    for i, (lab, v, kind) in enumerate(steps):
        if kind == "total":
            ax.bar(i, v, color=style.SECOND, width=0.6); level = v
            ax.text(i, v + 0.12, f"{v:.1f}%", ha="center", va="bottom", fontsize=12, fontweight="bold")
        else:
            bottom = level if v >= 0 else level + v
            ax.bar(i, abs(v), bottom=bottom, color=style.ACCENT if v > 0 else style.GREY, width=0.6)
            ax.text(i, bottom + abs(v) + 0.12, f"{v:+.1f}", ha="center", va="bottom", fontsize=12)
            level += v
    ax.axhline(3, color=style.DARK, lw=1, ls="--"); ax.text(5.45, 2.75, "3% limit", fontsize=9)
    ax.set_xticks(range(len(steps))); ax.set_xticklabels([s[0] for s in steps], fontsize=9.5)
    ax.set_ylim(0, 7.2); ax.set_xlim(-0.6, 6.1); ax.grid(axis="y", color=style.GRID); ax.tick_params(axis="y", labelsize=10)
    style.save(fig, CHARTS / "03_effort_2027.png")


def main():
    OUT.mkdir(exist_ok=True); CHARTS.mkdir(exist_ok=True)
    data = make_data()
    tb, rb = bridge_tables(data)
    shares, rec = shares_and_record(data)
    chart_deficit_history()
    print(chart_waterfall(tb, shares))
    chart_effort()
    print(tb[tb.period == "2010-2024"].pivot_table(index="theme", columns="geo", values="pp_gdp", sort=False).round(2).to_string())
    print(rb.to_string(index=False))
    print(rec.to_string(index=False))
    print(shares[(shares.geo == "FR") & shares.year.isin([2010, 2013, 2019, 2024, 2025])].to_string(index=False))


if __name__ == "__main__":
    main()
