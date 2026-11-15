# The EU budget: small next to national budgets, and error is not waste

**Claim tested.** "The EU budget is huge and wasteful."

**Answer in three lines.**
1. The 2025 EU budget provides EUR 155bn in payments, 1.7% of public spending in the EU. On the auditors' 2024 base it is 2.2% (2.8% with the recovery fund); with up to about EUR 72bn of NextGenerationEU, up to about 2.4%. About EUR 340 a person a year, against about EUR 20,700 from national governments.
2. The auditors' estimated error rate was 3.6% in 2024 (5.6% in 2023, 4.2% in 2022), above the 2% threshold, with an adverse opinion for six years. Error means rules broken; most errors show no sign of fraud (19 suspected cases in 812 sampled transactions) and it is not a value-for-money measure. On the ECA 2024 base (EUR 191.1bn) 3.6% is about EUR 7bn.
3. Verdict: mostly false. Size is false; waste is unproven because value for money is not measured here.

**Method.** Shares are payments or commitments divided by EU27 general government expenditure (Eurostat). Per person uses 2024 EU27 population. The euro amount "in error" is illustrative: the 2024 rate applied to 2025 payments. `run.py` checks the manifest, writes the CSVs and the chart, and asserts every number quoted in the article.

**Method note.** The Council's 155.2bn payments and 199.4bn commitments include special instruments (headline excluding them: 149.6bn and 192.8bn); they match the 0.84% and 1.08% of GNI quoted. Overlap between EU transfers and national spending moves the share by under 0.1 points (1.64% to 1.69%).

**Limits.** Budgeted, not outturn; Eurostat 2025 may be provisional. National spending includes some EU money passed on, so shares are approximate. NextGenerationEU is an estimate. No 2025 population in the cached file. See `outputs/data_flags.csv`.

**Sources.** Council 2025 EU budget infographic; ECA annual report 2024 FAQ; Commission 2025 draft budget page; Eurostat; OECD productivity database. See `data/raw/SOURCES.md`.

**Rerun.** `python3 -I run.py` (offline). `--refresh` is not implemented offline: re-pull the files as described in `data/raw/SOURCES.md`.
