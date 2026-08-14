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

## The memory landscape, and the cost trade-off inside it

The architectural choice here is usually framed as a feature comparison. It's really a cost decision:

| Approach | How it works | Trade-off |
|---|---|---|
| **Self-editing** (Letta / MemGPT lineage) | Virtual-memory hierarchy; the *agent* pages information in and out via memory tools | Adaptive and inspectable — but **every memory operation costs inference tokens**, because the agent reasons about what to store |
| **Passive extraction** (Mem0 lineage) | Facts extracted automatically into scoped stores over hybrid vector + graph + KV | Consistent and token-efficient; can't make nuanced in-context judgements |
| **Temporal graph** (Zep / Graphiti) | Knowledge graph maintaining validity periods for facts | Solves supersession directly, at the cost of a heavier substrate |
| **Provider-managed** | Built-in memory features | Zero build, zero control |
| **Custom schema** | Your own tables | Full control, full maintenance |

**Three observations that connect memory to cost and reliability:**

1. **Self-editing memory has a token tax.** Spending inference on every turn to decide what to remember is a real, recurring cost — an architectural trade-off, not a feature preference.
2. **Memory is a retrieval-quality problem that degrades over time, not a storage problem.** A store that can't represent supersession gets *worse* as it grows, so memory quality and token efficiency decay together.
3. **Compaction is where cost and reliability failures meet.** MAST (see [Agent Reliability](12-agent-reliability.md)) names loss-of-conversation-history and step-repetition as distinct failure modes; both are compaction failures. Bad compaction costs money *and* causes the incident.

## Programmatic tool calling

The highest-leverage context lever most teams haven't pulled: rather than the model calling tools one at a time with every intermediate result landing in the context window, the model **writes code that orchestrates the tools**, and only the final result returns to the window.

For any workflow with several chained calls and large intermediate payloads — filtering a large result set, joining two API responses, iterating over a list — this removes the intermediates from context entirely. It's the difference between the model *reading* every row and the model *writing a query*.

## Why this matters economically

Poor context engineering hurts both sides of the value equation at once: it raises cost (more tokens) *and* lowers output quality (context rot) simultaneously. See [Cost-per-Verified-Outcome](11-cost-per-outcome-instrument.md).
