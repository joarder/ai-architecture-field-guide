# Runtime Control Patterns

Governance chapters describe *what* should be true. This chapter covers the runtime mechanisms that make it true — the patterns that turn a policy statement into something a system enforces whether or not anyone is watching.

!!! note "Attribution"
    Graded autonomy, the run-record structure, and several of the anti-pattern diagnostics below are drawn from Uchit Vyas's published work at [hellouchit.com](https://hellouchit.com/). See [References](references.md).

## Where the structural patterns live

Two of the most important runtime patterns — the **two clocks** (process tier vs run tier) and the **single chokepoint** — are structural enough that they're drawn into the reference architecture itself in [Agent Orchestration](02-orchestration.md) rather than treated as add-ons here. This chapter covers the patterns that sit *inside* that structure.

## Graded autonomy

The useful question isn't "is this agent autonomous." It's *how much autonomy, for which class of action* — and the level in force gets written to the run record:

| Level | Meaning |
|---|---|
| **Propose-only** | Agent drafts; a human commits |
| **Act-then-notify** | Agent acts; a human is informed after |
| **Act-within-envelope** | Agent acts freely inside defined bounds (spend, scope, reversibility) |
| **Act-freely** | No per-action gate |

The gate then has two outcomes: **auto-commit** (reversible, internal, within the declared level) or **review queue** (irreversible, commercial, or client-facing).

Two sharp observations worth internalising:

- **A sustained approval rate above ~95% means you have automation with a liability sponge attached, not oversight.** Rejection records are the evidence that review is doing real work. If nothing is ever rejected, the reviewer is rubber-stamping and you've added latency without adding control.
- **Reversibility is a property of the system, not the agent.** The same delete is reversible against a versioned store and irreversible against a live one. "Can the agent undo this?" is the wrong question; "does the substrate support undo?" is the right one.

## The run record

Capture, per run: the exact assembled context plus a hash of it, retrieved knowledge IDs, upstream run IDs, every policy decision with its reason, prompt version, model, tokens, cost, latency, and a groundedness map of claim-to-citation *including unsupported claims*.

The insight that makes this worth the storage: **the evidence a regulator wants and the dataset your improvement loop needs are the same rows.** Audit and learning are usually funded as separate initiatives; they're the same artefact. It also enables replay from any step, which is the difference between debugging an agent and guessing about it.

The corollary most systems get wrong: storing only *final state* throws away the highest-value learning signal. The two signals that beat any offline benchmark are **field-level diffs of what a human changed** and **predictions linked to outcomes** — and the first is destroyed by overwriting.

## Prompts belong in a datastore, not in code

Prompts as string literals inside service code is a persistent anti-pattern. The test: *what changed in the prompt last week?* If answering requires git archaeology across application commits, the prompt is inline.

The better shape is a prompt registry with lifecycle states — `draft → canary → active → retired` — with canary percentage and output schema stored alongside. **Rollback becomes a row update, not a release.**

Related: pin your model versions. Grep your codebase for `latest`, `stable`, `current`, `default` — an unpinned model reference means your production behaviour can change without a deploy.

## Confidentiality as a retrieval tier

Where multiple sensitivity levels coexist, make them separate retrieval tiers resolved at the chokepoint **from caller context, never from the prompt**. Promotion between tiers is an explicit, reviewed act. Row-level security from the first migration, not retrofitted.

This is the concrete implementation of the "inference control" layer of sovereignty from [Australian AI Governance](08-au-governance.md) — controlling what the model can *reach*, not just where it runs.

## Blast radius

Step ceilings, spend ceilings, rate ceilings, and a **tested** kill switch. The nuance that separates a real kill switch from a claimed one: stopping an agent *between* steps is easy; stopping one halfway through a multi-call action is the case that matters. The metric is **time from decision to halt**, and it's only meaningful if you've measured it.

## Anti-patterns to check yourself against

| Anti-pattern | The diagnostic question |
|---|---|
| **The eval set that never runs** | What happens to a deploy whose prompt change drops a critical eval score by 30%? If it ships, the eval set is decorative |
| **Model-as-latest** | Is any production model reference unpinned? |
| **The inline prompt** | What changed in the prompt last week? |
| **Vault theatre** | How long is the credential valid? Over an hour and it's effectively static |
| **PDF principles** | Is this principle encoded in a platform default or policy-as-code? If not, it doesn't exist at runtime |

## Reference implementation

`boilerplate/src/governance.py` implements the minimal versions of three of these: scoped identity per agent (the authorize step of the chokepoint), TTL on that scope (short-lived credentials), and an audit log recording every attempt with its allow/deny outcome and reason (the beginnings of a run record). The demo deliberately shows a *denial* as well as an approval — a permission system you've only ever seen approve is untested.
