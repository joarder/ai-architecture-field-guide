# Build Order: What to Do First

Every other chapter describes what exists and how to choose. This one answers the question they don't: **in what order?**

The sequencing principle is simple — do the things that make later things *cheaper or knowable* first. Most of what follows is not expensive; it's just easy to defer until it's expensive to add.

## Wave 0 — before the first user

Nothing here requires a platform investment. Skipping any of it makes everything after it guesswork.

| Do this | Why first |
|---|---|
| **Name the outcome and its baseline** | If you can't say what success is against what it's replacing, no later measurement means anything |
| **Build an eval set (~50 cases minimum) with known-good answers** | This is the prerequisite for every other decision in this guide — you cannot tell whether a prompt change, a model swap, or a fine-tune helped without it. See [Evals](04-evals-observability.md) |
| **Decide your task tier** — workflow, pipeline, or true agent | Determines whether your costs are boundable at all. See [Agent Reliability](12-agent-reliability.md) |
| **Pin your model version** | An unpinned reference means production behaviour changes without a deploy |

**The hard dependency worth stating plainly:** the eval set gates everything downstream. Fine-tuning, distillation, model routing, and cost-per-verified-outcome are all *uncomputable* without it. Teams that defer evals aren't deferring measurement — they're deferring the ability to make any of the later decisions on evidence.

## Wave 1 — with the first deploy

| Do this | Why now |
|---|---|
| **One chokepoint** — a single execution path | Retrofitting this after multiple call sites exist is a refactor, not a config change. See [Orchestration](02-orchestration.md) |
| **Per-run tracing with replay** | Without it you're debugging by guessing |
| **Workload identity per agent** | Attribution is impossible to reconstruct retrospectively — you can't tell which agent did what after the fact |
| **Treat all retrieved and tool-returned content as untrusted data, never instructions** | Architectural, not a filter. Retrofitting means re-auditing every tool. See [Agent Security](13-agent-security.md) |
| **Bound the blast radius** — step, spend and rate ceilings | Cheap to add now; expensive to explain later |

## Wave 2 — within the first month

| Do this | Why here |
|---|---|
| **Eval-gated deploys** — the eval set blocks a merge on regression | An eval set that doesn't gate anything is decorative |
| **Prompts out of code, into a registry** | Rollback becomes a row update rather than a release |
| **Cost tagged per verified outcome**, attributed to the consuming feature | Raw token counts don't tell you whether spend produced value. See [The Instrument](11-cost-per-outcome-instrument.md) |
| **Input and output guardrails for the two failure modes you most fear** | Named, not generic — a guardrail tuned for nothing catches nothing |
| **Graded autonomy per action class**, recorded per run | See [Runtime Controls](14-runtime-controls.md) |

## Wave 3 — the platform investment

These are the ones that make the *next ten* features cheap rather than this one safe:

- **Audit evidence generated at decision time, not audit time** — the run record as both compliance artefact and training signal
- **Risk-tiered governance with written criteria** rather than committee judgement
- **Confidentiality as a retrieval tier**, resolved from caller context
- **Provenance across agents** — outputs traceable to the upstream runs that produced their inputs
- **Process/run tier separation** with a reconciler

## What to defer deliberately

Equally important, and rarely written down:

- **Multi-agent orchestration (L4)** — until you've proven a single agent can't do it, and specifically until you've established the task is read-heavy rather than write-heavy
- **Fine-tuning** — until prompting is genuinely exhausted, and the eval harness exists to tell you if it helped
- **Distillation** — until volume clears the break-even (roughly 50M tokens/month of stable, narrow workload)
- **A memory architecture** — until you know whether you need working, episodic, or semantic memory; they have different costs and different failure modes

## The one-line version

Evals first, because nothing downstream is measurable without them. Then a single execution path, because retrofitting one is a rewrite. Then cost attribution, because unmeasured spend can't be optimised. Everything else is a choice; those three are prerequisites.
