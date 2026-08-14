"""
Chapter 4 — Evals & Observability
====================================
The three-tier eval pattern: deterministic checks on everything, a cheap
judge for common cases, an expensive judge sampled rarely. This is what
turns "produced an output" into "verified outcome" — the mechanism the
Chapter 11 instrument depends on.
"""
from dataclasses import dataclass


@dataclass
class EvalResult:
    verified: bool
    tier_used: str
    reason: str


def deterministic_check(response: str) -> EvalResult | None:
    """Near-zero cost. Run on 100% of traffic. Returns None if this tier
    can't make a verdict (i.e. needs escalation to a judge)."""
    if not response or response.strip() == "":
        return EvalResult(False, "deterministic", "empty response")
    if response == "LOW_CONFIDENCE":
        return EvalResult(False, "deterministic", "model signalled low confidence")
    return None   # can't verify content correctness deterministically — escalate


def lightweight_judge(response: str, query: str) -> EvalResult:
    """MOCK — stand-in for a small fine-tuned judge model (sub-200ms, cheap).
    Real version: a small classifier checking groundedness/relevance."""
    plausible = len(response) > 10 and "mock response" in response.lower()
    return EvalResult(plausible, "lightweight_judge",
                       "passed basic relevance/length heuristic" if plausible
                       else "failed basic relevance heuristic")


def full_llm_judge(response: str, query: str) -> EvalResult:
    """MOCK — stand-in for a frontier-model judge. Reserved for a 5-10%
    sample in production, or for high-stakes categories always."""
    # In production this would be a real LLM call scoring correctness,
    # tone, and policy compliance against a rubric.
    return EvalResult(True, "full_llm_judge", "frontier judge approved (mocked)")


def evaluate(response: str, query: str, high_stakes: bool = False) -> EvalResult:
    """The tiering logic itself: escalate only as far as needed."""
    det = deterministic_check(response)
    if det is not None:
        return det

    if high_stakes:
        return full_llm_judge(response, query)

    return lightweight_judge(response, query)
