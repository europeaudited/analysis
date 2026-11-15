# Contributing

## Report a mistake

Open an issue with the **"Something's wrong"** form. Tell us which piece, where (file, chart or sentence),
what is wrong, why, and give a source or evidence. We rerun the analysis and reply.

## Suggest a claim to test

Open an issue with the **"Suggest an idea"** form. Say what claim people make, where you hear it,
what data could test it, and which country it concerns.

## Send a pull request

1. Fork the repository and install the requirements: `pip install -r requirements.txt`.
2. Make your change. Keep sentences short. Do not use em dashes.
3. Rerun the affected piece: `python <folder>/run.py`. Commit the changed outputs.
4. Explain in the pull request what changed and why. Changes to published numbers go in [CORRECTIONS.md](CORRECTIONS.md).

The workflow reruns every piece and fails if outputs change without a matching commit.

## Rules

- Official statistics first. Every number must trace to a file in `outputs/`.
- No personal information in issues, commits or files.
- Be civil. We test claims, not people.

By contributing you agree that your code is released under MIT and your text under CC BY 4.0.
