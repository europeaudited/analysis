# Methodology

## How a piece is made

1. **Brief.** One claim, stated as people actually say it. The brief names the data that could test it and why now.
2. **Data.** We start from official statistics, pulled from the publishers' APIs. The raw files are cached in the repository with SHA-256 checksums.
3. **Analysis.** Code in `run.py` turns the cached data into output tables and charts. Every number in a piece traces to a file in `outputs/`.
4. **Review committee.** Three reviewers, each with one job, read the analysis and the draft:
   - **Statistician.** Is the method sound? Do the results survive other start years, benchmarks and data checks?
   - **Economist from the other side.** What is the strongest argument against our reading? Do we state it fairly?
   - **Hostile reader.** What would a motivated critic quote against us? Which sentences go beyond the numbers?

   Each reviewer lists must-fix and should-fix points. Every must-fix is resolved or the claim is cut.
5. **Editor.** Cuts the text to house style, checks every number against the outputs, and writes the verdict.
6. **Human approval.** A human editor reads every piece, and nothing is published without that approval.

Pieces are produced with AI agents and checked by a human editor before publication.

## Verdict scale

| Verdict | Meaning |
|---|---|
| True | The data support the claim as stated. |
| Mostly true | The data support the main point, with qualifications we state. |
| Mixed | The claim is right for some cases, countries or periods, and wrong for others. |
| Mostly false | The data contradict the main point, though a part of it holds. |
| False | The data contradict the claim. |
| Unproven | The data to test the claim do not exist, or do not settle it. |

We alternate verdicts on purpose. At least one piece in three shows where Europe's model works.
Every piece names the strongest counter-argument to its own reading.

## Data sources policy

- Official statistics come first: Eurostat, the European Commission (AMECO), the JRC (ARDECO), national statistical offices and central banks, the OECD, the IMF.
- Studies come second. We cite them by author, year and link, and we say how strong the method is.
- Raw files are cached under `<piece>/data/raw/` with a SHA-256 manifest. A run fails if a file has changed.
- `SOURCES.md` in each data folder lists dataset codes, URLs, the pull date and known data flags.
- Refreshing data is a separate, explicit step (`run.py --refresh`). A refresh is never committed automatically.

## What we will not do

- Use anonymous sources.
- Publish a number we cannot trace to a file in the repository.
- Hide a result that goes against our own reading.
- Target individuals or parties. We test claims.
- Take money tied to a policy outcome.
- Present illustrative model paths as forecasts.

## Corrections policy

- If a number, chart or sentence is wrong, we fix it and record it in [CORRECTIONS.md](CORRECTIONS.md): date, piece, what changed, why.
- Any change to a published number is a correction, however small.
- We do not edit a published piece silently.
- Readers can report a problem with the "Something's wrong" issue form. We reply, rerun the analysis, and say what we found, even when the claim holds.

## Conflicts of interest

The editors have no party affiliation. Full interests statement: to be published before launch.

## AI disclosure

Our pieces are produced with AI agents and checked by a human editor before publication.
Agents draft, analyse and review. A human reads every piece, holds editorial responsibility and approves it.
