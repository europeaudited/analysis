"""Re-download the raw data for this piece. UNTESTED IN SANDBOX; VALIDATED IN CI.

The dataset codes and filters below are the best available mapping of each cached indicator to
its source. The first CI refresh run prints a comparison against the cached files
(compare_with_cache); treat any large difference as a mapping error to fix, not as new data.
Writes the same file formats the analysis already reads, then run.py rewrites the manifest.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipelines import ameco, eurostat  # noqa: E402

GEOS = ["BE", "NL", "DE", "DK", "FR"]
FIRST_YEAR = 2009

# indicator -> (dataset, filters). Only indicators the analysis reads are refreshed.
EUROSTAT_SPEC = {
    "gdp_clv10_meur": ("nama_10_gdp", dict(na_item="B1GQ", unit="CLV10_MEUR")),
    "gdp_cp_meur": ("nama_10_gdp", dict(na_item="B1GQ", unit="CP_MEUR")),
    "comp_employees_cp": ("nama_10_a10", dict(nace_r2="TOTAL", na_item="D1", unit="CP_MEUR")),
    "hh_consumption_cp": ("nama_10_gdp", dict(na_item="P31_S14_S15", unit="CP_MEUR")),
    "employment_ths_per": ("nama_10_a10_e", dict(nace_r2="TOTAL", na_item="EMP_DC", unit="THS_PER")),
    "hours_ths": ("nama_10_a10_e", dict(nace_r2="TOTAL", na_item="EMP_DC", unit="THS_HW")),
    "pop_jan": ("demo_gind", dict(indic_de="JAN")),
    "pc_65_plus": ("demo_pjanind", dict(indic_de="PC_Y65_MAX")),
    "lfs_emp_20_64_ths": ("lfsi_emp_a", dict(indic_em="ACT", age="Y20-64", sex="T", unit="THS_PER")),
    "lfs_emp_rate_20_64": ("lfsi_emp_a", dict(indic_em="ACT", age="Y20-64", sex="T", unit="PC_POP")),
    "tax_hh_income": ("gov_10a_taxag", dict(sector="S13_S212", na_item="D51A", unit="MIO_EUR")),
    "tax_ssc_net": ("gov_10a_taxag", dict(sector="S13_S212", na_item="D61REC", unit="MIO_EUR")),
    "tax_production_imports": ("gov_10a_taxag", dict(sector="S13_S212", na_item="D2REC", unit="MIO_EUR")),
    "tax_total": ("gov_10a_taxag", dict(sector="S13_S212", na_item="D2_D5_D91_D61_M_D995", unit="MIO_EUR")),
    "gov_TE": ("gov_10a_main", dict(sector="S13", na_item="TE", unit="MIO_EUR")),
    "gov_TR": ("gov_10a_main", dict(sector="S13", na_item="TR", unit="MIO_EUR")),
    "gov_interest": ("gov_10a_main", dict(sector="S13", na_item="D41PAY", unit="MIO_EUR")),
    "exp_old_age": ("gov_10a_exp", dict(sector="S13", cofog99="GF1002", na_item="TE", unit="MIO_EUR")),
    "exp_survivors": ("gov_10a_exp", dict(sector="S13", cofog99="GF1003", na_item="TE", unit="MIO_EUR")),
    "exp_health": ("gov_10a_exp", dict(sector="S13", cofog99="GF07", na_item="TE", unit="MIO_EUR")),
    "exp_sick_disab": ("gov_10a_exp", dict(sector="S13", cofog99="GF1001", na_item="TE", unit="MIO_EUR")),
}

# cached AMECO label -> AMECO full variable (validate in CI)
AMECO_SPEC = {
    "UBLG_pctGDP": "1.0.0.0.UBLG",
    "UBLGAP_CAB_pctPotGDP": "1.0.0.0.UBLGAP",
    "UBLGAPS_structural_pctPotGDP": "1.0.0.0.UBLGAPS",
    "UBLGBPS_struct_primary_pctPotGDP": "1.0.0.0.UBLGBPS",
    "AVGDGP_output_gap_pct": "1.0.0.0.AVGDGP",
    "UYIGE_interest_pctGDP": "1.0.0.0.UYIGE",
}
AMECO_COUNTRIES = {"BEL": "Belgium", "NLD": "Netherlands", "DEU": "Germany"}
AMECO_NAME_TO_COUNTRY = {"Belgium": "Belgium", "Netherlands": "Netherlands", "Germany": "Germany"}


def refresh_eurostat(raw_dir):
    rows = []
    for ind, (ds, filt) in EUROSTAT_SPEC.items():
        df = eurostat.fetch_dataset(ds, since=FIRST_YEAR, geo=GEOS, **filt)
        series = eurostat.to_series_by_geo(df)
        for geo in GEOS:
            s = series.get(geo, {})
            if not s:
                raise RuntimeError(f"No data for {ind} {geo}")
            first, last = min(s), max(s)
            rows.append([ind, geo, first] + [("" if y not in s else s[y]) for y in range(first, last + 1)])
    with open(Path(raw_dir) / "eurostat_waterfall_inputs.csv", "w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


def refresh_ameco(raw_dir):
    out, years = [], list(range(2009, 2028))
    for label, full in AMECO_SPEC.items():
        df = ameco.fetch_series(full, countries=",".join(AMECO_COUNTRIES), years=f"{years[0]}-{years[-1]}")
        for country in ("Belgium", "Germany", "Netherlands"):
            d = df[df.country.str.contains(country)]
            vals = {int(y): v for y, v in zip(d.year, d.value)}
            out.append([label, country] + ["" if vals.get(y) != vals.get(y) or y not in vals else vals[y] for y in years])
    with open(Path(raw_dir) / "ameco_fiscal_cycle_BE_NL_DE.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["code", "country"] + [f"y{y}" for y in years])
        w.writerows(out)


def compare_with_cache(old_dir, new_dir):
    """Print the largest relative difference per indicator on overlapping years (Eurostat file)."""
    def read(p):
        d = {}
        for line in open(p):
            q = line.strip().split(",")
            d[(q[0], q[1])] = {int(q[2]) + i: float(v) for i, v in enumerate(q[3:]) if v != ""}
        return d
    old, new = read(Path(old_dir) / "eurostat_waterfall_inputs.csv"), read(Path(new_dir) / "eurostat_waterfall_inputs.csv")
    for key in sorted(new):
        if key in old:
            diffs = [abs(new[key][y] / old[key][y] - 1) for y in new[key] if y in old[key] and old[key][y]]
            if diffs:
                print(f"refresh check {key[0]:24s} {key[1]}  max relative change {max(diffs):.4f}")


def refresh(raw_dir):
    import shutil
    import tempfile
    raw_dir = Path(raw_dir)
    backup = Path(tempfile.mkdtemp())
    for p in raw_dir.glob("*.csv"):
        shutil.copy(p, backup / p.name)
    refresh_eurostat(raw_dir)
    refresh_ameco(raw_dir)
    compare_with_cache(backup, raw_dir)
