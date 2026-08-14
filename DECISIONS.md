# Decisions

Why this repo is shaped the way it is. CLAUDE.md records *what* is here; this records *why*, so the reasoning doesn't have to be reconstructed — or re-argued — later.

Format: decision, the alternative considered, and what tipped it.

---

## D1 — Governance sits in the request path, not beside it

**Decision.** The reference architecture in `02-orchestration.md` draws a single execution chokepoint enclosing L2–L5, rather than a governance plane floating alongside the stack.

**Alternative.** The original drawing had governance as a cross-cutting plane below the stack — architecturally honest, and how most stack diagrams do it.

**What tipped it.** A cross-cutting concern is precisely the thing that gets deferred to "phase two," because nothing structurally requires it. Drawing it as the one path every execution passes through changes the claim being made: not *we have controls*, but **there is no second path**. A control that can be bypassed by importing the provider SDK is not a control.

**Cost accepted.** The diagram is busier, and the layering is less immediately clean.

---

## D2 — The process clock and the run clock are separate tiers

**Decision.** The stack has a process tier (durable rows, event log, reconciler) above the run tier (retries, timeouts, fan-out for one step).

**Alternative.** A single flat L0–L7 describing one run, which is what the guide had originally.

**What tipped it.** The flat stack had no time dimension at all. Without the split, "which steps are still outstanding?" is something you *remember* rather than something you *query*. Coverage becomes computed instead of tracked.

---

## D3 — The book keeps its own economic instrument rather than adopting an external control set wholesale

**Decision.** Cost-per-**verified**-outcome, with eval-tiering as the mechanism that makes "verified" computable, stays the spine of the book.

**Alternative.** Adopting cost-per-*resolved*-task, the more established framing.

**What tipped it.** "Resolved" does a large amount of unexamined work in that phrase. Without an eval gate, every token is productive by default and there is no mechanism to demote it. The eval-tiering layer is a genuine addition rather than a restatement, and it's the part of this guide that's actually original.

---

## D4 — Vendor-agnosticism is a first-class constraint

**Decision.** Every layer boundary is described as a contract, not a product. No chapter assumes a specific vendor, framework, or substrate.

**Alternative.** An opinionated, regulated-enterprise-shaped architecture that names specific identity patterns, policy engines, and data controls.

**What tipped it.** The opinionated version is more immediately actionable but less portable, and portability is the argument this guide actually needs to make. The Australian governance chapter is the one deliberate exception — jurisdiction-specific by nature.

---

## D5 — Build order is stated explicitly

**Decision.** `15-build-order.md` sequences the work into Wave 0–3, plus a "defer deliberately" list.

**Alternative.** Leave sequencing implicit; the chapters describe choices, readers decide order.

**What tipped it.** A descriptive reference tells you what exists but never what to do first. The eval-set-before-everything dependency in particular is load-bearing and easy to miss — fine-tuning, distillation, routing and cost-per-verified-outcome are all *uncomputable* without it.

---

## D6 — The boilerplate lives in this repo, not a separate one

**Decision.** `boilerplate/` sits at repo root, outside `docs/` so MkDocs ignores it.

**Alternative.** A separate `support-copilot-boilerplate` repo, which is the more conventional "clone and run" shape.

**What tipped it.** Several chapters quote the code directly. Two repos means the quotes can silently drift from the implementation, and a book that misquotes its own reference implementation is worse than one with no code at all. Co-location means one commit updates both.

**Cost accepted.** Slightly weaker "here's a runnable repo" framing; the code is a directory rather than a project.

---

## D7 — Dual licence: CC BY 4.0 for content, MIT for code

**Decision.** `docs/` under CC BY 4.0; `boilerplate/`, the analyzer, and build tooling under MIT.

**Alternative.** A single permissive licence across everything.

**What tipped it.** The two artefacts want different things. The book's purpose is reach with attribution attached — CC BY is built for exactly that. The code's purpose is frictionless reuse, where an attribution requirement is just an obstacle.

---

## D8 — Third-party framings are attributed in-chapter, not just in references

**Decision.** Where a framing is distinctly one author's, they're named in the chapter itself as well as in `references.md`.

**Alternative.** A single references page, which is normal practice for a synthesis.

**What tipped it.** The book's stated purpose is credibility. Anything that could read as absorbing another practitioner's framework without credit undercuts that faster than any technical error would. When in doubt, over-attribute.

---

## D9 — Nav sections dropped their "Layer N" prefixes

**Decision.** Sections are named Connectivity, Cognition, Quality & Economics, Reliability & Security, Governance, Putting It Together.

**Alternative.** Continue "Layer 1 — Connectivity" and renumber to close the gap.

**What tipped it.** Two competing numbering schemes in a book about layered architecture: nav "Layer 1–4" versus the stack's "L0–L7". Reserving "layer" language for the thing that genuinely is a layered stack makes the diagram land harder.

---

## D10 — The analyzer lives beside its page, not in `docs/assets/`

**Decision.** `docs/tool/analyzer.html` sits next to `docs/tool/index.md`.

**What tipped it.** Two problems at once: MkDocs' strict link checker resolves source paths while `use_directory_urls` changes output paths, so the old relative link warned on every build; and our file was landing in `site/assets/` alongside Material's own theme output, one name collision from breaking. Co-locating fixes both, and strict mode now passes with zero warnings — which means a future warning is a real signal.

---

## Open questions

Not yet decided; noted so they aren't mistaken for oversights.

- **Memory architecture chapter.** Currently a section within `03-context-memory-rag.md`. It may deserve its own chapter as the vendor landscape matures.
- **Whether the guide should carry worked case studies.** Currently it's patterns plus a reference implementation; case studies would strengthen it but require real, non-confidential material.
- **MkDocs 2.0.** A breaking rewrite with no migration path. `requirements.txt` is pinned deliberately; revisit only when the licensing and plugin situation settles.
- **The analyzer's rule logic** is a first-pass hypothesis engine. It has not been validated against a real workload the author knows well. Until it is, it should be described as a starting hypothesis, which is how the page currently frames it.
