"""Are Europeans about 30% poorer than Americans? Reads data/raw, writes outputs/ and charts/.

    python3 -I run.py     # offline; checks data/MANIFEST.sha256, asserts every number quoted in article.md

Definitions and assumptions:
- GDP per head (current prices, USD at purchasing-power parity, PPP) = GDP per hour worked x hours worked per head of population.
  Both inputs are read from the OECD Productivity database, so the split into output per hour and hours per person is exact:
  ratio of GDP per head = ratio of GDP per hour x ratio of hours per head. Log shares use natural logs of those ratios.
- "Gap" = 1 - EU / US. EU = the 27 current members (EU27_2020).
- Eurostat volume index (EU27 = 100) is a second, independent source. GDP is the 2024 column; actual individual consumption
  (AIC: household spending plus health and education paid by government) is 2023, because the US 2024 value is empty in the source.
- Ireland is shown in the table but left off the chart: its GDP is inflated by multinational profits booked there.
- Trend: three measures are shown because they disagree (see data_flags.csv). Nothing here is a median or a distribution.
- OECD US row: HRSAV (hours per worker, 1,702) x EMP / POP gives 825 hours per head, but HRSPOP is 860. Total hours (HRSTO,
  292,630.3 million, added to the raw file for the US) / POP = 860.4 = HRSPOP, and GDP per hour is GDP / HRSTO, so GDP per hour and
  hours per head are consistent on the 860 basis. HRSAV is the odd series (HRSTO / EMP = 1,775). 860 is the primary basis.
  A sensitivity on the 825 basis (US GDP per hour scaled up so GDP per head is unchanged) shows how the split would move.
"""
import os, sys, math, hashlib, shutil, textwrap
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

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

NAMES = {"USA": "US", "EU27_2020": "EU", "EA20": "Euro area", "BEL": "Belgium", "DEU": "Germany", "FRA": "France",
         "NLD": "Netherlands", "DNK": "Denmark", "SWE": "Sweden", "ITA": "Italy", "ESP": "Spain", "POL": "Poland",
         "IRL": "Ireland", "GBR": "UK"}
d = pd.read_csv(os.path.join(RAW, "oecd_productivity.csv"))
d["name"] = d.area.map(NAMES)
d["gdp_per_head_usd_ppp"] = d.gdp_per_hour_usd_ppp * d.hours_per_capita
d["employment_per_head"] = d.employment_thousands / d.population_thousands
d["implied_hours_per_head"] = d.employment_thousands * d.hours_per_worker / d.population_thousands
d.round(4).to_csv(os.path.join(OUT, "oecd_computed_all_years.csv"), index=False, lineterminator="\n")

u = d[d.year == 2024].set_index("area")
us = u.loc["USA"]
t = pd.DataFrame(index=u.index)
t["name"] = u.name
t["gdp_per_head_usd_ppp"] = u.gdp_per_head_usd_ppp
t["gdp_per_head_vs_us"] = u.gdp_per_head_usd_ppp / us.gdp_per_head_usd_ppp * 100
t["gdp_per_hour_vs_us"] = u.gdp_per_hour_usd_ppp / us.gdp_per_hour_usd_ppp * 100
t["hours_per_head_vs_us"] = u.hours_per_capita / us.hours_per_capita * 100
t["gap_pct"] = 100 - t.gdp_per_head_vs_us
t["output_per_hour_gap_pct"] = 100 - t.gdp_per_hour_vs_us
t["hours_per_head_gap_pct"] = 100 - t.hours_per_head_vs_us
lg = lambda x: math.log(x / 100)
t["log_share_from_output_per_hour"] = [lg(a) / lg(b) * 100 if abs(lg(b)) > 1e-9 else float("nan")
                                       for a, b in zip(t.gdp_per_hour_vs_us, t.gdp_per_head_vs_us)]
# log shares are not meaningful when the two terms have opposite signs (one above the US, one below): blank them
_opp = (t.gdp_per_hour_vs_us - 100) * (t.hours_per_head_vs_us - 100) < 0
t.loc[_opp, "log_share_from_output_per_hour"] = float("nan")
t["log_share_from_hours"] = 100 - t.log_share_from_output_per_hour
t["hours_per_worker_vs_us"] = u.hours_per_worker / us.hours_per_worker * 100
assert ((t.gdp_per_hour_vs_us * t.hours_per_head_vs_us / 100 - t.gdp_per_head_vs_us).abs() < 1e-6).all()
t = t.sort_values("gdp_per_head_vs_us", ascending=False)
t.round(2).to_csv(os.path.join(OUT, "gdp_per_head_decomposition_2024.csv"), lineterminator="\n")

# ---- Eurostat index ----
e = pd.read_csv(os.path.join(RAW, "ppp_volume_index_eu100.csv")).set_index("geo")
us_e, bel_e, eu_e = e.loc["US"], e.loc["BE"], e.loc["EU27_2020"]
eur = pd.DataFrame({
    "gdp_2024_us100": e.GDP_2024 / us_e.GDP_2024 * 100,
    "aic_2023_us100": e.AIC_2023 / us_e.AIC_2023 * 100})
eur["gdp_gap_pct"] = 100 - eur.gdp_2024_us100
eur["aic_gap_pct"] = 100 - eur.aic_2023_us100
eur.round(1).to_csv(os.path.join(OUT, "eurostat_index_vs_us.csv"), lineterminator="\n")

# ---- trend: EU as % of US on three measures ----
rows = []
for y in (2015, 2019, 2024):
    x = d[d.year == y].set_index("area")
    cur = x.loc["EU27_2020", "gdp_per_head_usd_ppp"] / x.loc["USA", "gdp_per_head_usd_ppp"] * 100
    con = x.loc["EU27_2020", "gdp_per_capita_const_2020ppp"] / x.loc["USA", "gdp_per_capita_const_2020ppp"] * 100
    ero = e.loc["EU27_2020", f"GDP_{y}"] / e.loc["US", f"GDP_{y}"] * 100
    rows.append((y, cur, con, ero))
trend = pd.DataFrame(rows, columns=["year", "oecd_current_price_eu_pct_of_us", "oecd_constant_2020ppp_eu_pct_of_us",
                                    "eurostat_index_eu_pct_of_us"]).set_index("year")
trend.round(1).to_csv(os.path.join(OUT, "trend_eu_vs_us.csv"), lineterminator="\n")
g = lambda area, y, col: float(d.loc[(d.area == area) & (d.year == y), col].iloc[0])
growth = {f"{a}_const_gdp_per_head_growth_2015_2024_pct": (g(a, 2024, "gdp_per_capita_const_2020ppp") / g(a, 2015, "gdp_per_capita_const_2020ppp") - 1) * 100
          for a in ("EU27_2020", "USA")}

# ---- US hours identity (editor check) ----
hrsto = float(us.hours_total_millions)
assert abs(hrsto * 1000 / us.population_thousands - us.hours_per_capita) < 0.1      # HRSTO / POP = HRSPOP = 860.4
us_hours_per_job = hrsto * 1000 / us.employment_thousands                              # HRSTO / EMP, hours per worker
assert round(us_hours_per_job) == 1775 and abs(us.hours_per_worker - 1702.3) < 0.01   # HRSAV is the odd series
# GDP per hour = GDP / HRSTO: US GDP implied (USD tn) is the same on either hours basis
us_gdp_tn = us.gdp_per_hour_usd_ppp * hrsto / 1e6
assert 29.0 < us_gdp_tn < 29.6
# Sensitivity (flag, not in the card): if US hours per head were the persons-based 825, US GDP per hour would be
# GDP per head / 825 (GDP per head is unchanged), and every country's output-per-hour ratio and hours ratio move.
alt_h = float(us.implied_hours_per_head); alt_ph = float(us.gdp_per_head_usd_ppp) / alt_h
def _split(a):
    ph = u.loc[a, "gdp_per_hour_usd_ppp"] / alt_ph * 100; hh = u.loc[a, "hours_per_capita"] / alt_h * 100
    return ph, hh
eu_ph, eu_hh = _split("EU27_2020"); bel_ph, bel_hh = _split("BEL")
sens = {"sens825_US_hours_per_head": alt_h, "sens825_US_gdp_per_hour": alt_ph,
        "sens825_EU_output_per_hour_vs_us": eu_ph, "sens825_EU_hours_gap_pct": 100 - eu_hh,
        "sens825_EU_productivity_log_share": math.log(eu_ph / 100) / math.log(eu_ph * eu_hh / 1e4) * 100,
        "sens825_BEL_output_per_hour_vs_us": bel_ph, "sens825_BEL_hours_gap_pct": 100 - bel_hh,
        "US_hours_per_job_hrsto_over_emp": us_hours_per_job, "US_gdp_implied_tn_usd": us_gdp_tn}
# ---- Ireland inside the EU figure ----
ie = u.loc["IRL"]; eu_ = u.loc["EU27_2020"]
eu_ex_ie = (eu_.gdp_per_head_usd_ppp * eu_.population_thousands - ie.gdp_per_head_usd_ppp * ie.population_thousands) / (eu_.population_thousands - ie.population_thousands)
eu_gap_ex_ie = 100 - eu_ex_ie / us.gdp_per_head_usd_ppp * 100
# ---- employment per head of population (persons basis) and growth since 2019 ----
emp = {f"{a}_employment_per_head_pct": float(u.loc[a, "employment_per_head"] * 100) for a in ("USA", "EU27_2020", "BEL", "FRA", "ITA", "DEU", "NLD", "DNK")}
gr19 = {f"{a}_const_gdp_per_head_growth_2019_2024_pct": (g(a, 2024, "gdp_per_capita_const_2020ppp") / g(a, 2019, "gdp_per_capita_const_2020ppp") - 1) * 100 for a in ("EU27_2020", "USA")}

H = t.loc  # shorthand
facts = {
 "US_gdp_per_head_usd": us.gdp_per_head_usd_ppp, "EU_gdp_per_head_usd": H["EU27_2020", "gdp_per_head_usd_ppp"],
 "EU_gap_gdp_per_head_oecd_pct": H["EU27_2020", "gap_pct"],
 "EU_gdp_per_hour_gap_pct": H["EU27_2020", "output_per_hour_gap_pct"],
 "EU_hours_per_head_gap_pct": H["EU27_2020", "hours_per_head_gap_pct"],
 "EU_log_share_from_output_per_hour": H["EU27_2020", "log_share_from_output_per_hour"],
 "EU_log_share_from_hours": H["EU27_2020", "log_share_from_hours"],
 "EA_gap_gdp_per_head_oecd_pct": H["EA20", "gap_pct"],
 "eurostat_EU_gap_gdp_2024_pct": eur.loc["EU27_2020", "gdp_gap_pct"],
 "eurostat_EU_gap_aic_2023_pct": eur.loc["EU27_2020", "aic_gap_pct"],
 "eurostat_US_gdp_index_2024": us_e.GDP_2024, "eurostat_US_aic_index_2023": us_e.AIC_2023,
 "eurostat_BE_gap_gdp_2024_pct": eur.loc["BE", "gdp_gap_pct"], "eurostat_BE_gap_aic_2023_pct": eur.loc["BE", "aic_gap_pct"],
 "eurostat_NL_gap_aic_2023_pct": eur.loc["NL", "aic_gap_pct"], "eurostat_DK_gap_aic_2023_pct": eur.loc["DK", "aic_gap_pct"],
 "eurostat_DE_gap_aic_2023_pct": eur.loc["DE", "aic_gap_pct"],
 "BEL_gdp_per_head_vs_us": H["BEL", "gdp_per_head_vs_us"], "BEL_gap_gdp_per_head_pct": H["BEL", "gap_pct"],
 "BEL_gdp_per_hour_vs_us": H["BEL", "gdp_per_hour_vs_us"], "BEL_hours_per_head_gap_pct": H["BEL", "hours_per_head_gap_pct"],
 "BEL_hours_per_head": float(u.loc["BEL", "hours_per_capita"]), "US_hours_per_head": float(us.hours_per_capita),
 "BEL_gdp_per_hour_usd": float(u.loc["BEL", "gdp_per_hour_usd_ppp"]), "US_gdp_per_hour_usd": float(us.gdp_per_hour_usd_ppp),
 "BEL_hours_per_worker_vs_us": H["BEL", "hours_per_worker_vs_us"],
 "DEU_gap_gdp_per_head_pct": H["DEU", "gap_pct"], "DEU_gdp_per_hour_vs_us": H["DEU", "gdp_per_hour_vs_us"],
 "DEU_hours_per_head_gap_pct": H["DEU", "hours_per_head_gap_pct"],
 "FRA_gap_gdp_per_head_pct": H["FRA", "gap_pct"], "FRA_output_per_hour_gap_pct": H["FRA", "output_per_hour_gap_pct"],
 "FRA_hours_per_head_gap_pct": H["FRA", "hours_per_head_gap_pct"],
 "NLD_gdp_per_head_vs_us": H["NLD", "gdp_per_head_vs_us"], "DNK_gdp_per_head_vs_us": H["DNK", "gdp_per_head_vs_us"],
 "NLD_gdp_per_hour_vs_us": H["NLD", "gdp_per_hour_vs_us"], "DNK_gdp_per_hour_vs_us": H["DNK", "gdp_per_hour_vs_us"],
 "NLD_hours_per_head_gap_pct": H["NLD", "hours_per_head_gap_pct"], "DNK_hours_per_head_gap_pct": H["DNK", "hours_per_head_gap_pct"],
 "DNK_hours_per_worker_vs_us": H["DNK", "hours_per_worker_vs_us"],
 "POL_gdp_per_head_vs_us": H["POL", "gdp_per_head_vs_us"], "POL_gdp_per_hour_vs_us": H["POL", "gdp_per_hour_vs_us"],
 "ITA_gdp_per_head_vs_us": H["ITA", "gdp_per_head_vs_us"], "ESP_gdp_per_head_vs_us": H["ESP", "gdp_per_head_vs_us"],
 "IRL_gdp_per_head_vs_us": H["IRL", "gdp_per_head_vs_us"],
 "trend_gap_2015_oecd_current_pct": 100 - trend.loc[2015, "oecd_current_price_eu_pct_of_us"],
 "trend_gap_2019_oecd_current_pct": 100 - trend.loc[2019, "oecd_current_price_eu_pct_of_us"],
 "trend_gap_2024_oecd_current_pct": 100 - trend.loc[2024, "oecd_current_price_eu_pct_of_us"],
 "trend_gap_2015_oecd_constant_pct": 100 - trend.loc[2015, "oecd_constant_2020ppp_eu_pct_of_us"],
 "trend_gap_2019_oecd_constant_pct": 100 - trend.loc[2019, "oecd_constant_2020ppp_eu_pct_of_us"],
 "trend_gap_2024_oecd_constant_pct": 100 - trend.loc[2024, "oecd_constant_2020ppp_eu_pct_of_us"],
 "trend_gap_2015_eurostat_pct": 100 - trend.loc[2015, "eurostat_index_eu_pct_of_us"],
 "trend_gap_2019_eurostat_pct": 100 - trend.loc[2019, "eurostat_index_eu_pct_of_us"],
 "trend_gap_2024_eurostat_pct": 100 - trend.loc[2024, "eurostat_index_eu_pct_of_us"],
 **growth,
 "EU_gap_gdp_per_head_ex_Ireland_pct": eu_gap_ex_ie,
 "eurostat_DNK_gdp_gap_2024_pct": eur.loc["DK", "gdp_gap_pct"],
 "US_hours_reported_over_implied": float(us.hours_per_capita / us.implied_hours_per_head),
 **sens, **emp, **gr19,
}
facts = {k: float(v) for k, v in facts.items()}

# ---- assertions: every number quoted in article.md ----
r = lambda k, n=0: round(facts[k], n)
assert r("US_gdp_per_head_usd", -2) == 86100 and r("EU_gdp_per_head_usd", -2) == 63700
assert r("EU_gap_gdp_per_head_oecd_pct") == 26 and r("eurostat_EU_gap_gdp_2024_pct") == 28 and r("eurostat_EU_gap_aic_2023_pct") == 35
assert r("EU_gdp_per_hour_gap_pct") == 19 and r("EU_hours_per_head_gap_pct") == 9
assert r("EU_log_share_from_output_per_hour") == 69 and r("EU_log_share_from_hours") == 31
assert r("BEL_gap_gdp_per_head_pct") == 14 and round(facts["BEL_gdp_per_hour_vs_us"]) == 109 and r("BEL_hours_per_head_gap_pct") == 21
assert r("eurostat_BE_gap_gdp_2024_pct") == 16 and r("eurostat_BE_gap_aic_2023_pct") == 26
assert round(facts["BEL_hours_per_head"]) == 682 and round(facts["US_hours_per_head"]) == 860
assert round(facts["BEL_gdp_per_hour_usd"]) == 109 and round(facts["US_gdp_per_hour_usd"]) == 100
assert r("DEU_gap_gdp_per_head_pct") == 14 and round(facts["DEU_gdp_per_hour_vs_us"]) == 100 and r("DEU_hours_per_head_gap_pct") == 14
assert r("FRA_gap_gdp_per_head_pct") == 27 and r("FRA_output_per_hour_gap_pct") == 7 and r("FRA_hours_per_head_gap_pct") == 22
assert r("NLD_gdp_per_head_vs_us") == 98 and r("DNK_gdp_per_head_vs_us") == 96
assert r("NLD_gdp_per_hour_vs_us") == 102 and r("DNK_gdp_per_hour_vs_us") == 112
assert r("eurostat_NL_gap_aic_2023_pct") == 22 and r("eurostat_DK_gap_aic_2023_pct") == 29
assert r("POL_gdp_per_head_vs_us") == 58 and r("POL_gdp_per_hour_vs_us") == 60 and r("IRL_gdp_per_head_vs_us") == 164
assert r("trend_gap_2019_oecd_constant_pct") == 28 and r("trend_gap_2024_oecd_constant_pct") == 31
assert r("trend_gap_2019_eurostat_pct") == 25 and r("trend_gap_2024_eurostat_pct") == 28
assert r("trend_gap_2019_oecd_current_pct") == 30 and r("trend_gap_2024_oecd_current_pct") == 26
assert r("trend_gap_2015_oecd_current_pct") == 36
assert r("EU27_2020_const_gdp_per_head_growth_2015_2024_pct") == 13 and r("USA_const_gdp_per_head_growth_2015_2024_pct") == 18
assert r("US_gdp_per_head_usd", -3) == 86000 and r("EU_gdp_per_head_usd", -3) == 64000
assert r("DNK_hours_per_worker_vs_us") == 80 and facts["NLD_hours_per_head_gap_pct"] < 4
assert r("EU_gap_gdp_per_head_oecd_pct") == 26 and abs(facts["EU_gap_gdp_per_head_ex_Ireland_pct"] - 27.1) < 0.1
assert r("EU27_2020_const_gdp_per_head_growth_2019_2024_pct") == 4 and r("USA_const_gdp_per_head_growth_2019_2024_pct") == 10
assert round(facts["BEL_employment_per_head_pct"]) == 43 and round(facts["USA_employment_per_head_pct"], 1) == 48.5
assert all(facts[f"{a}_employment_per_head_pct"] < facts["USA_employment_per_head_pct"] - 3 for a in ("BEL", "FRA", "ITA"))
assert abs(facts["sens825_EU_productivity_log_share"] - 82.5) < 0.1 and abs(facts["sens825_BEL_output_per_hour_vs_us"] - 104.4) < 0.1
assert math.isnan(t.loc["BEL", "log_share_from_output_per_hour"])
pd.Series(facts, name="value").round(2).to_csv(os.path.join(OUT, "headline_numbers.csv"), header=True, lineterminator="\n")

# ---------- style ----------
ACCENT, DARK, GREY, SECOND, BG = "#1554C0", "#121212", "#8C8C8C", "#4D4D4D", "#FFFFFF"
PALE_ACCENT, LIGHT, GRID = "#E3EBFA", "#D9D9D9", "#EEEEEE"
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": BG, "axes.facecolor": BG})
def frame(fig, title, subtitle, source):
    W, H_ = fig.get_size_inches()
    fig.patches.append(plt.Rectangle((0.03, 1 - 0.30 / H_), 0.07, 0.10 / H_, transform=fig.transFigure, color=ACCENT, clip_on=False))
    fig.text(0.03, 1 - 0.45 / H_, title, fontsize=17, fontweight="bold", color=DARK, va="top", ha="left")
    fig.text(0.03, 1 - 1.12 / H_, "\n".join(textwrap.wrap(subtitle, 66)), fontsize=10.5, color=SECOND, va="top", ha="left", linespacing=1.3)
    fig.text(0.03, 0.15 / H_, source, fontsize=8, color=SECOND, va="bottom", ha="left")

# ---------- chart 1: GDP per head vs US ----------
order = ["EU27_2020", "EA20", "NLD", "DNK", "BEL", "DEU", "SWE", "GBR", "FRA", "ITA", "ESP", "POL"]
c1 = t.loc[order].sort_values("gdp_per_head_vs_us")
fig = plt.figure(figsize=(7, 7.2))
ax = fig.add_axes([0.20, 0.17, 0.72, 0.60])
cols = [ACCENT if k == "EU27_2020" else GREY for k in c1.index]
ax.barh(c1.name, c1.gdp_per_head_vs_us, color=cols, height=0.7)
for y, (v, k) in enumerate(zip(c1.gdp_per_head_vs_us, c1.index)):
    inside = 93 < v <= 100
    ax.text(v - 1 if inside else v + 1, y, f"{v:.0f}", va="center", ha="right" if inside else "left", fontsize=11.5,
            color=ACCENT if k == "EU27_2020" else DARK, fontweight="bold" if k in ("EU27_2020", "BEL") else "normal")
ax.axvline(100, color=DARK, lw=1.2); ax.text(101, len(c1) - 0.3, "US = 100", fontsize=10.5, color=DARK, ha="left", va="bottom")
ax.set_xlim(0, 118); ax.set_ylim(-0.6, len(c1) + 0.2)
ax.tick_params(axis="y", length=0, labelsize=11.5); ax.tick_params(axis="x", labelsize=10.5, colors=SECOND)
ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
for lbl in ax.get_yticklabels():
    if lbl.get_text() in ("EU", "Belgium"): lbl.set_fontweight("bold")
    if lbl.get_text() == "EU": lbl.set_color(ACCENT)
frame(fig, "The EU produces about a quarter\nless per head than the US",
      "GDP per head in 2024, current prices at purchasing-power parity, US = 100", 
      "Source: OECD Productivity database (GDP per hour x hours per head). Ireland (164) is left off\nthe chart but counted in the EU figure; multinational profits inflate its GDP.")
fig.savefig(os.path.join(CH, "01_gdp_per_head_vs_us_2024.png"), dpi=200); plt.close(fig)

# ---------- chart 2: split of the gap ----------
o2 = ["EU27_2020", "BEL", "DEU", "FRA"]
c2 = t.loc[o2]
fig = plt.figure(figsize=(7, 7.2))
ax = fig.add_axes([0.27, 0.17, 0.66, 0.60])
yy = list(range(len(o2)))[::-1]
bh = 0.36
for y, k in zip(yy, o2):
    a, b = c2.loc[k, "gdp_per_hour_vs_us"], c2.loc[k, "hours_per_head_vs_us"]
    ax.barh(y + bh / 2, a, height=bh, color=DARK)
    ax.barh(y - bh / 2, b, height=bh, color=ACCENT)
    ins = 93 < a <= 100
    ax.text(a - 1 if ins else a + 1, y + bh / 2, f"{a:.0f}", va="center", ha="right" if ins else "left", fontsize=11.5, color="white" if ins else DARK, fontweight="bold")
    ax.text(b + 1, y - bh / 2, f"{b:.0f}", va="center", fontsize=11.5, color=ACCENT, fontweight="bold")
ax.set_yticks(yy); ax.set_yticklabels([f"{NAMES[k]}\nGDP per head {c2.loc[k, 'gdp_per_head_vs_us']:.0f}" for k in o2], fontsize=10.5, fontweight="bold")
ax.axvline(100, color=DARK, lw=1.2); ax.text(101, len(o2) - 0.4, "US = 100", fontsize=9, color=DARK, ha="left", va="bottom")
ax.set_xlim(0, 125); ax.set_ylim(-0.7, len(o2) - 0.3)
ax.tick_params(axis="y", length=0); ax.tick_params(axis="x", labelsize=10.5, colors=SECOND)
ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
ax.legend(handles=[Patch(color=DARK, label="Output per hour worked"), Patch(color=ACCENT, label="Hours worked per head of population")],
          loc="lower center", bbox_to_anchor=(0.45, -0.17), ncol=1, frameon=False, fontsize=10.5)
frame(fig, "Belgium's gap is hours, not\noutput per hour",
      "Output per hour worked and hours worked per head of population, 2024, US = 100. Multiply the two to get GDP per head.",
      "Source: OECD Productivity database, current prices at purchasing-power parity.")
fig.savefig(os.path.join(CH, "02_gap_split_hours_vs_output_2024.png"), dpi=200); plt.close(fig)

FLAGS = [
 ("ppp_uncertainty", "Purchasing-power-parity (PPP) comparisons carry an error of several points. The OECD figure (EU gap 26%) and the Eurostat index (28%) differ by 2 points on the same year for this reason."),
 ("trend_measures_disagree", "The direction of the gap over time depends on the measure. Since 2019 the gap widened on OECD constant-price GDP per head (28% to 31%) and on the Eurostat index (25% to 28%), but narrowed on OECD current-price GDP per head (30% to 26%). Since 2015 the Eurostat index (32% to 28%) and the current-price series (36% to 26%) narrowed, constant-price widened (29% to 31%). The constant-price series is a growth fact (real GDP per head since 2019: EU +4%, US +10%); the current-price narrowing coincides with relative price changes (not verified) and the Eurostat 2019 to 2024 move is about 2 points, inside PPP error. The card quotes real growth and both current-price windows and says the trend is not settled."),
 ("us_hours_identity", "FOR THE EDITOR, not in the card. OECD US row: HRSPOP = 860.4 hours per head, but EMP x HRSAV / POP = 825.4 (4.2% lower); all 13 other areas reconcile. Editor check of the OECD file: total hours HRSTO 2024 = 292,630.3 million (2023: 291,066); HRSTO / POP = 860.4 = HRSPOP; HRSTO / EMP = 1,775 hours per worker; GDP per hour (GDPHRS) divides GDP by the same HRSTO, so GDP per hour and hours per head are consistent on the 860 basis. HRSAV (1,702) is the odd series, probably a different employment or per-job concept. 860 is the primary basis; GDP per head and the EU gap (26%) do not depend on it. Sensitivity if the persons-based 825 were right (US GDP per hour 104.4): EU productivity share of the gap about 82% instead of 69%, EU hours gap about 5% instead of 9%, Belgium output per hour about 104 instead of 109, Belgium hours gap about 17% instead of 21%. Direction of every conclusion is unchanged (Belgium at or above the US per hour; EU gap mostly output per hour)."),
 ("us_hours_per_worker", "If US hours per worker are quoted anywhere use 1,775 (HRSTO / EMP), not HRSAV 1,702. Because HRSAV is inconsistent, Denmark's hours per worker are not compared with the US in the card."),
 ("log_share_negative", "Log shares of the gap are blank where one term is above and the other below the US (Belgium, Netherlands, Denmark): the split is not meaningful there."),
 ("selection", "Belgium's output per hour is flattered by selection: 43% of the population is employed against 48.5% in the US (persons basis), so fewer lower-productivity workers are in the denominator. More people in work would probably lower average output per hour."),
 ("employment_wording", "EU employment per head (48.6%) equals the US (48.5%), so for the EU as a whole the hours gap is hours per worker, not fewer people in work. Fewer people in work applies to Belgium (43%), France and Italy."),
 ("ireland_in_eu", "Ireland is left off chart 1 but is inside the EU bar. Excluding it the OECD EU gap is 27.1% instead of 26.0%."),
 ("ireland", "Ireland's GDP per head is 164 (US = 100) in the OECD data, inflated by multinationals' booked profits. Shown in outputs, left off chart 1. Its Eurostat consumption index (99, EU = 100) is a better guide to living standards."),
 ("aic_year_mismatch", "Consumption (AIC) gap uses 2023 because the US 2024 value is empty in the Eurostat extract. GDP gap uses 2024. Different years, so the two gaps are not strictly comparable."),
 ("aic_health_prices", "AIC counts health and education provided by government at cost. The US spends much more per head on health. Whether that is higher living standards or higher prices is not tested here, so the 35% consumption gap may overstate the gap in what households can enjoy."),
 ("average_not_median", "All figures are averages per head. Nothing here measures the median household, inequality, poverty or health. The US has higher average income partly because its top is richer (not tested here)."),
 ("hours_preference", "Fewer hours per head mix choice (more holiday, shorter weeks) and constraint (fewer people in work). The OECD data do not separate the two. The employment-rate split is not used because of the US identity issue above."),
 ("eu_average_composition", "The EU figure averages very different countries: Poland is at 58 and the Netherlands at 98 (US = 100) in GDP per head. 'Europeans' as one group hides this. EU27 is the current 27 members; the UK, Switzerland and Norway are outside it."),
 ("current_price_conversion", "Current-price GDP per head in USD PPP is computed as GDP per hour x hours per head. It is not read directly from a GDP per capita series."),
 ("vintage", "Data pulled 2026-11-15; the OECD API could not be re-queried during review. 2024 is the latest year in both sources. OECD figures for 2024 may be provisional and revised."),
]
pd.DataFrame(FLAGS, columns=["item", "flag"]).to_csv(os.path.join(OUT, "data_flags.csv"), index=False, lineterminator="\n")

print(pd.Series(facts).round(1).to_string())
