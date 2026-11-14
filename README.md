# Europe, Audited

**Europe's social model is worth keeping. That's why we audit it. Code included.**

We test popular claims about Europe's social model against official data. Every piece comes with its data,
its code and a verdict, so you can rerun it, check it and challenge it.
We say where the model works and where it does not. We test claims, not people or parties.

## Published pieces

| Piece | Claim tested | Verdict | Folder |
|---|---|---|---|
| Belgium's budget row is about the wrong number | "Ageing is why Belgium can't balance its books" | Mostly false | [2026-11-belgium-deficit](2026-11-belgium-deficit/) |
| Aid came, the gap stayed | "Subsidies and public spending drive growth" | Mixed | [2026-11-subsidies-myth](2026-11-subsidies-myth/) |

Verdict scale: True, Mostly true, Mixed, Mostly false, False, Unproven. Definitions are in [METHODOLOGY.md](METHODOLOGY.md).

## Rerun a piece

```
pip install -r requirements.txt
python <folder>/run.py              # rebuild outputs and charts from the cached data
python <folder>/run.py --refresh    # re-download the raw data first (needs internet)
```

The default run uses cached raw files, checked against SHA-256 checksums in `<folder>/data/MANIFEST.sha256`.
It needs no internet. A GitHub Action reruns every piece on each pull request and every Monday,
and fails if any output CSV changes.

## Challenge a piece

- Think a number, chart or sentence is wrong? Open an issue with the **"Something's wrong"** form.
  Say where, why, and give a source.
- Have a better method or a fix? Open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).
- Want us to test a claim? Open an issue with the **"Suggest an idea"** form.

## Licences

- Code: MIT. See [LICENSE](LICENSE).
- Text, charts and processed data: CC BY 4.0. See [LICENSE-CONTENT.md](LICENSE-CONTENT.md).
- Source data stay under the licences of their publishers (Eurostat, European Commission, JRC).

## How these pieces are made, and AI disclosure

Our pieces are produced with AI agents and checked by a human editor before publication.
The agents pull the data, run the analysis, draft the text and review it. A human editor reads every piece,
and approves it before it goes out. Method, review process and rules: [METHODOLOGY.md](METHODOLOGY.md).

## Corrections

We publish every correction in [CORRECTIONS.md](CORRECTIONS.md), with what changed and why.
