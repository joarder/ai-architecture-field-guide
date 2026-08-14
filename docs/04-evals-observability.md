# Evals & Observability

Evals are the mechanism that turns "produced an output" into "verified outcome." Without an eval gate, every token spend is productive by definition — there's no mechanism to demote it to wasteful.

## The three-tier taxonomy (mirrors cost tiering)

1. **Deterministic checks (near-zero cost)** — schema validation, tool-call format, JSON parsing, safety filters. Run on 100% of traffic.
2. **Lightweight model judge (low cost)** — a small fine-tuned judge (~440M params), sub-200ms latency, for hallucination/grounding checks at scale.
3. **Full LLM-as-judge (medium/high cost)** — a frontier model for nuanced scoring: reasoning quality, instruction-following. Reserved for a 5–10% production sample.

Rule of thumb: deterministic metrics for exact checks, LLM-as-judge only for genuine judgment calls. Using a frontier judge to check whether JSON parsed is the eval equivalent of using a frontier model for arithmetic.

## Trace-based evaluation

Score *spans* inside the execution trace — each tool call, retrieval step, reasoning span, sub-agent handoff — not just the final answer. This localizes a failure to the exact layer that caused it (tool call vs. reasoning vs. retrieval), rather than just knowing the answer was wrong.

## Three points in the lifecycle

- **Offline** — against curated golden datasets, pre-release
- **Pre-merge/CI** — before any prompt or model change ships
- **Online** — sampled against live production traffic, in the same dashboard as cost and latency

That last point matters most for governance: mature platforms put quality, cost, and latency in one dashboard — meaning cost-per-verified-outcome can be a *live* production metric, not a retrospective calculation, if eval score and cost tag share a trace ID.

## Reference implementation

From `src/evals.py` — the three-tier cascade as actual escalation logic, not just a policy diagram:

```python
def evaluate(response, query, high_stakes=False):
    det = deterministic_check(response)      # near-zero cost, 100% of traffic
    if det is not None:
        return det                            # short-circuit — no judge needed

    if high_stakes:
        return full_llm_judge(response, query)   # reserved for the risky sample

    return lightweight_judge(response, query)    # the common-case default
```

In `orchestrator.py`, billing tickets are marked `high_stakes=True` and FAQ tickets aren't — this is the routing decision from Chapter 4 applied, not just described: regulated/financial outcomes get the expensive judge, routine ones don't.

## The sharp edge

LLM-as-judge is itself non-deterministic and needs calibration against human review. Validate judge behavior against a human-reviewed sample periodically — especially for safety-sensitive or high-stakes outputs. You can pay to verify with a system that has its own error rate.
