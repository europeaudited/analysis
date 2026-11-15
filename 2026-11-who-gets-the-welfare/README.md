# Who gets the welfare? Where each euro of social benefits goes

**Claim tested.** "Social spending mostly goes to the poor and the unemployed."

**Answer in three lines.**
1. In the EU in 2024, old age, survivors, health care, sickness and disability take about 84% of social benefits. Unemployment takes about 4% (3% in Belgium).
2. About 11% of EU benefits are means-tested (Belgium about 6%, a lower bound). Even counting all unemployment, housing and exclusion benefits plus every means-tested benefit, the total is about 14%.
3. This is spending by purpose, not by recipient income. Pensions and health care also keep many low-income households out of poverty, which the data here cannot fully size (EU poverty: 43% before all transfers, 24% with pensions as income, 16% after).

**Method.** Shares are each function's euro total over the sum of the 8 ESSPROS functions (EU27 and Belgium, 2024), grouped into five purposes. Means-tested share = means-tested euros over total euros across the 8 functions. `run.py` checks the manifest, writes the CSVs and the chart, and asserts the numbers quoted in the article.

**Limits.** Belgium has no means-tested split for sickness, survivors and unemployment. Country definitions of means-tested differ. Means-tested is not the same as poor. 2025 ESSPROS values are early estimates (EU27 total within 0.2 points of GDP of 2024). Poverty rates are the 2025 survey, queried 2026-11-15. See `outputs/data_flags.csv`.

**Sources.** Eurostat ESSPROS and poverty datasets; see `data/raw/*.SOURCES.md`. Korpi and Palme (1998), American Sociological Review 63, 661-687, is cited as opinion context only (https://econpapers.repec.org/RePEc:lis:liswps:174).

**Rerun.** `python3 -I run.py` (offline). `--refresh` is not implemented offline: re-pull the Eurostat files as described in the SOURCES files.
