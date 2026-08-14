# Contributing

This is a living document maintained by one person. Corrections and additions are welcome, particularly these:

## Especially wanted

- **Factual corrections.** If a claim here is wrong, outdated, or unsupported, open an issue with a source. The guide's value depends entirely on being right.
- **Missing attribution.** If a framing here belongs to someone and isn't credited, that's a defect — please flag it and it'll be fixed promptly and credited.
- **Broken links**, particularly in the landing-page diagram, where MkDocs can't validate them automatically.

## Ground rules for content

- **No unsourced figures.** Every statistic, benchmark result, or dated claim needs a source that can be checked. If it can't be verified at source, it doesn't go in.
- **Attribute distinctly-authored framings in the chapter**, not only in `references.md`. See `DECISIONS.md` (D8).
- **Australian English.**
- Prose over bullet fragments — chapters read as written argument.

## Structural changes

Read `DECISIONS.md` first. If you're proposing a change to the reference architecture, the licence split, or the repo layout, please raise an issue before a pull request — those choices have recorded reasoning and it's worth arguing against that reasoning directly.

## Local setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

`mkdocs build --strict` must pass with zero warnings before a pull request. CI runs strict, so a warning fails the build.

## Licence

Contributions to `docs/` are accepted under CC BY 4.0; contributions to code under MIT. See `LICENSE`.
