"""
Chapter 5 — Prompt vs RAG vs Fine-tune vs Distill
Chapter 6 — Inference Economics
====================================================
A model router implementing the cascade pattern from Chapter 6 (cheap model
first, escalate on low confidence) and a cost ledger implementing the
Chapter 11 instrument (tag every call with cost AND outcome, not just cost).

Swap-in point: replace call_llm() with real API calls (Anthropic, OpenAI,
a self-hosted model). The economics/routing logic doesn't change — only
this one function does.
"""
from dataclasses import dataclass, field


# --- Mocked model tiers, priced roughly like real 2026 spreads -------------
MODEL_PRICING = {
    "small":    {"cost_per_1k_tokens": 0.0004},   # e.g. a distilled/small model
    "frontier": {"cost_per_1k_tokens": 0.015},    # e.g. a frontier model
}


def call_llm(prompt: str, tier: str = "small") -> tuple[str, int]:
    """MOCK — replace with a real API call. Returns (response_text, tokens_used).
    The mock fakes 'confidence' by looking for keywords that a real small model
    would plausibly struggle with, to make the cascade demo meaningful."""
    tokens_used = max(20, len(prompt.split()) * 2)

    hard_signal = any(w in prompt.lower() for w in ["dispute", "legal", "cancel", "chargeback"])
    if tier == "small" and hard_signal:
        return "LOW_CONFIDENCE", tokens_used   # signals the cascade to escalate

    if "account data" in prompt.lower():
        return "Mock response: here's your account status based on the billing lookup.", tokens_used
    return "Mock response: answered from FAQ context.", tokens_used


@dataclass
class CallRecord:
    tier_used: str
    tokens: int
    cost_usd: float
    escalated: bool = False


def cascade_call(prompt: str) -> tuple[str, CallRecord]:
    """Chapter 6's model-cascade lever: try the cheap tier, escalate only on
    low confidence. This is the single biggest cost lever in most breakdowns —
    made concrete instead of abstract."""
    response, tokens = call_llm(prompt, tier="small")
    cost = (tokens / 1000) * MODEL_PRICING["small"]["cost_per_1k_tokens"]

    if response == "LOW_CONFIDENCE":
        response, tokens2 = call_llm(prompt, tier="frontier")
        cost += (tokens2 / 1000) * MODEL_PRICING["frontier"]["cost_per_1k_tokens"]
        return response, CallRecord("frontier", tokens + tokens2, cost, escalated=True)

    return response, CallRecord("small", tokens, cost, escalated=False)


def recommend_lever(task_shape: str, monthly_volume_tokens: int) -> str:
    """Chapter 5's decision sequence, as code instead of prose."""
    if task_shape == "stable-behavior" and monthly_volume_tokens > 50_000_000:
        return "distill"          # pays back at this volume
    if task_shape == "stable-behavior":
        return "fine-tune"        # form/tone consistency, volume too low to distill yet
    if task_shape == "rag-heavy":
        return "rag"              # value comes from changing facts, not stable behaviour
    return "prompt"               # exhaust this layer first — most teams under-use it
