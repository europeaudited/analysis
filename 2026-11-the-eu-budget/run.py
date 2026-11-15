"""The EU budget against public spending in the EU. Reads data/raw, writes outputs/ and charts/.

    python3 -I run.py     # offline; checks data/MANIFEST.sha256, asserts every number quoted in article.md

Definitions and assumptions:
- EU budget = the annual budget as adopted for 2025 (Council figures), not outturn. Payments = cash actually paid in the year;
  commitments = legal promises that can be paid over several years.
- NextGenerationEU (NGEU) is borrowed money outside the annual budget. The Commission expected about EUR 72bn of
  disbursements in 2025. It is shown as a separate, estimated bar and is not in the 1% figures.
- National public spending = EU27 general government total expenditure 2025 (Eurostat gov_10a_main, TE, S13). Some of it is money
  the EU budget sent to governments and they then spent, so comparing the two is not a strict sum: the ratio is approximate.
- Per person uses EU27 population for 2024 (451.0m), the latest in the cached file. No 2025 population is cached.
- ECA error rate = share of audited spending that broke EU or national rules (estimated). It is not a fraud rate and not a waste rate.
- The EUR bn "in error" for 2025 is illustrative: the 2024 error rate applied to 2025 payments. The ECA audited a different base.
"""
import os, sys, hashlib, shutil, textwrap
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

if "--refresh" in sys.argv:
    print("No network in the default build. Re-pull data/raw per data/raw/SOURCES.md, then rerun."); sys.exit(0)
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

ext = pd.read_csv(os.path.join(RAW, "external_figures.csv"))
xtra = pd.read_csv(os.path.join(RAW, "eu_budget_extra_figures.csv"))
gov = pd.read_csv(os.path.join(RAW, "eu_gov_totals.csv"))
pop = pd.read_csv(os.path.join(RAW, "oecd_productivity_eu27.csv"))

def one(df, item, year, **kw):
    m = (df["item"] == item) & (df["year"] == year)
    for k, v in kw.items(): m &= df[k] == v
    assert m.sum() == 1, (item, year)
    return float(df.loc[m, "value"].iloc[0])

commit = one(ext, "eu_budget_commitments", 2025, area="EU")
commit_gni = one(ext, "eu_budget_commitments_pct_gni", 2025)
pay = one(ext, "eu_budget_payments", 2025)
pay_gni = one(ext, "eu_budget_payments_pct_gni", 2025)
admin = one(ext, "eu_budget_admin_payments", 2025)
err = {y: one(ext, "eca_error_rate", y) for y in (2022, 2023, 2024)}
thr = one(xtra, "eca_materiality_threshold", 2024)
adverse_years = one(xtra, "eca_adverse_opinion_consecutive_years", 2024)
ngeu = one(xtra, "nextgenerationeu_disbursements_expected", 2025)
te = one(gov, "TE", 2025, geo="EU27_2020") / 1000       # EUR bn
gdp = one(gov, "GDP", 2025, geo="EU27_2020") / 1000
ecabase = one(xtra, "eca_audited_eu_budget_spending", 2024)
ecabase_rrf = one(xtra, "eca_spending_incl_rrf", 2024)
fraud_n, fraud_of, fraud_eppo = (one(xtra, k, 2024) for k in ("eca_suspected_fraud_cases", "eca_transactions_audited_fraud_test", "eca_fraud_cases_sent_to_eppo"))
err_complex = one(xtra, "eca_error_rate_complex_rules", 2024)
te24 = one(gov, "TE", 2024, geo="EU27_2020") / 1000
popm = float(pop.loc[pop.year == 2024, "population_thousands"].iloc[0]) / 1000   # millions

f = {
 "eu_commitments_2025_eur_bn": commit, "eu_payments_2025_eur_bn": pay, "eu_admin_2025_eur_bn": admin,
 "eu_commitments_pct_gni": commit_gni, "eu_payments_pct_gni": pay_gni,
 "ngeu_expected_disbursements_2025_eur_bn": ngeu,
 "national_public_spending_2025_eur_bn": te, "eu27_gdp_2025_eur_bn": gdp,
 "national_spending_pct_gdp": te / gdp * 100,
 "eu_payments_pct_public_spending": pay / te * 100,
 "eu_commitments_pct_public_spending": commit / te * 100,
 "eu_payments_plus_ngeu_eur_bn": pay + ngeu,
 "eu_payments_plus_ngeu_pct_public_spending": (pay + ngeu) / te * 100,
 "eu_payments_pct_gdp": pay / gdp * 100,
 "eu_payments_plus_ngeu_pct_gdp": (pay + ngeu) / gdp * 100,
 "national_spending_per_euro_of_eu_payments": te / pay,
 "population_2024_millions": popm,
 "eu_payments_per_person_eur": pay * 1000 / popm,
 "eu_admin_per_person_eur": admin * 1000 / popm,
 "national_spending_per_person_eur": te * 1000 / popm,
 "eu_admin_share_of_payments_pct": admin / pay * 100,
 "eca_error_2022": err[2022], "eca_error_2023": err[2023], "eca_error_2024": err[2024],
 "eca_threshold_pct": thr, "eca_error_2024_over_threshold_x": err[2024] / thr,
 "eca_adverse_opinion_years": adverse_years,
 "illustrative_error_2024_rate_on_2025_payments_eur_bn": err[2024] / 100 * pay,
 "illustrative_error_pct_of_public_spending": err[2024] / 100 * pay / te * 100,
 "illustrative_error_per_person_eur": err[2024] / 100 * pay * 1000 / popm,
}
f["illustrative_error_if_2023_rate_eur_bn"] = err[2023] / 100 * pay
f.update({
 "eca_audited_base_2024_eur_bn": ecabase, "eca_base_incl_rrf_2024_eur_bn": ecabase_rrf,
 "national_public_spending_2024_eur_bn": te24,
 "eca_base_pct_public_spending_2024": ecabase / te24 * 100,
 "eca_base_incl_rrf_pct_public_spending_2024": ecabase_rrf / te24 * 100,
 "eca_error_eur_bn_on_audited_base": err[2024] / 100 * ecabase,
 "eca_error_per_person_eur": err[2024] / 100 * ecabase * 1000 / popm,
 "eca_error_pct_public_spending_2024": err[2024] / 100 * ecabase / te24 * 100,
 "eca_error_2023_rate_eur_bn_on_audited_base": err[2023] / 100 * ecabase,
 "eca_suspected_fraud_cases": fraud_n, "eca_transactions_fraud_test": fraud_of, "eca_fraud_cases_to_eppo": fraud_eppo,
 "eca_error_complex_rules": err_complex,
 "overlap_low_pct": pay / (te + pay) * 100, "overlap_high_pct": pay / (te - pay) * 100,
 "overlap_ngeu_low_pct": (pay + ngeu) / (te + pay + ngeu) * 100, "overlap_ngeu_high_pct": (pay + ngeu) / (te - pay) * 100,
})
pd.Series(f, name="value").round(3).to_csv(os.path.join(OUT, "headline_numbers.csv"), header=True, index_label="item", lineterminator="\n")

bars = pd.DataFrame([
 ("National governments, all spending", te, "EU27 general government total expenditure 2025"),
 ("EU budget, payments", pay, "Council, 2025 EU budget (adopted)"),
 ("EU budget + NextGenerationEU (est.)", pay + ngeu, "Council plus Commission estimate of NGEU disbursements"),
], columns=["bar", "eur_bn", "basis"])
bars["pct_of_national_spending"] = bars.eur_bn / te * 100
bars["eur_per_person_2024_pop"] = bars.eur_bn * 1000 / popm
bars.round(3).to_csv(os.path.join(OUT, "eu_vs_national_spending.csv"), index=False, lineterminator="\n")

# asserts: every number quoted in article.md
assert round(pay) == 155 and round(commit) == 199 and round(pay_gni, 2) == 0.84 and round(commit_gni, 2) == 1.08
assert round(te) == 9336 and round(f["national_spending_pct_gdp"]) == 49
assert round(f["eu_payments_pct_public_spending"], 1) == 1.7 and round(f["eu_commitments_pct_public_spending"], 1) == 2.1
assert round(f["eu_payments_plus_ngeu_pct_public_spending"], 1) == 2.4 and round(ngeu) == 72
assert round(f["national_spending_per_euro_of_eu_payments"]) == 60
assert round(f["eu_payments_per_person_eur"], -1) == 340 and round(f["national_spending_per_person_eur"], -2) == 20700
assert round(f["eu_admin_per_person_eur"]) == 28 and round(f["eu_admin_share_of_payments_pct"]) == 8
assert (err[2022], err[2023], err[2024], thr, adverse_years) == (4.2, 5.6, 3.6, 2.0, 6.0)
assert round(f["illustrative_error_2024_rate_on_2025_payments_eur_bn"], 1) == 5.6
assert round(f["illustrative_error_pct_of_public_spending"], 2) == 0.06 and round(f["illustrative_error_per_person_eur"]) == 12
assert round(ecabase, 1) == 191.1 and round(f["eca_error_eur_bn_on_audited_base"]) == 7 and round(f["eca_error_per_person_eur"]) == 15
assert round(f["eca_base_pct_public_spending_2024"], 1) == 2.2 and round(f["eca_base_incl_rrf_pct_public_spending_2024"], 1) == 2.8
assert (fraud_n, fraud_of, fraud_eppo, err_complex) == (19, 812, 7, 5.2) and round(err[2024] / thr, 1) == 1.8
assert max(f["overlap_high_pct"], f["overlap_ngeu_high_pct"]) - min(f["overlap_low_pct"], f["overlap_ngeu_low_pct"]) < 1
assert round(admin) == 13 and round(f['illustrative_error_2024_rate_on_2025_payments_eur_bn']) == 6 and round(te, -2) == 9300
print(pd.Series(f).round(2).to_string())

# ---------- chart ----------

ACCENT, DARK, GREY, SECOND, BG = "#1554C0", "#121212", "#8C8C8C", "#4D4D4D", "#FFFFFF"
PALE_ACCENT, LIGHT, GRID = "#E3EBFA", "#D9D9D9", "#EEEEEE"
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": BG, "axes.facecolor": BG})
def frame(fig, title, subtitle, source):
    W, H = fig.get_size_inches()
    fig.patches.append(plt.Rectangle((0.03, 1 - 0.30 / H), 0.07, 0.10 / H, transform=fig.transFigure, color=ACCENT, clip_on=False))
    fig.text(0.03, 1 - 0.45 / H, title, fontsize=17, fontweight="bold", color=DARK, va="top", ha="left")
    fig.text(0.03, 1 - 1.12 / H, "\n".join(textwrap.wrap(subtitle, 66)), fontsize=10.5, color=SECOND, va="top", ha="left", linespacing=1.3)
    fig.text(0.03, 0.15 / H, source, fontsize=8, color=SECOND, va="bottom", ha="left")

fig = plt.figure(figsize=(7, 5.6))
ax = fig.add_axes([0.27, 0.22, 0.68, 0.50])
lab = ["National\ngovernments", "EU budget\n(payments)", "EU budget + up to\nNextGenEU (est.)"]
vals = list(bars.eur_bn)
cols = [GREY, ACCENT, ACCENT]
ax.barh(lab[::-1], vals[::-1], color=cols[::-1], height=0.6)
for i, (v, p) in enumerate(zip(vals[::-1], bars.pct_of_national_spending[::-1])):
    txt = f"EUR {round(v, -2) if v > 1000 else round(v):,.0f}bn" + ("" if p == 100 else f"\n{p:.1f}% of national")
    ax.text(v + 150, i, txt, va="center", fontsize=11, color=DARK, fontweight="bold")
ax.set_xlim(0, 15500); ax.set_xticks([0, 3000, 6000, 9000]); ax.set_xlabel("EUR billion", fontsize=9, color=SECOND); ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.tick_params(axis="y", length=0, labelsize=10); ax.tick_params(axis="x", labelsize=9, colors=SECOND)
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
frame(fig, "EU money is about 2% of\npublic spending in the EU",
      "EU27 spending in 2025, EUR billion. National governments against the EU budget (as budgeted)",
      "Source: Eurostat (gov_10a_main), Council (2025 EU budget), Commission (NextGenerationEU).\n"
      "NextGenEU: borrowed, outside the budget, draft-stage estimate, may include loans.")
fig.savefig(os.path.join(CH, "01_eu_budget_vs_national_spending_2025.png"), dpi=200); plt.close(fig)

FLAGS = [
 ("adopted_not_outturn", "The 2025 EU budget figures are the adopted budget (commitments 199.44bn, payments 155.21bn), not final outturn. Amendments during the year may change them."),
 ("ngeu_off_budget", "NextGenerationEU (up to about 72bn, may include loans that are financing, not spending) is borrowed and sits outside the annual budget. The Commission expected about 72bn of disbursements in 2025 (an estimate, from a Commission page about the draft budget). With it, EU money is about 2.4% of public spending, not 1.7%."),
 ("overlap", "National general government spending includes some EU funds that governments receive and spend. The EU share is therefore approximate and the two figures are not strictly additive."),
 ("population_year", "The cached population file has no 2025 value. Per-person figures use 2024 EU27 population (451.0m)."),
 ("error_not_waste", "The ECA error rate measures spending that broke EU or national rules. The ECA says error is not fraud and most errors do not signal fraud. It is not a measure of waste or value for money."),
 ("error_amount", "About 7bn in error is our calculation: the ECA 2024 rate (3.6%) times the ECA's 2024 EU budget spending (191.1bn, excluding the recovery fund). The ECA FAQ gives no euro amount. The 2025 payments x 3.6% (5.6bn) is kept in headline_numbers.csv only."),
 ("outturn_base", "The ECA's 2024 spending base (191.1bn; 247.0bn with the recovery fund) is above 2025 adopted payments (155.2bn). Reason not verified. On that base the share of 2024 national spending is 2.2%, or 2.8% with the recovery fund. Treat 1.7% as the low end."),
 ("overlap_bounds", "Overlap between EU transfers and national spending moves the payments share between about 1.6% and 1.7% (2.4% to 2.5% with NextGenerationEU): under 0.1 points."),
 ("eurostat_provisional", "Eurostat 2025 totals may be a first release; the cached file has no status flag."),
 ("special_instruments", "The Council's 155.21bn payments and 199.44bn commitments include special instruments; the headline excluding them is 149.6bn and 192.8bn. We use the larger figures. 155.2 is consistent with the 0.84% of GNI quoted."),
 ("admin_share", "Administration is 12.84bn in the Council's 'European public administration' heading, 8% of payments. It covers all institutions' staff, pensions and buildings. Another source quotes about 6%, from a different base; not reconciled here."),
 ("gni_vs_gdp", "Council shares are of GNI (0.84% payments); our public-spending shares use Eurostat GDP and spending. Both are shown and labelled."),
 ("belgium", "Belgium hosts several institutions. No net-contribution figure is sourced here, so none is given."),
 ("hand_entered", "NextGenerationEU 72bn, the sixth adverse opinion and the 2% threshold are in eu_budget_extra_figures.csv (read in the cited pages), not in the shared inbox file."),
]
pd.DataFrame(FLAGS, columns=["item", "flag"]).to_csv(os.path.join(OUT, "data_flags.csv"), index=False, lineterminator="\n")
