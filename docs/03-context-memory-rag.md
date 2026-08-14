# Context, Memory & RAG

## RAG isn't a layer — it's a pattern spanning layers

Classic RAG inserted retrieval as a fixed pre-processing step before the model ever ran. **Agentic RAG** (the 2026 default) moves retrieval inside the reasoning loop: the agent decides *if*, *when*, and *how many times* to retrieve, calling it as a tool like any other MCP capability. Retrieval isn't architecturally special anymore.

## Untangling "stateless" — two unrelated claims

1. **The model (L3) is stateless** — always has been. Every inference call is independent.
2. **MCP's transport is going stateless** (July 2026 spec) — an infrastructure/scaling decision about server sessions, unrelated to memory.

Memory doesn't make the *model* stateful — it makes the *system* stateful by reconstructing the right context fresh on every call. Conflating these two is an easy trap because "stateless" is doing double duty.

## The three-layer memory model (2026 consensus)

- **Working memory** — the live context window: current conversation, loaded files, this turn's tool results. Gone at session end. Not a retrieval problem — a *budget* problem, managed by compression/summarization.
- **Episodic memory** — history of past sessions, retrieved when relevant.
- **Semantic memory** — accumulated facts about entities/relationships that get *updated*, not just appended. Plain vector stores don't know a fact has been superseded — retrieval quality degrades as the corpus grows.

**Context engineering** is the discipline name for orchestrating all of this — memory + RAG + tool outputs + system constraints + per-agent visibility boundaries — as a single designed "operating system" for the agent, rather than an afterthought.

## Context rot — the enemy

A measured, real phenomenon: model performance degrades as input length grows, even on tasks the model handles fine with a smaller, curated context. A 1M-token window doesn't repeal this — it just raises the point where the rot becomes visible. Frontier models show 30%+ accuracy degradation in mid-window positions.

**Best-practice levers** (roughly by ROI):

- Just-in-time retrieval instead of upfront dumps
- Lazy tool/schema loading — discover on demand, not at session start
- Prompt caching for static context blocks
- Sub-agent context isolation — each specialist gets a clean, scoped window
- Session compaction/summarization instead of replaying full history
- Budget by context-window *fill percentage*, not raw token count — compact proactively past ~60% full

## Reference implementation

From `src/rag.py`. Retrieval scores by keyword overlap (zero dependencies, so the demo runs with no API key) and returns only the top few chunks — never the whole corpus, which is the Chapter 3 lesson made literal:

```python
def search(query, top_k=2):
    """Just-in-time retrieval: score, return only the top few."""
    query_words = set(query.lower().split())
    scored = []
    for doc_id, text in FAQ_DOCS.items():
        overlap = len(query_words & set(text.lower().split()))
        if overlap > 0:
            scored.append((overlap, doc_id, text))
    scored.sort(reverse=True)
    return [text for _, _, text in scored[:top_k]]
```

`WorkingMemory` truncates rather than accumulating (a crude stand-in for real compaction); `SemanticMemory` **overwrites** on `upsert()` rather than appending — the exact property plain vector stores lack:

```python
class SemanticMemory:
    def upsert(self, key, value):
        self._facts[key] = value   # overwrite, don't append — this is the point
```

**Swap-in point**: replace `search()`'s keyword scoring with a real embedding model + vector index (sentence-transformers + FAISS/pgvector) — the call signature agents use doesn't change.

## Why this matters economically

Poor context engineering hurts both sides of the value equation at once: it raises cost (more tokens) *and* lowers output quality (context rot) simultaneously. See [Cost-per-Verified-Outcome](11-cost-per-outcome-instrument.md).
