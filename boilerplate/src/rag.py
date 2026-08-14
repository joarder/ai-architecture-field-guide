"""
Chapter 3 — Context, Memory & RAG
===================================
A deliberately simple retrieval implementation: keyword overlap scoring
instead of embeddings, so this runs with zero dependencies and zero API
calls. The point is the *pattern* (agent decides to retrieve, gets scoped
context back, uses it) not the retrieval algorithm's sophistication.

Swap-in point: replace `search()`'s scoring with a real embedding model +
vector store (e.g. sentence-transformers + a FAISS/pgvector index) — the
call signature agents use doesn't need to change.
"""

FAQ_DOCS = {
    "refund-policy": "Refunds are available within 30 days of purchase for annual plans, "
                      "and within 14 days for monthly plans. Refunds are processed to the "
                      "original payment method within 5-7 business days.",
    "plan-upgrade": "You can upgrade your plan at any time from Account Settings > Billing. "
                     "Upgrades take effect immediately and are billed pro-rata for the "
                     "remainder of the current cycle.",
    "downtime-credit": "If a service outage exceeds our published SLA, affected customers "
                        "receive an automatic account credit calculated as a percentage of "
                        "the monthly fee proportional to the downtime duration.",
    "password-reset": "Password resets are self-service via the 'Forgot password' link on "
                       "the login page. Reset links expire after 1 hour.",
}


def search(query: str, top_k: int = 2) -> list[str]:
    """Just-in-time retrieval: score docs by keyword overlap, return only
    the top few — never the whole corpus. This is the Chapter 3 lesson made
    literal: retrieve scoped context, not everything you have."""
    query_words = set(query.lower().split())
    scored = []
    for doc_id, text in FAQ_DOCS.items():
        overlap = len(query_words & set(text.lower().split()))
        if overlap > 0:
            scored.append((overlap, doc_id, text))
    scored.sort(reverse=True)
    return [text for _, _, text in scored[:top_k]]


class WorkingMemory:
    """Chapter 3's three-layer memory model, layer 1: this conversation only.
    Gone when the session ends — managed by truncation here, by real
    summarization/compaction in production."""

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.turns: list[dict] = []

    def add(self, role: str, content: str):
        self.turns.append({"role": role, "content": content})
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]   # crude compaction

    def as_context(self) -> str:
        return "\n".join(f"{t['role']}: {t['content']}" for t in self.turns)


class SemanticMemory:
    """Layer 3: facts that persist and get *updated*, not just appended —
    the property plain vector stores lack (Chapter 3's core critique)."""

    def __init__(self):
        self._facts: dict[str, str] = {}

    def upsert(self, key: str, value: str):
        self._facts[key] = value   # overwrite, don't append — this is the point

    def get(self, key: str) -> str | None:
        return self._facts.get(key)
