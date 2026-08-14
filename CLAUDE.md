# CLAUDE.md

Context for Claude Code sessions in this repo. Read this first.

## Working preferences

- **Australian English** throughout (organisation, optimise, behaviour, centre).
- **Never fabricate figures, statistics, dates, or citations.** If a number is needed and not in the repo, ask me — do not estimate, infer, or fill from training data. This is the single most important rule here; the book's credibility depends on it.
- **Ask rather than assume** when a fact about my work, projects, or context is missing.
- Prefer **tables and comparisons** over prose for technical trade-offs.
- Prose over bullet-fragments in the chapters themselves — the book reads as written argument, not slide notes.
- Be direct about problems. If something in the repo is wrong, weak, or unsupported, say so plainly rather than working around it.

## Read this too

`DECISIONS.md` records *why* the architecture is shaped the way it is — including alternatives that were considered and rejected. **Before changing anything structural** (the reference architecture, the licence split, where the boilerplate lives, the nav scheme), check whether there's already a decision recorded there. If you make a new structural decision, add an entry.

## What this repo is

**The AI Architecture Field Guide** — a public, living reference for architecting, governing, and costing agentic AI systems. Published free via GitHub Pages at `https://joarder.github.io/ai-architecture-field-guide/`.

Purpose: a practitioner reference I actually use to reason about workloads, *and* a public artefact establishing credibility and thought leadership in AI architecture. Both audiences matter — it has to be genuinely useful to me and defensible to a sharp reader.

## Repo layout

```
CLAUDE.md                     — this file
DECISIONS.md                  — why the architecture is shaped this way (read before structural changes)
LICENSE / LICENSE-CODE        — CC BY 4.0 for docs/, MIT for code
mkdocs.yml                    — site config + navigation (edit nav here when adding a chapter)
requirements.txt              — PINNED mkdocs-material version (see warning below)
bootstrap.sh                  — one-time macOS setup script (already run)
.github/workflows/deploy.yml  — auto-publishes on every push to main
docs/                         — THE BOOK. Only this directory is built into the site.
  index.md                    — landing page (contains the interactive stack diagram)
  stylesheets/stack-map.css   — styles for that diagram; registered via extra_css in mkdocs.yml
  01-mcp.md … 15-build-order.md
  references.md               — attribution + further reading
  tool/index.md               — page embedding the interactive analyzer
  tool/analyzer.html          — the Workload Architecture Analyzer (standalone, no build step)
boilerplate/                  — runnable reference implementation (NOT built into the site)
  main.py, src/*.py
```

**Important:** MkDocs only builds `docs/`. `boilerplate/` is deliberately outside it — it's shipped via the repo, not the site.

## The book's structure and its two structural commitments

Chapters are grouped: Connectivity → Cognition → Quality & Economics → Reliability & Security → Governance → Putting It Together.

Two commitments run through the whole thing and should be preserved in any edit:

1. **Governance sits in the request path, not beside it.** The reference architecture (in `02-orchestration.md`) draws a single execution chokepoint rather than a governance plane floating alongside the stack. The claim being made is "there is no second path," not "we have controls."
2. **The process clock and the run clock are separate.** A business process lives for months; an agent run lives for seconds. The stack diagram splits them.

The governing idea of the whole book: **the unit of account is the verified outcome, not the token.** Every chapter should ultimately feed that instrument (`11-cost-per-outcome-instrument.md`).

## The boilerplate

`boilerplate/` is a runnable support-ticket copilot demonstrating every pattern in the book. Zero dependencies, zero API keys — LLM calls are mocked in `src/model_router.py`'s `call_llm()`.

```bash
cd boilerplate && python3 main.py
```

| File | Chapter | Demonstrates |
|---|---|---|
| `src/mcp_tools.py` | 1 | Tool server/client: discover then invoke by name |
| `src/orchestrator.py` | 2 | Hub-and-spoke: direct handling vs delegation |
| `src/rag.py` | 3 | Just-in-time retrieval; working vs semantic memory |
| `src/evals.py` | 4 | Three-tier eval cascade |
| `src/model_router.py` | 5, 6 | Model-selection lever; cost cascade |
| `src/a2a_protocol.py` | 7 | Agent-to-agent delegation |
| `src/governance.py` | 10, 14 | Scoped agent identity, audit log, enforced denial |
| `src/cost_per_outcome.py` | 11 | Cost tagged to verified outcome |

**Critical constraint:** several chapters quote this code directly. If you change the boilerplate, check whether a chapter quotes the changed lines and update both in the same commit. That co-location is the main reason the code lives in this repo rather than a separate one.

## Current state

Chapters 1–15 plus `references.md` are written and published. The reference implementation runs. Strict mode passes with zero warnings.

The things most likely to need attention next, in rough priority:

1. **The analyzer's rule logic has not been validated against a real workload.** It's a first-pass hypothesis engine and the page says so — but if it's ever used to *argue* a position rather than illustrate one, that gap matters.
2. **Chapter code excerpts and `boilerplate/` must stay in sync.** Nothing enforces this automatically.
3. **Raw-HTML links in the landing-page diagram are unvalidated** — see gotchas below.

## Workflow

```bash
source .venv/bin/activate
mkdocs serve                  # preview at http://127.0.0.1:8000
git add . && git commit -m "..." && git push   # auto-deploys via GitHub Action
```

Adding a chapter: create `docs/NN-topic.md`, add it to `nav:` in `mkdocs.yml`, push.

### The interactive stack diagram

The landing page opens with a clickable block diagram of the L0–L7 stack (process tier → run tier with the chokepoint → run record, plus a cross-cutting rail). It's raw HTML in `docs/index.md` styled by `docs/stylesheets/stack-map.css`.

- It uses **Material's own CSS variables** (`--md-primary-fg-color`, `--md-accent-fg-color`, etc.) so light/dark mode works automatically. Don't hardcode colours.
- Links inside it are **raw HTML hrefs**, so MkDocs does *not* validate or rewrite them. They use output paths (`02-orchestration/`, not `02-orchestration.md`). **If you rename or move a chapter, these break silently** — strict mode will not catch it. Check them manually after any nav change.
- Two are anchor links (`#reference-architecture-vendor-agnostic-layering`, `#the-run-record`); renaming those headings breaks the jump.

### Known gotchas

- **`mkdocs build --strict` should pass with zero warnings.** If it doesn't, something is genuinely broken — treat a warning as a real problem, not noise. (The analyzer lives at `docs/tool/analyzer.html` beside its own page precisely so source and output paths agree; don't move it back under `docs/assets/`, which also collides with Material's theme assets.)
- **`requirements.txt` pins `mkdocs-material==9.7.6` deliberately.** MkDocs 2.0 is a breaking rewrite with no migration path. Don't unpin without checking that first.
- **`bootstrap.sh` has a bug**: its find-and-replace only rewrote `mkdocs.yml`, not `docs/*.md`. If reusing it elsewhere, widen the `sed`.

## Attribution discipline

The book synthesises published work from across the field, and `references.md` is not decoration — it's load-bearing for credibility.

- Where a framing is distinctly one author's, **name them in the chapter** and list them in `references.md`.
- Currently attributed in-chapter: Uchit Vyas ([hellouchit.com](https://hellouchit.com/)) for graded autonomy, the chokepoint principle, the two-clocks split, and run-record-as-audit-pack.
- Canonical field sources: MAST (Cemri et al.), Willison's lethal trifecta, Cognition/Anthropic/LangChain on multi-agent, Chroma on context rot, Anthropic on context engineering.
- **If you can't verify a claim at source, leave it out** rather than repeating it.

## Licensing

Dual-licensed, deliberately:

- **`docs/` (the book)** — CC BY 4.0. Reuse permitted including commercially, with attribution.
- **`boilerplate/`, `docs/tool/analyzer.html`, build tooling** — MIT.

See `LICENSE` and `LICENSE-CODE`. When adding content, keep the split intact — don't put substantive prose in `boilerplate/` or code in `docs/` outside the analyzer.

## Out of scope for this repo

Interview prep, client work, employer-specific material, and anything confidential do **not** belong here — it's a public repo with an automatic publish pipeline. Keep those in a separate folder outside this tree.
