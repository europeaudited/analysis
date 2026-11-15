"""Belgium deficit piece: theme bridge, robustness, 2026-2035 scenarios and charts.

    python 2026-11-belgium-deficit/run.py            # rerun from cached data (default)
    python 2026-11-belgium-deficit/run.py --refresh  # re-download raw data first (needs internet)

Reads data/raw/*.csv next to this file, checks them against data/MANIFEST.sha256,
writes outputs/*.csv and charts/*.png. Nothing here depends on the working directory.
"""
import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from lib.decompose import lmdi  # noqa: E402
from lib import style  # noqa: E402
from pipelines import cache  # noqa: E402

RAW = HERE / "data" / "raw"
OUT = HERE / "outputs"
CHARTS = HERE / "charts"
CN = {"BE": "Belgium", "NL": "Netherlands", "DE": "Germany"}


# ---------------------------------------------------------------- data ---------
def load_inputs():
    eurostat_path = cache.verified_path(RAW / "eurostat_waterfall_inputs.csv")
    ameco_path = cache.verified_path(RAW / "ameco_fiscal_cycle_BE_NL_DE.csv")
    rows = {}
    with open(eurostat_path) as f:
        for line in f:
            p = line.strip().split(",")
            ind, geo, fy = p[0], p[1], int(p[2])
            rows[(ind, geo)] = {fy + i: (float(v) if v != "" else np.nan) for i, v in enumerate(p[3:])}
    am = {}
    with open(ameco_path) as f:
        for r in csv.DictReader(f):
            am[(r["code"], r["country"])] = {int(k[1:]): (float(v) if v else np.nan)
                                              for k, v in r.items() if k.startswith("y")}
    return rows, am


# ------------------------------------------------------- 1. theme bridge ------
# Change in the general government balance (% of GDP) split into big themes.
# The split is an exact accounting identity (ties to Eurostat revenue minus expenditure):
#   balance/Y = [L + C + K + NT]/Y - [PEN + HEA + SIC + OTH]/Y - INT/Y
#   L/Y   = (L/D1) * (D1/Y)         labour tax + SSC: rate -> tax ratio; wage share -> growth theme
#   C/Y   = (C/Cn) * (Cn/Y)         indirect taxes: rate -> tax ratio; consumption share -> growth
#   PEN/Y = (P65/P) * (PENr/P65) / (Yr/P)   share 65+ -> ageing; real pension per 65+ -> spending per beneficiary
#   X/Y   = (Xr/P) / (Yr/P) for health, sickness/disability, other primary spending
#   Yr/P  = (W/P) * (E/W) * (H/E) * (Yr/H)  W/P -> ageing; E/W, H/E -> jobs; Yr/H -> productivity
# The cycle (AMECO actual minus cyclically adjusted balance) is carved out of the growth theme.
# Real = deflated by the GDP deflator. Each product is split with the LMDI helper in lib/decompose.py.
# "Spending per beneficiary" is measured against a frozen real benchmark, so it includes automatic
# drift (indexation, welfare adjustment, health norm, pension maturation, relative prices).
class Data:
    def __init__(self):
        self.rows, self.am = load_inputs()

    def g(self, ind, geo, y):
        return self.rows[(ind, geo)].get(y, np.nan)

    def parts(self, geo, y):
        g = lambda ind, yy=y: self.g(ind, geo, yy)  # noqa: E731
        Y = g("gdp_cp_meur"); Yr = g("gdp_clv10_meur"); d = Y / Yr
        P = (g("pop_jan") + g("pop_jan", y + 1)) / 2
        P65 = P * g("pc_65_plus") / 100
        W = g("lfs_emp_20_64_ths") * 1000 / (g("lfs_emp_rate_20_64") / 100)
        E = g("employment_ths_per") * 1000
        H = g("hours_ths") * 1000
        Lt = g("tax_hh_income") + g("tax_ssc_net")
        C = g("tax_production_imports")
        T = g("tax_total")
        TR = g("gov_TR"); TE = g("gov_TE"); INT = g("gov_interest")
        PEN = g("exp_old_age") + g("exp_survivors")
        HEA = g("exp_health"); SIC = g("exp_sick_disab")
        OTH = TE - INT - PEN - HEA - SIC
        D1 = g("comp_employees_cp"); Cn = g("hh_consumption_cp")
        return dict(Y=Y, Yr=Yr, d=d, P=P, P65=P65, W=W, E=E, H=H, L=Lt, C=C, K=T - Lt - C, NT=TR - T,
                    TR=TR, TE=TE, INT=INT, PEN=PEN, HEA=HEA, SIC=SIC, OTH=OTH, D1=D1, Cn=Cn)

    def bridge(self, geo, a, b):
        A, B = self.parts(geo, a), self.parts(geo, b)
        c = {}

        def gdpph(S):
            return dict(dem_wap=S["W"] / S["P"], jobs_emp=S["E"] / S["W"],
                        jobs_hours=S["H"] / S["E"], prod=S["Yr"] / S["H"])

        # revenue side (positive = improves the balance)
        for k, (num, base) in {"L": ("L", "D1"), "C": ("C", "Cn")}.items():
            f0 = {"rate": A[num] / A[base], "share": A[base] / A["Y"]}
            f1 = {"rate": B[num] / B[base], "share": B[base] / B["Y"]}
            for kk, v in lmdi(A[num] / A["Y"] * 100, B[num] / B["Y"] * 100, f0, f1).items():
                c[f"rev_{k}_{kk}"] = v
        c["rev_other_taxes_K"] = (B["K"] / B["Y"] - A["K"] / A["Y"]) * 100
        c["rev_nontax"] = (B["NT"] / B["Y"] - A["NT"] / A["Y"]) * 100
        # spending side (sign flipped: a higher spending ratio worsens the balance)
        for k in ["PEN", "HEA", "SIC", "OTH"]:
            vol = "P65" if k == "PEN" else "P"

            def fac(S, k=k, vol=vol):
                f = {"per_benef": (S[k] / S["d"]) / S[vol]}
                if k == "PEN":
                    f["share65"] = S["P65"] / S["P"]
                for kk, v in gdpph(S).items():
                    f[kk] = 1 / v
                return f

            for kk, v in lmdi(A[k] / A["Y"] * 100, B[k] / B["Y"] * 100, fac(A), fac(B)).items():
                c[f"sp_{k}_{kk}"] = -v
        c["interest"] = -(B["INT"] / B["Y"] - A["INT"] / A["Y"]) * 100
        db = (B["TR"] - B["TE"]) / B["Y"] * 100 - (A["TR"] - A["TE"]) / A["Y"] * 100
        assert abs(sum(c.values()) - db) < 1e-6, (geo, a, b, sum(c.values()), db)

        am = self.am
        cyc = lambda y: am[("UBLG_pctGDP", CN[geo])][y] - am[("UBLGAP_CAB_pctPotGDP", CN[geo])][y]  # noqa: E731
        dcyc = cyc(b) - cyc(a)
        th = {}
        th["1 Demography (ageing)"] = c["sp_PEN_share65"] + sum(v for k, v in c.items() if k.endswith("dem_wap"))
        jobs = sum(v for k, v in c.items() if "jobs_" in k)
        prod = sum(v for k, v in c.items() if k.endswith("_prod"))
        struct = c["rev_L_share"] + c["rev_C_share"]
        th["2 Growth: jobs & hours"] = jobs
        th["2 Growth: productivity"] = prod
        th["2 Growth: wage/consumption share of GDP"] = struct
        th["3 Tax ratio: labour (tax+SSC / wages)"] = c["rev_L_rate"]
        th["3 Tax ratio: consumption (indirect taxes / consumption)"] = c["rev_C_rate"]
        th["3 Spending per beneficiary: pension per 65+"] = c["sp_PEN_per_benef"]
        th["3 Spending per beneficiary: health per head"] = c["sp_HEA_per_benef"]
        th["3 Spending per beneficiary: sickness/disability per head"] = c["sp_SIC_per_benef"]
        th["3 Spending per beneficiary: other primary per head"] = c["sp_OTH_per_benef"]
        th["4 Cycle (AMECO cyclical component)"] = dcyc
        th["5 Interest"] = c["interest"]
        th["6 Other taxes & non-tax revenue (mixed)"] = c["rev_other_taxes_K"] + c["rev_nontax"]
        # carve the cycle out of growth, pro rata over jobs and productivity
        gsum = jobs + prod
        for k, v in [("2 Growth: jobs & hours", jobs), ("2 Growth: productivity", prod)]:
            th[k] = v - dcyc * (v / gsum if abs(gsum) > 1e-9 else 0.5)
        assert abs(sum(th.values()) - db) < 1e-6
        yrs = b - a
        meta = dict(
            balance_start=(A["TR"] - A["TE"]) / A["Y"] * 100,
            balance_end=(B["TR"] - B["TE"]) / B["Y"] * 100,
            d_balance=db,
            gdp_end_bn=B["Y"] / 1000,
            real_gdp_per_head_growth_pa=((B["Yr"] / B["P"]) / (A["Yr"] / A["P"])) ** (1 / yrs) * 100 - 100,
            real_primary_spend_per_head_growth_pa=(((B["TE"] - B["INT"]) / B["d"] / B["P"])
                                                   / ((A["TE"] - A["INT"]) / A["d"] / A["P"])) ** (1 / yrs) * 100 - 100)
        return th, c, meta


def run_theme_bridge(data):
    out, det = [], []
    for geo in ["BE", "NL", "DE"]:
        for a, b in [(2010, 2019), (2019, 2024), (2010, 2024)]:
            th, c, m = data.bridge(geo, a, b)
            for k, v in th.items():
                out.append(dict(geo=geo, period=f"{a}-{b}", theme=k, pp_gdp=round(v, 2),
                                eur_bn_at_end_gdp=round(v * m["gdp_end_bn"] / 100, 1)))
            for k, v in m.items():
                out.append(dict(geo=geo, period=f"{a}-{b}", theme="META " + k, pp_gdp=round(v, 2), eur_bn_at_end_gdp=""))
            for k, v in c.items():
                det.append(dict(geo=geo, period=f"{a}-{b}", component=k, pp_gdp=round(v, 3)))
    df = pd.DataFrame(out)
    df.to_csv(OUT / "theme_bridge.csv", index=False)
    pd.DataFrame(det).to_csv(OUT / "theme_bridge_detail.csv", index=False)
    return df


# ------------------------------------------------------- 2. robustness --------
# (a) tax-rate effect split labour vs consumption, (b) a second benchmark where spending per
# beneficiary growing with real GDP per head is "neutral", (c) sensitivity to start and end year.
def run_robustness(data):
    rows = []
    for geo in ["BE", "NL", "DE"]:
        for a, b in [(2010, 2024), (2011, 2024), (2010, 2023), (2012, 2024), (2010, 2019), (2019, 2024)]:
            th, c, m = data.bridge(geo, a, b)
            sp_rate = sum(v for k, v in c.items() if k.endswith("per_benef"))
            sp_growth = sum(v for k, v in c.items() if k.startswith("sp_") and ("jobs_" in k or k.endswith("_prod")))
            rows.append(dict(
                geo=geo, period=f"{a}-{b}", d_balance=round(m["d_balance"], 2),
                demography=round(th["1 Demography (ageing)"], 2),
                spend_per_benef_vs_frozen_real=round(sp_rate, 2),
                spend_per_benef_vs_income_per_head=round(sp_rate + sp_growth, 2),
                labour_tax_ratio=round(c["rev_L_rate"], 2), consumption_tax_ratio=round(c["rev_C_rate"], 2),
                interest=round(th["5 Interest"], 2)))
    r = pd.DataFrame(rows)
    r.to_csv(OUT / "theme_bridge_robustness.csv", index=False)
    return r


# ------------------------------------------------------- 3. scenarios ---------
# Belgium 2026-2035, general government, % of GDP. Simple and transparent.
# Baseline: Federal Planning Bureau outlook (Feb 2026: 4.9, 5.1, 5.2, 5.7, 6.2, 6.3 for 2026-31),
# shifted to 5.1 (2026) and 6.4 (2031) for the later FPB revision; 2032-35 drift of +0.10 pp a year
# (central) or +0.20 (high) is OUR ASSUMPTION. The baseline excludes the NATO path to 3.5% of GDP
# on defence (a risk of up to +1.5 pp).
# Debt: 2025 = 107.9 (AMECO); d_t = d_(t-1) / (1 + g_t) + deficit_t; g = 3.1% nominal baseline,
# growth levers raise g.
# Levers (balance effect, % of GDP, against the baseline):
#   SPENDING CUTS: 0.4% of GDP a year 2027-31 (2.0% in total); first-year yield 70%.
#   REVENUE:       trimming tax breaks 0.25% a year 2028-31 (1.0% in total); same first-year yield.
#   JOBS:          +3 pp employment above baseline by 2035, linear from 2027, 0.25% of GDP per pp
#                  (LOW confidence, derived); adds ~0.35 pp a year to real GDP while ramping.
#   PRODUCTIVITY:  +0.3 pp a year from 2028; balance +0.06 pp a year, cumulating (LOW confidence).
# Interest feedback: 3% on the debt avoided.
YEARS = list(range(2025, 2036))
FEB = {2026: 4.9, 2027: 5.1, 2028: 5.2, 2029: 5.7, 2030: 6.2, 2031: 6.3}
GDP_2026_EUR_TRN = 0.66          # approximate 2026 nominal GDP, EUR trillion (assumption)
GOV_PLAN_BN = 10                 # the government's stated savings target by 2029, EUR bn


def baseline(drift):
    b = {2025: 5.2}
    for y in range(2026, 2032):
        b[y] = FEB[y] + 0.2 + (0.1 - 0.2) * (y - 2026) / 5
    for y in range(2032, 2036):
        b[y] = b[y - 1] + drift
    return b


def ramp(y, start, end, per, first=0.7, scale=1.0):
    return sum(per * scale * (first if y == k else 1.0) for k in range(start, end + 1) if y >= k)


cuts = lambda y, s=1.0: ramp(y, 2027, 2031, 0.4, scale=s)  # noqa: E731
rev = lambda y, s=1.0: ramp(y, 2028, 2031, 0.25, scale=s)  # noqa: E731
jobs = lambda y: 0 if y < 2027 else 3.0 * min(1, (y - 2026) / 9) * 0.25  # noqa: E731
jobs_g = lambda y: 0.0035 if 2027 <= y <= 2035 else 0  # noqa: E731
prod = lambda y: 0 if y < 2028 else 0.06 * (y - 2027)  # noqa: E731
prod_g = lambda y: 0.003 if y >= 2028 else 0  # noqa: E731

SC = {
    "1 No change": (lambda y: 0, lambda y: 0),
    "2 Cuts only (2% GDP spending)": (lambda y: cuts(y), lambda y: 0),
    "3 Growth only (jobs + productivity)": (lambda y: jobs(y) + prod(y), lambda y: jobs_g(y) + prod_g(y)),
    "4 Mix (1% cuts + growth)": (lambda y: cuts(y, 0.5) + jobs(y) + prod(y), lambda y: jobs_g(y) + prod_g(y)),
    "5 Big mix (2% cuts + 1% revenue + growth)": (lambda y: cuts(y) + rev(y) + jobs(y) + prod(y),
                                                   lambda y: jobs_g(y) + prod_g(y)),
}


def run_drift(drift):
    base = baseline(drift)
    out = []
    for name, (f, gx) in SC.items():
        db = 107.9
        d = 107.9
        for y in YEARS:
            if y == 2025:
                out.append(dict(drift=drift, scenario=name, year=y, deficit=base[y], debt=d, lever=0))
                continue
            db = db / 1.031 + base[y]
            lev = f(y)
            isave = max(0, (db - d)) * 0.03
            dfc = base[y] - lev - isave
            d = d / (1.031 + gx(y)) + dfc
            out.append(dict(drift=drift, scenario=name, year=y, deficit=round(dfc, 2), debt=round(d, 1), lever=round(lev, 2)))
    return pd.DataFrame(out)


def run_scenarios():
    df = pd.concat([run_drift(0.10), run_drift(0.20)])
    df.to_csv(OUT / "scenarios_2026_2035.csv", index=False)
    # What it takes: measures needed (before interest feedback) = baseline deficit minus the target.
    b = baseline(0.10)
    rows = []
    for label, tgt, yr in [("deficit 3% in 2029", 3.0, 2029), ("deficit 3% in 2031", 3.0, 2031),
                           ("deficit 1% in 2032", 1.0, 2032), ("balanced budget in 2032", 0.0, 2032)]:
        need = b[yr] - tgt
        rows.append(dict(target=label, year=yr, measures_pp_gdp=round(need, 2),
                         eur_bn_at_2026_gdp=round(need * GDP_2026_EUR_TRN * 10, 1)))
    wit = pd.DataFrame(rows)
    wit.to_csv(OUT / "what_it_takes.csv", index=False)
    return df, wit


# ------------------------------------------------------- 4. charts ------------
def chart_same_ageing_bill(tb):
    def pick(geo, theme):
        s = tb[(tb.geo == geo) & (tb.period == "2010-2024") & (tb.theme == theme)].pp_gdp
        return float(s.iloc[0])
    be = [pick("BE", "1 Demography (ageing)"), pick("BE", "META d_balance")]
    nl = [pick("NL", "1 Demography (ageing)"), pick("NL", "META d_balance")]
    fig = style.frame("Same ageing bill, different result",
                      "Belgium and the Netherlands, 2010-2024, % of GDP (negative = worse budget)",
                      "Sources: Eurostat; authors' calculations. Ageing = cost of more over-65s and fewer people of working age.")
    ax = style.main_axes(fig)
    x = [0, 1]; w = 0.36
    ax.set_ylim(-5.5, 6)
    b1 = ax.bar([i - w / 2 for i in x], be, w, color=style.ACCENT, label="Belgium")
    b2 = ax.bar([i + w / 2 for i in x], nl, w, color=style.SECOND, label="Netherlands")
    style.label_bars(ax, b1); style.label_bars(ax, b2)
    ax.set_xticks(x); ax.set_xticklabels(["Cost of ageing", "Change in budget balance"], fontsize=12)
    ax.axhline(0, color=style.DARK, lw=1); ax.set_yticks([])
    ax.legend(frameon=False, fontsize=11, loc="upper left")
    style.save(fig, CHARTS / "01_same_ageing_bill.png")


def chart_gap_twice_plan(wit):
    v = wit.set_index("target").eur_bn_at_2026_gdp
    lo, hi = float(v["deficit 3% in 2029"]), float(v["deficit 3% in 2031"])
    bal = float(v["balanced budget in 2032"])
    labels = ["On the table\n(federal plan)", "Deficit under 3%\n(debt stops rising)", "Balanced budget\nby 2032"]
    vals = [GOV_PLAN_BN, (lo + hi) / 2, bal]
    texts = [f"€{GOV_PLAN_BN}bn", f"€{round(lo)}-{round(hi)}bn", f"~€{round(bal)}bn"]
    fig = style.frame("The gap is twice the plan", "Annual savings needed, € bn at 2026 prices",
                      "Sources: Federal Planning Bureau; European Commission; authors' model. Government target: "
                      f"€{GOV_PLAN_BN}bn by 2029.")
    ax = style.main_axes(fig, (0.08, 0.16, 0.88, 0.58))
    bars = ax.bar(labels, vals, color=[style.GREY, style.ACCENT, style.LIGHT], width=0.6)
    for r, t in zip(bars, texts):
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 1, t, ha="center", fontsize=14, fontweight="bold")
    ax.set_yticks([]); ax.tick_params(axis="x", labelsize=11.5); ax.set_ylim(0, max(vals) * 1.2)
    style.save(fig, CHARTS / "02_gap_twice_plan.png")


def chart_no_single_fix(sc):
    s = sc[sc.drift == 0.10]
    fig = style.frame("No single fix is enough", "Belgian budget deficit, % of GDP",
                      "Sources: Federal Planning Bureau (baseline to 2031, extended); authors' model. Illustrative.")
    ax = fig.add_axes([0.08, 0.12, 0.66, 0.62])
    for name, col, lab in [("1 No change", style.GREY, "Current policy"),
                           ("2 Cuts only (2% GDP spending)", style.SECOND, "Cuts only\n(~€13bn)"),
                           ("5 Big mix (2% cuts + 1% revenue + growth)", style.ACCENT, "Cuts + fewer tax\nbreaks + more jobs")]:
        d = s[s.scenario == name]
        ax.plot(d.year, d.deficit, color=col, lw=3)
        ax.text(2035.2, d.deficit.iloc[-1], lab, color=col, fontsize=10.5, va="center", fontweight="bold")
    ax.axhline(3, color=style.DARK, lw=1, ls="--")
    ax.text(2025, 2.75, "3%: debt stops rising", fontsize=9.5, color=style.DARK)
    ax.set_xlim(2025, 2035); ax.set_ylim(0, 7.5); ax.grid(axis="y", color=style.GRID); ax.tick_params(labelsize=10)
    style.save(fig, CHARTS / "03_no_single_fix.png")


GROUPS = ["Demography (ageing)", "Growth (jobs, productivity)", "Tax ratio: labour", "Tax ratio: consumption",
          "Spending per beneficiary (policy + drift)", "Cycle", "Interest", "Other taxes & non-tax (mixed)"]


def _group(t):
    if t.startswith("1"):
        return GROUPS[0]
    if t.startswith("2"):
        return GROUPS[1]
    if "labour" in t:
        return GROUPS[2]
    if "consumption" in t:
        return GROUPS[3]
    if t.startswith("3"):
        return GROUPS[4]
    if t.startswith("4"):
        return GROUPS[5]
    if t.startswith("5"):
        return GROUPS[6]
    return GROUPS[7]


def chart_theme_detail(tb):
    df = tb[~tb.theme.str.startswith("META")].copy()
    df["G"] = df.theme.map(_group)
    p = df[df.period == "2010-2024"].pivot_table(index="G", columns="geo", values="pp_gdp", aggfunc="sum").reindex(GROUPS)[["BE", "NL", "DE"]]
    p.round(2).to_csv(OUT / "theme_bridge_summary_2010_2024.csv")
    tot = {g: float(tb[(tb.geo == g) & (tb.period == "2010-2024") & (tb.theme == "META d_balance")].pp_gdp.iloc[0]) for g in ["BE", "NL", "DE"]}
    fig = style.frame("Where the budget balance moved, 2010-2024",
                      "Contribution to the change in balance, % of GDP (negative = worse)\n"
                      "Change in balance: " + ", ".join(f"{g} {v:+.1f}" for g, v in tot.items()),
                      "Eurostat national and government accounts, COFOG; AMECO for the cycle. Spending per beneficiary is real (GDP deflator)\n"
                      "against a frozen benchmark, so it includes indexation and other automatic drift. Results move with start and end years.",
                      figsize=(10, 7.2))
    ax = fig.add_axes([0.30, 0.15, 0.66, 0.62])
    y = np.arange(len(GROUPS)); w = 0.27
    for k, (geo, col) in enumerate([("BE", style.ACCENT), ("NL", style.SECOND), ("DE", style.GREY)]):
        ax.barh(y + (k - 1) * w, p[geo], height=w, color=col, label=CN[geo])
    ax.set_yticks(y); ax.set_yticklabels(GROUPS, fontsize=10); ax.invert_yaxis()
    ax.axvline(0, color=style.DARK, lw=0.8); ax.grid(axis="x", color=style.GRID); ax.tick_params(axis="x", labelsize=10)
    ax.legend(frameon=False, fontsize=10, ncol=3, loc="upper left", bbox_to_anchor=(0.0, -0.06))
    style.save(fig, CHARTS / "theme_bridge_detail.png")


# ------------------------------------------------------- 5. checks ------------
def check_key_numbers(tb, sc, rb):
    """Regression guard for the published numbers. Skipped after --refresh, when data may move."""
    def tbv(geo, theme):
        return float(tb[(tb.geo == geo) & (tb.period == "2010-2024") & (tb.theme == theme)].pp_gdp.iloc[0])

    def d2035(scn, drift=0.10):
        s = sc[(sc.drift == drift) & (sc.scenario == scn) & (sc.year == 2035)]
        return float(s.deficit.iloc[0])

    expected = [
        ("BE demography 2010-24", tbv("BE", "1 Demography (ageing)"), -3.82),
        ("BE change in balance", tbv("BE", "META d_balance"), -0.27),
        ("NL change in balance", tbv("NL", "META d_balance"), 4.57),
        ("2035 deficit, no change", round(d2035("1 No change"), 1), 6.7),
        ("2035 deficit, growth only", round(d2035("3 Growth only (jobs + productivity)"), 1), 5.2),
        ("2035 deficit, mix", round(d2035("4 Mix (1% cuts + growth)"), 1), 4.0),
        ("2035 deficit, big mix", round(d2035("5 Big mix (2% cuts + 1% revenue + growth)"), 1), 1.7),
    ]
    cuts_only = round(d2035("2 Cuts only (2% GDP spending)"), 1)
    ok = cuts_only in (4.3, 4.4)
    print(f"{'2035 deficit, cuts only':32s} {cuts_only:>7} (expected 4.3 or 4.4) {'ok' if ok else 'MISMATCH'}")
    bad = [] if ok else ["cuts only"]
    for name, got, want in expected:
        flag = "ok" if abs(got - want) < 0.005 else "MISMATCH"
        print(f"{name:32s} {got:>7} (expected {want}) {flag}")
        if flag != "ok":
            bad.append(name)
    if bad:
        raise SystemExit(f"Key numbers changed: {bad}")


def eu_context():
    """EU context for the post: how many EU27 countries breach 3% and 100% in 2025."""
    rows = list(csv.DictReader(open(cache.verified_path(RAW / "eurostat_edp_2024_2025.csv"))))
    members = [r for r in rows if r["geo"] not in ("EU27_2020", "EA20")]
    assert len(members) == 27
    over3 = sorted(r["geo"] for r in members if float(r["deficit_2025"]) < -3.0)
    over100 = sorted(r["geo"] for r in members if float(r["debt_2025"]) > 100.0)
    be = next(r for r in rows if r["geo"] == "BE")
    with open(OUT / "eu_context_2025.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["measure", "value", "countries"])
        w.writerow(["eu27_deficit_above_3pct_2025", len(over3), " ".join(over3)])
        w.writerow(["eu27_debt_above_100pct_2025", len(over100), " ".join(over100)])
        w.writerow(["be_deficit_2025", be["deficit_2025"], "BE"])
        w.writerow(["be_debt_2025", be["debt_2025"], "BE"])
    assert len(over3) == 10 and len(over100) == 5, (over3, over100)
    assert float(be["deficit_2025"]) == -5.2 and float(be["debt_2025"]) == 108.1


def chart_deficit_history():
    """Belgium and the Netherlands, budget balance 2009 to 2027 (AMECO; 2026-27 are forecasts)."""
    rows = list(csv.reader(open(cache.verified_path(RAW / "ameco_fiscal_cycle_BE_NL_DE.csv"))))
    head = rows[0]
    years = [int(h[1:]) for h in head[2:]]
    series = {r[1]: [float(x) for x in r[2:]] for r in rows[1:] if r[0] == "UBLG_pctGDP"}
    be, nl = series["Belgium"], series["Netherlands"]
    actual = [y for y in years if y <= 2025]
    under3 = [y for y, v in zip(years, be) if y <= 2025 and v > -3.0]
    with open(OUT / "deficit_history.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "belgium_balance_pct_gdp", "netherlands_balance_pct_gdp", "forecast"])
        for y, b, n in zip(years, be, nl):
            w.writerow([y, b, n, int(y > 2025)])
    with open(OUT / "deficit_history_summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["measure", "value"])
        w.writerow(["years_2009_2025", len(actual)])
        w.writerow(["belgium_years_deficit_below_3pct_2009_2025", len(under3)])
        w.writerow(["belgium_years_below_3pct", " ".join(map(str, under3))])
    assert len(actual) == 17 and under3 == [2015, 2016, 2017, 2018, 2019], under3
    fig = style.frame("Belgium met the 3% limit in 5 of 17 years",
                      "General government balance, % of GDP, 2009 to 2025; shaded: forecasts",
                      "Source: European Commission, AMECO. Dashed line: the EU's 3% deficit limit.", figsize=(8, 6))
    ax = style.main_axes(fig, (0.09, 0.12, 0.86, 0.64))
    ax.axvspan(2025.5, 2027.4, color=style.GRID, zorder=0)
    ax.axhline(-3, color=style.DARK, lw=1, ls="--")
    ax.axhline(0, color=style.LIGHT, lw=1)
    ax.plot(years, nl, color=style.SECOND, lw=2)
    ax.plot(years, be, color=style.ACCENT, lw=3)
    ax.text(2027.5, be[-1], "Belgium", color=style.ACCENT, fontsize=12, fontweight="bold", va="center")
    ax.text(2027.5, nl[-1], "Netherlands", color=style.SECOND, fontsize=11, va="center")
    ax.text(2009.2, -2.7, "3% limit", fontsize=10, color=style.DARK)
    ax.set_xlim(2008.5, 2030); ax.set_ylim(-10, 3)
    ax.set_xticks([2009, 2012, 2015, 2018, 2021, 2024, 2027])
    ax.grid(axis="y", color=style.GRID); ax.tick_params(labelsize=10)
    style.save(fig, CHARTS / "05_deficit_history.png")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true", help="re-download raw data first (needs internet)")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True); CHARTS.mkdir(exist_ok=True)
    if args.refresh:
        import refresh  # untested in sandbox; validated in CI
        refresh.refresh(RAW)
        cache.write_manifest(HERE / "data")
    data = Data()
    tb = run_theme_bridge(data)
    rb = run_robustness(data)
    sc, wit = run_scenarios()
    chart_same_ageing_bill(tb)
    chart_gap_twice_plan(wit)
    chart_no_single_fix(sc)
    chart_theme_detail(tb)
    pd.set_option("display.width", 250)
    print(tb.pivot_table(index="theme", columns=["geo", "period"], values="pp_gdp", aggfunc="first", sort=False).round(2).to_string())
    print(rb.to_string(index=False))
    print(wit.to_string(index=False))
    if not args.refresh:
        check_key_numbers(tb, sc, rb)
    eu_context()
    chart_deficit_history()
    print("done: outputs/ and charts/ written")


if __name__ == "__main__":
    main()
