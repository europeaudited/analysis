# Poorer than America: output and consumption per head, EU vs US

**Claim tested.** "Europeans are about 30% poorer than Americans."

**Answer in three lines.**
1. The EU is 26% below the US in output per head (OECD, 2024), 28% below on Eurostat's index (2024), and 35% below in consumption per head (Eurostat, 2023).
2. For the EU as a whole about two-thirds of the output gap is lower output per hour and one-third fewer hours per head of population. In Belgium output per hour is above the US and the gap is hours (21% fewer hours per head), partly a selection effect (43% of the population employed against 48.5% in the US).
3. Verdict: Mostly true, on averages. Nothing here tests the median household, inequality or health.

**Method.** GDP per head (USD, current prices, PPP) = GDP per hour x hours per head, both read from the OECD Productivity database. Ratio to the US splits exactly into a ratio of output per hour times a ratio of hours per head; log shares are in `outputs/gdp_per_head_decomposition_2024.csv`. Eurostat volume indices (EU27 = 100) are rebased to US = 100. Trend: EU as % of US on three measures. `run.py` checks the manifest, writes the CSVs and two charts, and asserts every number quoted in the article.

**Limits.** Averages, not medians. PPP error of several points. Ireland is left off chart 1 but is in the EU figure (excluding it the gap is 27.1%). Consumption uses 2023 (US 2024 empty). The trend depends on the measure: real growth since 2019 is EU +4%, US +10%, while current-price gaps narrowed (partly price effects, not verified). The OECD's US hours per worker (HRSAV) do not reconcile with its total hours and employment; GDP per hour and hours per head are consistent on the 860 basis used here, and the EU gap is unaffected. OECD 2024 values may be revised; data pulled 2026-11-15 and not re-queried since. See `outputs/data_flags.csv`.

**Sources.** See `data/raw/*.SOURCES.md`: OECD Productivity database (OECD.SDD.TPS, DSD_PDB@DF_PDB v2.0); Eurostat prc_ppp_ind (VI_PPS_EU27_2020_HAB).

**Rerun.** `python3 -I run.py` (offline). `--refresh` is not implemented offline: re-pull the files as described in the SOURCES files.
