# The Instrument: Cost-per-Verified-Outcome

## The core principle

The unit of account must be the **verified outcome**, not the token. Falling cost-per-token doesn't resolve whether an AI investment is sustainable — it just changes what "enough demand" numerically means. Volume without verification is noise wearing the costume of value.

## Three layers

- **L1 — Unit economics**: cost per verified outcome
- **L2 — Value realization**: reconciled to P&L
- **L3 — Value-density**: verified value per kWh, usable as a policy/infrastructure gating instrument

## The levers that move L1 — everything in this guide is one of these

| Lever | Mechanism | Chapter |
|---|---|---|
| **Context engineering** | Poor context raises cost *and* lowers quality simultaneously (context rot) | [Context, Memory & RAG](03-context-memory-rag.md) |
| **Eval-tiering** | Makes a token spend countable as "verified" at all — without an eval gate, every token is productive by default | [Evals & Observability](04-evals-observability.md) |
| **Model-selection lever** | Prompt → RAG → Fine-tune → Distill is a break-even calculation trading fixed cost against per-call cost at a given accuracy ceiling | [Model Economics](05-model-economics.md) |
| **Inference economics** | Supply-side grounding — cost-per-token collapse doesn't resolve demand sustainability; self-hosted bets require sustained utilization | [Inference Economics](06-inference-economics.md) |

## Common design patterns for optimizing cost-per-verified-outcome

**Cost reduction**
- Model cascade/routing — cheap model first, escalate on failure
- Prompt/semantic caching — 41–80% savings measured on agentic workloads
- Plan/skill reuse — store a validated plan, replay instead of re-deriving. *The most expensive token is the one spent rediscovering a plan you already know works.*
- Bounded reflection loops — cap self-critique cycles; a 10-cycle reflection loop can cost ~50x a single pass

**Verification confidence**
- Verification-gated execution — separate, cheaper verification pass gates the action
- Structured output contracts — deterministic parsing beats another LLM call judging free text
- Runtime supervision — lightweight oversight can cut multi-agent token consumption ~30%

**Structural (avoid the waste before it happens)**
- Sub-agent context isolation
- Just-in-time retrieval / lazy tool loading

**Instrumentation underneath all of it**
None of the above matters unless spend is tagged by outcome, not just counted in raw tokens — classify consumption as productive / inefficient / wasteful against the specific verified result it produced.

## Reference implementation

From `src/cost_per_outcome.py` — the whole instrument in one function. Every call is logged with cost **and** eval verdict; the summary computes cost per outcome that actually passed verification, not per call made:

```python
def summary(self):
    total_cost = sum(r.cost_usd for r in self.records)
    verified_records = [r for r in self.records if r.verified]
    verified_cost = sum(r.cost_usd for r in verified_records)

    return {
        "verification_rate": len(verified_records) / len(self.records),
        "total_cost_usd": total_cost,
        "wasted_cost_usd": total_cost - verified_cost,
        "cost_per_verified_outcome_usd": verified_cost / len(verified_records),
    }
```

Running the full demo produces a real report:

```
--- Cost-per-Verified-Outcome Report -----------------------
  total_calls                 : 5
  verified_outcomes           : 5
  verification_rate           : 1.0
  total_cost_usd              : 0.00086
  wasted_cost_usd             : 0.0
  cost_per_verified_outcome_usd: 0.00017
  escalation_rate             : 0.2
--------------------------------------------------------------
```

Every other chapter's module feeds this number: MCP/A2A determine which calls happen, RAG/memory determine context cost, the model router determines per-call cost, evals determine `verified`, and governance determines what's even allowed to run. Change any one of them and this report changes — which is the whole point of treating it as *the* instrument rather than one metric among many.

## Why this is the right instrument for a demand-sustainability question

The trillion-dollar AI buildout's central risk isn't supply — it's whether the public and industry consume enough, *durably* enough, to absorb it. Cost-per-verified-outcome is the metric that distinguishes durable consumption from noise, because it's the only one of the candidates that fails visibly when volume isn't backed by verification.
