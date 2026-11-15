"""Who gets the welfare? Reads data/raw, writes outputs/ and charts/.

    python3 -I run.py     # offline; checks data/MANIFEST.sha256, asserts every number quoted in article.md

Definitions and assumptions:
- Benefits = Eurostat ESSPROS social protection benefits (cash and in kind), 2024. 2025 is an early estimate and
  is shown only as a check (EU27 total differs by 0.2 points of GDP).
- Shares of each euro are computed from the 8-function euro totals (MIO_EUR), which sum to the all-function total.
  Groups: old age and survivors; sickness/health care and disability; family and children; unemployment;
  housing and social exclusion.
- Means-tested = benefits paid only below an income or asset test (Eurostat scheme type MT). Country classification
  differs, so cross-country gaps are partly definitional.
- Belgium has no means-tested split for sickness/health care, survivors and unemployment: its means-tested share is a
  lower bound. Unemployment benefits are counted in full in the generous bound below, so the gap affects only the
  small means-tested part of sickness and survivors.
- 'Generous bound' on 'the poor and the unemployed' = all unemployment, housing and social exclusion benefits plus every
  means-tested benefit in the other functions. It overstates, since most unemployment insurance is not income-tested.
- Poverty rates (60% of median income, survey 2025) before all transfers (ilc_li09), before transfers except pensions
  (ilc_li10, pensions count as income) and after transfers (ilc_li02) come from eurostat_poverty_transfers.csv.
"""
import os, sys, hashlib, shutil
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import textwrap

if "--refresh" in sys.argv:
    print("No network in the default build. Re-pull data/raw per data/raw/*.SOURCES.md, then rerun."); sys.exit(0)
HERE = os.path.dirname(os.path.abspath(__file__))
RAW, OUT, CH = (os.path.join(HERE, d) for d in ("data/raw", "outputs", "charts"))
os.makedirs(OUT, exist_ok=True); os.makedirs(CH, exist_ok=True)
DATA = os.path.join(HERE, "data")
def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
_mf = os.path.join(DATA, "MANIFEST.sha256")
_raw = sorted(f for f in os.listdir(RAW) if f.endswith(".csv"))
if not os.path.exists(_mf):
    open(_mf, "w").write("".join(f"{_sha(os.path.join(RAW, f))}  raw/{f}\n" for f in _raw))
_listed = dict(l.split("  ", 1)[::-1] for l in open(_mf).read().splitlines() if l.strip())
assert set(_listed) == {f"raw/{f}" for f in _raw}, "raw files differ from manifest"
for _rel, _h in _listed.items():
    assert _sha(os.path.join(DATA, _rel)) == _h, f"checksum mismatch: {_rel}"

rd = lambda f: pd.read_csv(os.path.join(RAW, f))
func = rd("esspros_func_pcgdp.csv").set_index("geo")
mts = rd("means_tested_share_2024.csv")
mtf = rd("means_tested_by_function_2024.csv")
pen = rd("pensioners_by_country.csv").set_index("geo")
pov = rd("eurostat_poverty_transfers.csv"); pov = pov[pov.year == 2025].set_index("geo")

GROUPS = {
 "old age and survivors": ["old_age", "survivors"],
 "sickness, health care and disability": ["sickness_healthcare", "disability"],
 "family and children": ["family_children"],
 "unemployment": ["unemployment"],
 "housing and social exclusion": ["housing", "social_exclusion"],
}
mtf = mtf.copy()
rows = []
for geo in ("EU27_2020", "BE"):
    t = mtf[mtf.geo == geo].set_index("function")
    tot = t.total_meur.sum()
    for g, fs in GROUPS.items():
        meur = t.loc[fs, "total_meur"].sum()
        mt = t.loc[fs, "means_tested_meur"].sum(min_count=1)
        rows.append(dict(geo=geo, group=g, total_meur=round(meur, 1), share_of_benefits_pct=100 * meur / tot,
                         means_tested_meur=mt, mt_known=bool(t.loc[fs, "means_tested_meur"].notna().all())))
shares = pd.DataFrame(rows)
# % of GDP by group (ESSPROS, 2024 and 2025 early estimate)
code = {"old age and survivors": "OLD_SRV", "sickness, health care and disability": "SICK_DIS", "family and children": "FAM",
        "unemployment": "UNE", "housing and social exclusion": "HOU_EXCL"}
for y in (2024, 2025):
    shares[f"pc_gdp_{y}"] = [func.loc[r.geo, f"{code[r.group]}_{y}"] for r in shares.itertuples()]
    shares[f"total_pc_gdp_{y}"] = [func.loc[r.geo, f"TOTAL_{y}"] for r in shares.itertuples()]
shares.round(3).to_csv(os.path.join(OUT, "spending_by_function_2024.csv"), index=False, lineterminator="\n")

# means-tested ranked
mt_all = mts[mts.year == 2024].copy()
mt_ranked = mt_all[~mt_all.geo.isin(["EU27_2020"])].sort_values("mt_share_pct", ascending=False)
mt_ranked.to_csv(os.path.join(OUT, "means_tested_ranked_2024.csv"), index=False, lineterminator="\n")

def sh(geo, g): return float(shares[(shares.geo == geo) & (shares.group == g)].share_of_benefits_pct.iloc[0])
def mt_share(geo): return float(mt_all[mt_all.geo == geo].mt_share_pct.iloc[0])

# generous bound: all unemployment + housing + social exclusion + means-tested elsewhere
def generous(geo):
    t = mtf[mtf.geo == geo].set_index("function")
    tot = t.total_meur.sum()
    full = t.loc[["unemployment", "housing", "social_exclusion"], "total_meur"].sum()
    other = t.loc[["sickness_healthcare", "disability", "old_age", "survivors", "family_children"], "means_tested_meur"].sum()
    return 100 * (full + other) / tot
mt_by_fn_eu = mtf[mtf.geo == "EU27_2020"].set_index("function")

F = {}
for geo, k in (("EU27_2020", "EU"), ("BE", "BE")):
    for g, kk in (("old age and survivors", "old_survivors"), ("sickness, health care and disability", "sick_disab"),
                  ("family and children", "family"), ("unemployment", "unemployment"), ("housing and social exclusion", "housing_excl")):
        F[f"{k}_share_{kk}_2024_pct"] = sh(geo, g)
    F[f"{k}_total_pc_gdp_2024"] = float(func.loc[geo, "TOTAL_2024"])
    F[f"{k}_total_pc_gdp_2025"] = float(func.loc[geo, "TOTAL_2025"])
    F[f"{k}_unemployment_pc_gdp_2024"] = float(func.loc[geo, "UNE_2024"])
    F[f"{k}_unemployment_pc_gdp_2025"] = float(func.loc[geo, "UNE_2025"])
    F[f"{k}_mt_share_2024_pct"] = mt_share(geo)
    F[f"{k}_generous_bound_2024_pct"] = generous(geo)
F["EU_mt_unemployment_fn_pct"] = float(mt_by_fn_eu.loc["unemployment", "mt_share_pct"])
F["EU_mt_old_age_fn_pct"] = float(mt_by_fn_eu.loc["old_age", "mt_share_pct"])
F["EU_mt_sickness_fn_pct"] = float(mt_by_fn_eu.loc["sickness_healthcare", "mt_share_pct"])
F["EU_mt_family_fn_pct"] = float(mt_by_fn_eu.loc["family_children", "mt_share_pct"])
F["EU_mt_total_meur"] = float(mt_by_fn_eu.means_tested_meur.sum())
F["EU_mt_unemployment_share_of_all_mt_pct"] = 100 * float(mt_by_fn_eu.loc["unemployment", "means_tested_meur"]) / F["EU_mt_total_meur"]
F["EU_unemployment_total_meur"] = float(mt_by_fn_eu.loc["unemployment", "total_meur"])
F["EU_total_benefits_meur_2024"] = float(mt_all[mt_all.geo == "EU27_2020"].total_benefits_meur.iloc[0])
F["EU_mt_share_2019_pct"] = float(mts[(mts.geo == "EU27_2020") & (mts.year == 2019)].mt_share_pct.iloc[0])
F["mt_max_country_pct"] = float(mt_ranked.mt_share_pct.iloc[0]); F["mt_max_country"] = mt_ranked.geo.iloc[0]
F["DK_mt_share_2024_pct"] = mt_share("DK"); F["IE_mt_share_2024_pct"] = mt_share("IE")
F["n_countries_mt"] = len(mt_ranked)
F["n_countries_mt_below_20pct"] = int((mt_ranked.mt_share_pct < 20).sum())
F["n_countries_mt_below_15pct"] = int((mt_ranked.mt_share_pct < 15).sum())
F["n_countries_mt_above_20pct"] = int((mt_ranked.mt_share_pct >= 20).sum())
F["mt_median_country_pct"] = float(mt_ranked.mt_share_pct.median())
# unemployment benefits in other countries (% GDP, 2024), country rows only
cty = func[~func.index.isin(["EU27_2020"])]
F["max_unemployment_pc_gdp_2024"] = float(cty.UNE_2024.max()); F["max_unemployment_country"] = cty.UNE_2024.idxmax()
F["unemployment_share_of_total_max_country_pct"] = float((100 * cty.UNE_2024 / cty.TOTAL_2024).max())
F["unemployment_share_of_total_max_country"] = (100 * cty.UNE_2024 / cty.TOTAL_2024).idxmax()
F["EU_pension_plus_health_share_pct"] = F["EU_share_old_survivors_2024_pct"] + F["EU_share_sick_disab_2024_pct"]
F["BE_pension_plus_health_share_pct"] = F["BE_share_old_survivors_2024_pct"] + F["BE_share_sick_disab_2024_pct"]
for geo, k in (("EU27_2020", "EU"), ("BE", "BE")):
    F[f"{k}_arop_before_all_transfers_2025"] = float(pov.loc[geo, "arop_before_all_transfers_ilc_li09"])
    F[f"{k}_arop_before_non_pension_transfers_2025"] = float(pov.loc[geo, "arop_before_transfers_except_pensions_ilc_li10"])
    F[f"{k}_arop_after_transfers_2025"] = float(pov.loc[geo, "arop_after_transfers_ilc_li02"])
F["EU_arop_65plus_2025"] = float(pen.loc["EU27_2020", "arop_65p_2025"]); F["EU_arop_total_2025"] = float(pen.loc["EU27_2020", "arop_total_2025"])
F["BE_arop_65plus_2025"] = float(pen.loc["BE", "arop_65p_2025"]); F["BE_arop_total_2025"] = float(pen.loc["BE", "arop_total_2025"])
F["n_countries_65plus_poverty_below_total"] = int((cty.index.isin(pen.index)).sum() and sum(pen.loc[g, "arop_65p_2025"] < pen.loc[g, "arop_total_2025"] for g in cty.index if g in pen.index))
F["n_countries_65plus_poverty_pop"] = int(sum(g in pen.index for g in cty.index))
# consistency checks
for geo, k in (("EU27_2020", "EU"), ("BE", "BE")):
    s = sum(shares[shares.geo == geo].share_of_benefits_pct); assert abs(s - 100) < 0.01, (geo, s)
    gsum = sum(func.loc[geo, f"{c}_2024"] for c in code.values())
    assert abs(gsum - func.loc[geo, "TOTAL_2024"]) < 0.15, ("function sum vs total", geo, gsum)
assert abs(F["EU_total_benefits_meur_2024"] - mt_by_fn_eu.total_meur.sum()) < 5
F["EU_2025_vs_2024_total_diff_pp_gdp"] = F["EU_total_pc_gdp_2025"] - F["EU_total_pc_gdp_2024"]
F["EU_unemployment_2025_vs_2024_diff_pp_gdp"] = F["EU_unemployment_pc_gdp_2025"] - F["EU_unemployment_pc_gdp_2024"]
hn = pd.Series(F, name="value")
hn.to_csv(os.path.join(OUT, "headline_numbers.csv"), header=True, lineterminator="\n")
print(hn.to_string())

# ---------- assertions: numbers quoted in article.md ----------
r1 = lambda k: round(F[k], 1)
assert round(F["EU_share_old_survivors_2024_pct"]) == 47 and round(F["EU_share_sick_disab_2024_pct"]) == 37
assert round(F["EU_share_unemployment_2024_pct"]) == 4 and round(F["BE_share_unemployment_2024_pct"]) == 3
assert round(F["EU_pension_plus_health_share_pct"]) == 84 and round(F["BE_pension_plus_health_share_pct"]) == 86
assert round(F["EU_mt_share_2024_pct"]) == 11 and round(F["BE_mt_share_2024_pct"]) == 6
assert round(F["EU_generous_bound_2024_pct"]) == 14
assert round(F["DK_mt_share_2024_pct"]) == 36 and round(F["IE_mt_share_2024_pct"]) == 26
assert round(F["EU_total_pc_gdp_2024"], 1) == 27.3 and round(F["EU_unemployment_pc_gdp_2024"], 1) == 1.1
assert round(F["EU_mt_unemployment_fn_pct"]) == 20
assert (F["EU_arop_before_all_transfers_2025"], F["EU_arop_before_non_pension_transfers_2025"], F["EU_arop_after_transfers_2025"]) == (42.8, 24.4, 16.3)
assert (F["BE_arop_before_all_transfers_2025"], F["BE_arop_before_non_pension_transfers_2025"], F["BE_arop_after_transfers_2025"]) == (41.6, 23.0, 10.9)
assert F["EU_arop_after_transfers_2025"] == F["EU_arop_total_2025"] and F["BE_arop_after_transfers_2025"] == F["BE_arop_total_2025"]
assert F["EU_arop_65plus_2025"] == F["EU_arop_total_2025"] and F["n_countries_65plus_poverty_below_total"] == 12 and F["n_countries_65plus_poverty_pop"] == 28
assert round(F["EU_arop_before_all_transfers_2025"]) == 43 and round(F["EU_arop_before_non_pension_transfers_2025"]) == 24
assert F["EU_arop_65plus_2025"] == 16.3 and F["BE_arop_65plus_2025"] == 9.3 and F["BE_arop_total_2025"] == 10.9
assert round(F["EU_share_housing_excl_2024_pct"]) == 4 and round(F["EU_share_family_2024_pct"]) == 9
assert round(F["BE_share_old_survivors_2024_pct"]) == 48 and round(F["BE_share_sick_disab_2024_pct"]) == 38
assert round(F["unemployment_share_of_total_max_country_pct"]) == 6 and round(F["EU_total_pc_gdp_2024"]) == 27
assert abs(F["EU_2025_vs_2024_total_diff_pp_gdp"]) < 0.3  # 2025 early estimate not materially different
assert F["mt_max_country"] == "DK" and F["n_countries_mt_above_20pct"] == 3 and F["n_countries_mt"] == 30

# ---------- style ----------
ACCENT, DARK, GREY, SECOND, BG = "#1554C0", "#121212", "#8C8C8C", "#4D4D4D", "#FFFFFF"
PALE_ACCENT, LIGHT, GRID = "#E3EBFA", "#D9D9D9", "#EEEEEE"
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": BG, "axes.facecolor": BG})
def frame(fig, title, subtitle, source):
    W, H = fig.get_size_inches()
    fig.patches.append(plt.Rectangle((0.03, 1 - 0.30 / H), 0.07, 0.10 / H, transform=fig.transFigure, color=ACCENT, clip_on=False))
    fig.text(0.03, 1 - 0.45 / H, title, fontsize=17, fontweight="bold", color=DARK, va="top", ha="left")
    fig.text(0.03, 1 - 1.12 / H, "\n".join(textwrap.wrap(subtitle, 40)), fontsize=10.5, color=SECOND, va="top", ha="left", linespacing=1.3)
    fig.text(0.03, 0.15 / H, source, fontsize=8, color=SECOND, va="bottom", ha="left", linespacing=1.4)

SRC = ("Source: Eurostat, ESSPROS, 2024. Cash and in-kind benefits.\n"
       "Light grey: family. Mid grey: housing, social exclusion.\n"
       "Means-tested benefits are 11% of EU benefits (Belgium 6%*).\n"
       "* Lower bound: no split for three Belgian benefits.")
fig = plt.figure(figsize=(4.8, 6.2))
ax = fig.add_axes([0.20, 0.30, 0.76, 0.40])
order = list(GROUPS)
fills = {"old age and survivors": SECOND, "sickness, health care and disability": GREY, "family and children": LIGHT,
         "unemployment": ACCENT, "housing and social exclusion": "#BEBEBE"}
names = {"old age and survivors": "Pensions", "sickness, health care and disability": "Health,\ndisability"}
for yi, geo in enumerate(("EU27_2020", "BE")):
    y = 1.35 * (1 - yi); left = 0
    for g in order:
        v = sh(geo, g)
        ax.barh(y, v, left=left, color=fills[g], height=0.62, edgecolor="white", lw=1.2)
        if g in names:
            ax.text(left + v / 2, y, f"{names[g]}\n{v:.0f}%", ha="center", va="center", fontsize=10, fontweight="bold", color="white", linespacing=1.0)
        elif g == "family and children":
            ax.text(left + v / 2, y, f"{v:.0f}%", ha="center", va="center", fontsize=10, fontweight="bold", color=DARK)
        elif g == "unemployment":
            ax.annotate(f"Unemployment {v:.0f}%", (left + v / 2, y + 0.31), (left + v / 2, y + 0.62), fontsize=11, fontweight="bold",
                        color=ACCENT, ha="right", va="center", arrowprops=dict(arrowstyle="-", color=ACCENT, lw=1.3))
        left += v
ax.set_yticks([1.35, 0]); ax.set_yticklabels(["EU27", "Belgium"], fontsize=12, fontweight="bold")
ax.set_xlim(0, 100); ax.set_ylim(-0.5, 2.3)
ax.set_xticks([0, 50, 100]); ax.set_xticklabels(["0", "50", "100%"], fontsize=10, color=SECOND)
ax.tick_params(axis="y", length=0)
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
frame(fig, "Pensions and health take\n84% of benefits",
      "Share of each euro of social benefits, EU27 and Belgium, 2024, % (EU total 84%, Belgium 86%)", SRC)
fig.savefig(os.path.join(CH, "01_where_each_benefit_euro_goes_2024.png"), dpi=200); plt.close(fig)

FLAGS = [
 ("provisional_2025", "ESSPROS 2025 values are Eurostat early estimates. Headline numbers use 2024. The EU27 total differs by 0.2 points of GDP between the two years, so no message changes."),
 ("belgium_means_tested_lower_bound", "Eurostat gives no means-tested split for Belgian sickness/health care, survivors and unemployment. Belgium's 6% is a lower bound. The gap is small for the generous bound because unemployment is counted in full there."),
 ("classification_differs", "What counts as a means-tested scheme differs by country (Denmark 36%, Ireland 26% are outliers). Cross-country gaps are partly definitional. We read them as direction, not precision."),
 ("means_tested_is_not_poor", "Means-tested is a rule on the benefit, not a measure of who is poor. Flat-rate and insurance benefits also reach poor people, and means-tested benefits reach some who are not poor."),
 ("function_groups", "Eurostat groups health care with sickness and survivors with old age. 'Sickness, health care and disability' is mostly health care in kind. The two ESSPROS functions 'old age' and 'survivors' are summed."),
 ("benefits_exclude_admin", "Benefits exclude administration costs and tax breaks. Spending on education and some housing and social services outside ESSPROS is also outside."),
 ("poverty_measures", "Poverty rates are the 60%-of-median measure from the 2025 survey (incomes of 2024). ilc_li09 counts pensions as transfers (42.8% EU), ilc_li10 counts them as income (24.4%), ilc_li02 is after all transfers (16.3%). Health care in kind is not in any of the three."),
 ("pensioner_poverty_circular", "The 65+ poverty rate is measured after pensions. It shows pensioners are on average no more likely to be poor than others, not that pensions cause that."),
 ("generous_bound", "The 'generous bound' counts all unemployment, housing and social exclusion benefits and all means-tested benefits in other functions. It overstates the share going to poor or unemployed people."),
 ("no_incidence", "This is spending by purpose, not by recipient income. It does not say how much of each benefit reaches the bottom fifth, which needs household survey or microsimulation data not used here."),
]
pd.DataFrame(FLAGS, columns=["item", "flag"]).to_csv(os.path.join(OUT, "data_flags.csv"), index=False, lineterminator="\n")
