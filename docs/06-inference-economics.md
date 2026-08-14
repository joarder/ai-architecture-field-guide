# Inference Economics

## The headline collapse

LLM inference cost has dropped ~1,000x in three years — GPT-4-equivalent performance runs about $0.40/million tokens vs. $20–30/million in late 2022. Four compounding factors: hardware generations (2–3x), software optimization like continuous batching/PagedAttention (2–3x), Mixture-of-Experts architecture efficiency (3–5x), and quantization (2–4x).

Inference now accounts for roughly two-thirds of total AI compute, up from a third in 2023 — the buildout's power draw is increasingly a *serving* problem, not a training problem.

## Five optimization levers

- **Quantization** (FP16→INT8/INT4) — 2–4x cost reduction, 95–99% accuracy retained
- **Continuous batching / PagedAttention** — 2–3x throughput
- **Speculative decoding** — 2–3x latency reduction
- **Response/prompt caching** — 3–10x on repeated queries; batch endpoints ~50% off real-time pricing
- **Model routing** (cascade) — cheap model first, escalate only when needed

Stacked together: 80%+ total cost reduction is achievable.

## The build-vs-buy threshold

Self-hosting only beats API pricing above ~50% sustained GPU utilization; below that, a GPU at 30% utilization costs ~3.3x more per inference than one at full utilization. A sovereign or national buildout betting on self-hosted capacity is implicitly betting on sustained high utilization — which requires sustained demand.

## The number worth citing directly

Measured inference energy cost: ~0.0001–0.002 Wh per output token (mid-range ~0.0005 Wh, ≈1.8 joules). Current hardware runs roughly 10¹⁹–10²⁰ times less efficient than the Landauer thermodynamic limit — a real number, and a large remaining efficiency runway.

## Reference implementation

From `src/model_router.py` — the model-cascade lever, the single biggest cost lever in most breakdowns, as actual escalation logic:

```python
def cascade_call(prompt):
    response, tokens = call_llm(prompt, tier="small")
    cost = (tokens / 1000) * MODEL_PRICING["small"]["cost_per_1k_tokens"]

    if response == "LOW_CONFIDENCE":
        response, tokens2 = call_llm(prompt, tier="frontier")   # escalate only when needed
        cost += (tokens2 / 1000) * MODEL_PRICING["frontier"]["cost_per_1k_tokens"]
        return response, CallRecord("frontier", tokens + tokens2, cost, escalated=True)

    return response, CallRecord("small", tokens, cost, escalated=False)
```

Running the full demo (`python main.py`) shows this concretely: a routine FAQ ticket costs ~$0.00003; a billing dispute that trips the escalation trigger costs ~$0.00077 — a ~25x difference, all from one `if` statement deciding whether the cheap tier was good enough.

## The point that resists easy optimism

Cost-per-token is collapsing fast while *volume* is growing even faster. Falling cost-per-token doesn't resolve a demand-sustainability question — it just changes what "enough demand" numerically means. See [Cost-per-Verified-Outcome](11-cost-per-outcome-instrument.md) for why volume without verification is not the same as value.
