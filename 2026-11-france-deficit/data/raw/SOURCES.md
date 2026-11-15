# Sources for the raw files

## eurostat_waterfall_inputs.csv, eurostat_edp_2024_2025.csv, eurostat_eu27_spending.csv

Copied unchanged from `2026-11-belgium-deficit/data/raw/`, where their Eurostat datasets and query dates are listed. France rows are used here.

## ameco_fiscal_cycle_BE_NL_DE.csv

Copied unchanged from `2026-11-belgium-deficit/data/raw/`. Used for Belgium's line in the deficit chart.

## ameco_fiscal_FR.csv

European Commission, AMECO online database (`https://ec.europa.eu/economy_finance/ameco/wq/series`), France, queried 15 Nov 2026. Columns y2009 to y2027; 2026 and 2027 are Commission forecasts.
Full variable codes: UBLG `1.0.319.0.UBLG`, UBLGAP `1.0.319.0.UBLGAP`, UBLGAPS `1.0.319.0.UBLGAPS`, UBLGBPS `1.0.319.0.UBLGBPS`, AVGDGP `1.0.0.0.AVGDGP`, UYIGE `1.0.319.0.UYIGE`, UDGG `1.0.319.0.UDGG`, OVGD `1.1.0.0.OVGD`, UVGD `1.0.99.0.UVGD`, UUTG `1.0.319.0.UUTG`, URTG `1.0.319.0.URTG`.
The Belgian values in this AMECO release match the Belgium piece's cached file exactly, so both pieces use the same forecast round. The page did not state its vintage.
