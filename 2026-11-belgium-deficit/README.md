# Belgium's budget row is about the wrong number

Deep dive. Published piece: [article.md](article.md).

## Claim tested

"Ageing is why Belgium cannot balance its books." And a second question: is the government's target of EUR 10bn of savings by 2029 the right size?

## The answer in three lines

1. Ageing is real: it cost Belgium about 3.8% of GDP between 2010 and 2024. It cost the Netherlands about 3.6%. The Dutch budget improved by 4.6 points of GDP. Belgium's did not (-0.3). So ageing does not explain the gap between the two.
2. Getting the deficit under 3% of GDP, roughly where the debt ratio stops rising, takes about EUR 19bn-22bn a year in 2026 money: about twice what is on the table.
3. In our illustrative paths no single lever does it. Cuts alone leave the deficit near 4% in 2035, growth alone near 5%. Only a big mix gets under 3%, around 2031, and none meets the 2029 goal.

## Method

### Part 1: the theme bridge

We split the change in the general government balance (as % of GDP) into themes with an exact identity.
The split ties to Eurostat revenue minus expenditure to within 0.01 points.

```
balance / Y  =  [L + C + K + NT] / Y  -  [PEN + HEA + SIC + OTH] / Y  -  INT / Y

L   = labour taxes + net social contributions       L/Y   = (L / D1) * (D1 / Y)
C   = taxes on production and imports               C/Y   = (C / Cn) * (Cn / Y)
K   = other taxes,  NT = non-tax revenue
PEN = old-age + survivors spending                  PEN/Y = (P65 / P) * (PENr / P65) / (Yr / P)
HEA, SIC, OTH = health, sickness and disability, other primary spending
                                                    X/Y   = (Xr / P) / (Yr / P)
INT = interest

Yr / P = (W / P) * (E / W) * (H / E) * (Yr / H)
```

Symbols: Y nominal GDP, Yr real GDP, D1 compensation of employees, Cn household consumption, P population,
P65 population aged 65 and over, W working-age population, E employment, H hours worked, "r" means deflated by the GDP deflator.

Each product is split into one term per factor with the log-mean Divisia index (LMDI, `lib/decompose.py`):

```
X1 - X0 = sum over factors k of  L(X1, X0) * ln(f_k1 / f_k0),   with L(a, b) = (a - b) / (ln a - ln b)
```

The terms add up exactly, with no residual. The factors then map to themes:
- **Demography:** the share of people aged 65 and over in pension spending, and working-age people per head in GDP per head.
- **Growth:** employment rate, hours, productivity, and the wage and consumption share of GDP. The cycle (AMECO actual minus cyclically adjusted balance) is carved out of it.
- **Tax ratios:** labour tax and contributions as a share of the wage bill, indirect taxes as a share of consumption.
- **Spending per beneficiary:** real spending per person aged 65 and over (pensions) or per head (health, sickness and disability, other).
- **Interest, and other taxes and non-tax revenue.**

### Part 2: robustness

`outputs/theme_bridge_robustness.csv` shows (a) the tax ratio split into labour and consumption,
(b) a second benchmark in which spending per beneficiary growing with real GDP per head counts as neutral,
and (c) six start and end year choices.

### Part 3: scenarios to 2035

A deliberately simple model of the deficit and debt, general government, % of GDP.
- Baseline: Federal Planning Bureau outlook 2026-31, extended with a drift of +0.10 points a year (central) or +0.20 (high). The drift is our assumption.
- Levers: spending cuts of 0.4% of GDP a year in 2027-31, trimming tax breaks 0.25% a year in 2028-31, a jobs lever (+3 points of employment), a productivity lever. The jobs and productivity values are low-confidence assumptions.
- Debt: d(t) = d(t-1) / (1 + g) + deficit(t), with nominal growth g = 3.1% plus a small boost from growth levers. Interest feedback of 3% on debt avoided.
- "What it takes": baseline deficit minus the target, converted to euro with an approximate 2026 GDP of EUR 0.66 trillion.

Parameters, with sources, are in the header of `run.py`.

## Limits

- **Results move with the start and end years.** The Belgian spending effect ranges from about -2.3 to -6.2 points of GDP across the six windows in `theme_bridge_robustness.csv`. Report ranges, not decimals.
- **"Spending per beneficiary" includes automatic drift.** It is measured against a frozen real benchmark. It therefore includes indexation, the welfare adjustment of benefits, the health growth norm, pension maturation and relative price effects. It is not a measure of discretionary decisions in this decade.
  Under a benchmark in which spending per head grows with income per head, the Belgian effect is positive (+2.1) and the Netherlands' is +6.7. The gap of about 5 points between the two survives either benchmark.
- **Germany.** Germany's spending bar is larger than Belgium's. The article makes the claim only about the Belgium-Netherlands gap.
- **Classification.** Old-age spending includes early-retirement schemes and elderly care. The 2014-15 state reform moved some health and care spending between levels of government. The Dutch "other" revenue includes the decline in gas income.
- **Data flags.** See `data/raw/SOURCES.md` (duplicate values in two cached series, a rounded employment rate).
- **Scenarios are illustrative.** The jobs lever overlaps with employment growth already in the Planning Bureau baseline. Growth does not feed the debt denominator in the way a full model would. The baseline excludes extra defence spending: moving towards NATO's 3.5% target could add up to 1.5 points of GDP. No path meets the 3% goal by 2029.
- **Consolidated government.** The split cannot say which level of government spent the money.

## Sources

| What | Dataset (code) | Publisher |
|---|---|---|
| GDP, deflator, compensation of employees, household consumption | nama_10_gdp, nama_10_a10 | Eurostat |
| Employment, employees, hours | nama_10_a10_e | Eurostat |
| Population, age structure | demo_gind, demo_pjanind | Eurostat |
| Employment rate and level, age 20-64 | lfsi_emp_a | Eurostat |
| Taxes and social contributions | gov_10a_taxag | Eurostat |
| Revenue, expenditure, interest | gov_10a_main | Eurostat |
| Spending by function (COFOG) | gov_10a_exp | Eurostat |
| Cyclically adjusted balance, output gap, interest, debt | AMECO (UBLG, UBLGAP, UBLGAPS, UBLGBPS, AVGDGP, UYIGE, UDGG) | European Commission |
| Deficit outlook 2026-31 | Economic outlook 2026-2031 | Federal Planning Bureau |

Cached files, pull date and AMECO vintage caveat: [data/raw/SOURCES.md](data/raw/SOURCES.md).

## Rerun

```
pip install -r requirements.txt
python 2026-11-belgium-deficit/run.py            # from cached data, checksum-verified
python 2026-11-belgium-deficit/run.py --refresh  # re-download from Eurostat and AMECO (needs internet)
```

Outputs:

| File | What it holds |
|---|---|
| `outputs/theme_bridge.csv` | Themes by country (BE, NL, DE) and period, in points of GDP and euro bn at end-year GDP |
| `outputs/theme_bridge_detail.csv` | The 28 underlying components of the bridge |
| `outputs/theme_bridge_summary_2010_2024.csv` | Eight chart groups, 2010-2024 |
| `outputs/theme_bridge_robustness.csv` | Benchmarks and start and end year sensitivity |
| `outputs/scenarios_2026_2035.csv` | Deficit and debt by scenario and drift |
| `outputs/what_it_takes.csv` | Measures needed for each target, in points of GDP and euro bn |
| `charts/*.png` | The charts in the article, plus a detail chart of the bridge |

Licences: code MIT, text and charts CC BY 4.0. See the repository root.
