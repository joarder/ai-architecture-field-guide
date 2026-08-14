# Prompt vs RAG vs Fine-tune vs Distill

## The 2026 sequence: Prompt → RAG → Fine-tune → Distill

Each step up is a bigger commitment. Don't reach for the next tier until the one before it is genuinely exhausted.

### 1. Prompting — the default, underrated
Zero training cost, instantly reversible, portable across model upgrades. Few-shot, chain-of-thought scaffolding, schema-constrained decoding, ReAct loops — most teams haven't exhausted this layer before reaching for fine-tuning. Failure mode: brittleness — a 4,000-token prompt holding fifteen rules is a Jenga tower.

### 2. RAG — for facts that change
Ceiling problem: if the base model lacks domain understanding entirely, more context doesn't bridge that.

### 3. Fine-tuning — for form, not facts
Shapes behavior, tone, structured-output reliability, refusal patterns — the wrong tool for knowledge that changes weekly (that's RAG's job). Thin LoRA/QLoRA adapters on a strong base model dominate; full fine-tuning is rarely justified. **The real cost is the eval harness, data curation, and 12-month lifecycle ownership — not training compute.** You need the eval harness *before* training starts, or you can't tell if a checkpoint improved anything.

### 4. Distillation — for cost, not capability
Train a smaller "student" on a larger "teacher's" outputs. DeepSeek-V3 was reportedly distilled from R1 for ~$10,000. Broader guidance: projects run $35K–120K, pay back in 3–7 months — but only above ~50M tokens/month of a narrow, stable workload. Loses badly on open-ended generation, rapidly evolving domains, and reasoning-heavy chain-of-thought work — those stay on frontier models.

## Reference implementation

From `src/model_router.py` — the Chapter 5 decision sequence as a function, not just prose:

```python
def recommend_lever(task_shape, monthly_volume_tokens):
    if task_shape == "stable-behavior" and monthly_volume_tokens > 50_000_000:
        return "distill"          # pays back at this volume
    if task_shape == "stable-behavior":
        return "fine-tune"        # volume too low to distill yet
    if task_shape == "rag-heavy":
        return "rag"              # value comes from changing facts
    return "prompt"               # exhaust this layer first
```

## Wiring into cost-per-verified-outcome

| Tier | Fixed cost | Per-call cost | Ceiling |
|---|---|---|---|
| Prompting | ~none | highest | base model's raw capability |
| Fine-tuning | real (data + eval harness) | lower | tighter behavioral consistency |
| Distillation | highest | lowest | only pays back at volume |

This is a genuine break-even/capacity-planning calculation, not just a technical preference.
