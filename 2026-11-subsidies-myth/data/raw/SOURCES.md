# Sources for this piece

The raw file is a cached copy, pulled on 2026-11-14. Its checksum is in `../MANIFEST.sha256`.
Check it with: `cd data && sha256sum -c MANIFEST.sha256`.

## ardeco_nuts2_1980_2024.csv

JRC ARDECO, the Annual Regional Database of the European Commission's Directorate General for
Regional and Urban Policy and the Joint Research Centre. Version 2024, NUTS2 level.
API: `https://territorial.ec.europa.eu/ardeco-api-v2/rest/export/{VAR}?version=2024&unit={UNIT}&level_id=2`.

| Variable | Meaning |
|---|---|
| SOVGD | Real GDP, EUR million at 2020 prices |
| SNPTD | Average population, thousands |
| SNETD | Workplace employment, thousands |

Format: `var,geo,1980,...,2024`. One row per variable and region.

Regions. Belgian NUTS2 regions are provinces: BE10 Brussels, BE21 Antwerp, BE22 Limburg,
BE23 East Flanders, BE24 Flemish Brabant, BE25 West Flanders, BE31 Walloon Brabant, BE32 Hainaut,
BE33 Liege, BE34 Luxembourg, BE35 Namur. Other regions in the file: DEC0 Saarland,
FRE1 Nord-Pas-de-Calais, NL42 Limburg (NL).

Groups used in `run.py`:
- Belgium: all eleven Belgian regions.
- Flanders: BE21 to BE25.
- Rest of Wallonia: BE33, BE34, BE35 (Walloon Brabant is left out because it is a Brussels commuter belt).

## Known data flags

- **Back-casts.** Values before 1995 are ARDECO back-casts, not official ESA 2010 national accounts.
  They are spliced across accounting systems, which adds measurement error in the "before" period.
- **Carry-forward.** BE32 (Hainaut) and BE22 (Limburg) show 2023 equal to 2022 exactly. This looks like
  an ARDECO estimate or carry-forward.
- **Place of work and place of residence.** GDP is measured where people work and population where they
  live. Commuting to Brussels and Walloon Brabant grew over the period.
- **Contaminated comparisons.** Liege had Objective 2 status, and Namur and Luxembourg had Objective 5b
  status, in the 1990s. Nord-Pas-de-Calais had Objective 1 areas in 1994-99. EU funding to Hainaut also
  continued after 2006 as phasing-out and then transition support.

## Literature in `evidence.md`

The evidence table cites the studies by author and year, with links.
