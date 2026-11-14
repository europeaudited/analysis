# "Subsidies and public spending drive growth"

Myth card. Verdict: **Mixed**. Published piece: [article.md](article.md). Evidence table: [evidence.md](evidence.md).

## Claim tested

"Subsidies and public spending drive growth and local jobs." We test it for Belgium, with one test of our own:
did the EU's top tier of regional aid (Objective 1, 1994-2006) change the path of Hainaut, Belgium's poorest province?

## The answer in three lines

1. Subsidies deliver what they target. Research aid raises research spending. Evidence of a wider effect on growth or jobs is thin.
2. Hainaut's GDP per head fell from 74.5% of the Belgian level in 1980 to 69.4% in 1993, 64.8% in 2006 and 61.2% in 2024. The decline did not stop during the programme.
3. That rules out a large effect. It does not tell us what would have happened without the money.

## Method

For each region group we compute real GDP per head (ARDECO real GDP at 2020 prices divided by average population)
and workplace jobs per head. We compare Hainaut (BE32) with:
- Liege (BE33), the closest industrial neighbour;
- the rest of Wallonia excluding Walloon Brabant (BE33, BE34, BE35);
- Flanders (BE21 to BE25);
- Belgium (all eleven regions).

Periods: before 1980-1993, during 1993-2006, after 2006-2024.
For each comparator we compute the gap in annual GDP-per-head growth (log points) between Hainaut and the comparator in each period,
and the change in that gap from "before" to "during". We also move the start of the "before" window to 1985 and 1989.
Everything the article says about Hainaut can be read from the three CSV files in `outputs/`.

The literature review in [evidence.md](evidence.md) covers more than 20 Belgian and international studies, each with a method, a finding, a verdict and a confidence level.

## Limits

- **One treated region, no standard errors.** This is a descriptive comparison, not a causal estimate.
- **The answer depends on the comparison.** Against Belgium and Flanders there is no pause in Hainaut's relative decline during the programme.
  Against the rest of Wallonia the gap narrows, because those regions also slid during 1993-2006. The sign of the change flips when the "before" window starts in 1985.
- **Comparison regions were treated too.** Liege (Objective 2), Namur and Luxembourg (Objective 5b), Nord-Pas-de-Calais (Objective 1 areas, 1994-99). EU support to Hainaut continued after 2006.
- **Data.** Pre-1995 values are ARDECO back-casts. BE32 shows 2023 equal to 2022 (likely a carry-forward). GDP is measured where people work and population where they live.
- **Jobs.** Hainaut added fewer jobs per head than its neighbours in 1993-2006. This fits the literature, which finds income gains but no robust employment effect.
- **Dropped.** A cross-country comparison of subsidies and growth was removed after review: it was driven by Ireland.

## Sources

| What | Source | Code |
|---|---|---|
| Real GDP, population, employment by region | JRC ARDECO, NUTS2, version 2024 | SOVGD, SNPTD, SNETD |
| Business support, about EUR 25bn | National Bank of Belgium, Economic Review, October 2025 | see evidence.md |
| Research aid | Federal Planning Bureau evaluations (Dumont) | see evidence.md |
| Regional aid effects | Becker, Egger and von Ehrlich (2010, 2018); Vandenberghe (2018) | see evidence.md |

Raw data, dataset codes and caveats: [data/raw/SOURCES.md](data/raw/SOURCES.md).

## Rerun

```
pip install -r requirements.txt
python 2026-11-subsidies-myth/run.py            # from cached data, checksum-verified
python 2026-11-subsidies-myth/run.py --refresh  # re-download from the ARDECO API (needs internet)
```

Outputs:

| File | What it holds |
|---|---|
| `outputs/hainaut_objective1_test.csv` | Growth in GDP per head and change in jobs per head by period, and GDP per head against Belgium, for eight regions |
| `outputs/hainaut_growth_gaps.csv` | Growth gaps before, during and after, by comparator, with start-year sensitivity |
| `outputs/relative_gdp_per_head_index.csv` | Annual index, Belgium = 100 |
| `charts/04_hainaut.png` | The chart in the article |
| `charts/hainaut_vs_neighbours.png` | Hainaut against Liege, the rest of Wallonia and Flanders |

Licences: code MIT, text and charts CC BY 4.0. See the repository root.
