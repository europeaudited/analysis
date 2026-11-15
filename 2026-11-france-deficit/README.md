# Why France keeps missing 3%

Data and code behind the post. Rerun with `python 2026-11-france-deficit/run.py` from the repository root.

| File | What it is |
|---|---|
| `run.py` | France's record since 2009, spending and revenue shares, the 2010-2024 split of the budget balance (same method as `2026-11-belgium-deficit`), and the three charts |
| `data/raw/` | Cached Eurostat and AMECO inputs, with `SOURCES.md` and a checksum manifest |
| `outputs/*.csv` | Every number in the post |
| `charts/*.png` | The charts in the post |
| `post.md` | The published text |

Limits: the split is an accounting identity, not a causal model, and it moves with start and end years (see `theme_bridge_robustness.csv`). Government budget figures are the government's own estimates against its own baseline.

Licences: code MIT, text and charts CC BY 4.0. See the repository root.
