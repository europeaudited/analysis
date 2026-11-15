# Sources for this piece

Raw files are cached copies. They were pulled on 2026-11-14. Checksums are in `../MANIFEST.sha256`.
Check them with: `cd data && sha256sum -c MANIFEST.sha256`.

## eurostat_waterfall_inputs.csv

Format: `indicator,geo,first_year,values...`. One value per year from first_year. Empty means missing.
Countries: BE, NL, DE, DK, FR. 2025 values are provisional. COFOG spending runs to 2024.

| Indicator | Eurostat dataset | Filter (dimension = value) |
|---|---|---|
| gdp_clv10_meur | nama_10_gdp | na_item = B1GQ, unit = CLV10_MEUR |
| gdp_cp_meur | nama_10_gdp | na_item = B1GQ, unit = CP_MEUR |
| comp_employees_cp | nama_10_a10 | na_item = D1, unit = CP_MEUR |
| hh_consumption_cp | nama_10_gdp | na_item = P31_S14_S15, unit = CP_MEUR |
| employment_ths_per, employees_ths_per, hours_ths | nama_10_a10_e | total economy |
| pop_jan, natural_growth, net_migration | demo_gind | population on 1 January and its drivers |
| pc_65_plus | demo_pjanind | share of population aged 65 and over |
| lfs_emp_20_64_ths, lfs_emp_rate_20_64 | lfsi_emp_a | employment, age 20-64 |
| tax_hh_income, tax_ssc_net, tax_production_imports, tax_corporate, tax_total | gov_10a_taxag | S13_S212, million euro |
| gov_TE, gov_TR, gov_interest | gov_10a_main | S13, million euro |
| exp_old_age, exp_survivors, exp_health, exp_sick_disab | gov_10a_exp | S13, COFOG 10.2, 10.3, 07, 10.1 |

Dataset pages: `https://ec.europa.eu/eurostat/databrowser/view/<dataset>/default/table`.
API: `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<dataset>`.

## ameco_fiscal_cycle_BE_NL_DE.csv

European Commission, AMECO online database: `https://ec.europa.eu/economy_finance/ameco/wq/series`.
Belgium, Germany and the Netherlands. Columns y2009 to y2027.
Series: UBLG (net lending, % of GDP), UBLGAP (cyclically adjusted balance, % of potential GDP),
UBLGAPS (structural balance), UBLGBPS (structural primary balance), AVGDGP (output gap),
UYIGE (interest, % of GDP), UDGG (gross debt, % of GDP), OVGD (real GDP).
The cycle in the bridge is UBLG minus UBLGAP.

**Vintage caveat.** The AMECO page did not state its vintage. Values for 2025 to 2027 are European
Commission forecasts, probably from a 2026 forecast round. The bridge uses AMECO only up to 2024, but
the cyclically adjusted balance is revised with every forecast round, so the cycle term can move
slightly when AMECO is refreshed. Confirm the vintage when you refresh.

## Other inputs used by run.py (typed into the code, with the source)

- Federal Planning Bureau medium-term outlook 2026-31 (published 12 February 2026), deficit path 2026-31.
  Later revision to 5.1% (2026) and 6.4% (2031), reported by the Belga news agency.
- Debt in 2025, 107.9% of GDP: AMECO and the European Commission Spring 2026 forecast.
- Government savings target of EUR 10bn by 2029: Belgian federal government, July 2026.
- Nominal GDP in 2026, about EUR 0.66 trillion: approximate, used only to convert percent of GDP into euro.

## Known data flags

- German real GDP is identical in 2023 and 2024 in the cached file (3,089,797.2). It looks like a filled value.
- Belgian survivors' spending is identical in 2020 and 2021 (7,538.8).
- Working-age population is back-calculated from an employment rate rounded to one decimal.

## eurostat_edp_2024_2025.csv
Eurostat `gov_10dd_edpt1` (government deficit/surplus and debt, EDP notification), unit PC_GDP, sector S13, na_item B9 (net lending (+) / borrowing (-)) and GD (gross debt), 2024 and 2025. Queried 15 Nov 2026 from https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/gov_10dd_edpt1. Deficits are shown with their sign: negative = deficit.

## Other figures quoted, not in a raw file
- EU age-related spending 24.4% of GDP in 2022, projected to rise by about 1.2 points of GDP by 2070: European Commission, 2024 Ageing Report (Institutional Paper 279), as summarised by Bruegel, "Beyond retirement: a closer look at the very old" (2024).
