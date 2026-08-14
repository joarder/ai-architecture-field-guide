# References & Further Reading

This guide synthesises published work from across the field. Where a framing is distinctly one author's, it's named in the chapter and listed here. Anything I couldn't verify at source has been left out rather than repeated.

## Context engineering

- **Anthropic — "Effective context engineering for AI agents."** The canonical framing: context is a finite resource, and the engineering question shifts from *what words do I use* to *what configuration of context is most likely to produce the desired behaviour.*
- **Chroma — "Context Rot: How increasing input tokens impacts LLM performance."** The empirical backbone for Chapter 3. Longer context does not monotonically help.
- **Liu et al. — "Lost in the Middle"** (TACL 2024). The positional-degradation result that pairs with the above.

## Multi-agent architecture

- **Cemri et al. — "Why Do Multi-Agent LLM Systems Fail?"** (UC Berkeley; NeurIPS 2025 Datasets & Benchmarks). The MAST taxonomy: 1,600+ annotated traces, 14 failure modes, three clusters. Source for [Chapter 12](12-agent-reliability.md).
- **Cognition — "Don't Build Multi-Agents"** (Walden Yan). The case against; note the author publicly revised his position in 2026 — still sceptical of most designs, but reporting some that now work.
- **Anthropic — "How we built our multi-agent research system."** The case for, published in the same period.
- **LangChain — "How and when to build multi-agent systems."** The reconciliation: read-heavy fans out, write-heavy doesn't.

## Security

- **Simon Willison — "The lethal trifecta."** Private data + untrusted content + external communication. The structural framing used throughout [Chapter 13](13-agent-security.md). Willison is also the clearest voice on why prompt injection and jailbreaking are different problems.
- **Beurer-Kellner et al. — "Design patterns for securing LLM agents against prompt injections"** (arXiv 2506.08837).
- **Google DeepMind — CaMeL.** Architectural mitigation literature.
- **MELON** (ICML 2025). Runtime detection via masked-prompt trajectory comparison, with published attack-success reductions.
- **MCP-38 threat taxonomy** (arXiv 2603.18063). 38 MCP threat categories; source for the tool-description-poisoning discussion in Chapters 1 and 13.
- **OWASP Top 10 for LLM Applications** and **MITRE ATLAS.** The testing vocabularies.

## Cost, evaluation and value

- **FinOps Foundation AI Working Group.** Standardising AI cost discipline; three deployment archetypes with different activation-vs-marginal cost trade-offs.
- **McKinsey / Pay-i (David Tepper).** The deployment break-even formula and the workflow/pipeline/true-agent taxonomy. Read with the caveat that the source sells a solution to the problem it describes.
- **McKinsey — "Where AI will create value—and where it won't."** Three waves by durability: productivity < differentiation < transaction-cost collapse.
- **McKinsey — "Frontiers of Compute."** Energy-per-token as a currency parallel to cost-per-token.
- **Aider polyglot benchmark.** The source for cost-per-*solved*-task diverging from cost-per-task by roughly an order of magnitude.
- **EY — agentic AI enterprise token cost.** The cheaper-tokens-pricier-tasks paradox, concretely.
- **Crusoe / NVIDIA — "Tokenomics in the Age of Agentic Inference."** Supply-side decomposition; goodput vs throughput. Vendor content — treat as corroboration of mechanism, not independent evidence.

## Memory

- **Letta (formerly MemGPT).** LLM-as-OS: virtual-memory hierarchy with the agent paging information in and out via memory tools.
- **Mem0.** Passive extraction over hybrid vector + graph + KV; their ECAI 2025 paper reports latency and token-cost reductions versus full-context on LOCOMO.
- **Zep / Graphiti.** Temporal knowledge graph maintaining validity periods — the supersession problem plain vector stores can't represent.

## Runtime controls and regulated deployment

- **Uchit Vyas — [hellouchit.com](https://hellouchit.com/).** The most developed public treatment of agentic architecture for regulated environments: a layered reference architecture, a build-ordered control set for agents, and a named anti-pattern catalogue. Primary source for much of [Chapter 14](14-runtime-controls.md) — graded autonomy, the chokepoint principle, and the run-record-as-audit-pack idea are his framings, restated here because they generalise beyond the regulated context. Read the original.
- **Cloud Security Alliance** agent identity survey (2026) and related industry surveys — the workload-identity and kill-switch readiness figures cited in Chapters 10 and 13.
- **NIST NCCoE** concept paper applying OAuth 2.0, Zero Trust (SP 800-207) and Digital Identity Guidelines to agent scenarios.

## Observability

- **OpenTelemetry GenAI semantic conventions** and **W3C PROV-DM.** Both are a *floor* rather than a ceiling for agent runs — retrieved passages, tool-call rationales, memory items and inter-agent messages fall through both traditions, so budget for a semantic layer on top.

## Australian regulatory sources

- **DISR — Guidance for AI Adoption** (2025), superseding the Voluntary AI Safety Standard
- **Protective Security Policy Framework (PSPF)** and **ASD Information Security Manual (ISM)**
- **ASD — "Engaging with Artificial Intelligence"** and the AI Data Security information sheet
- **OAIC** guidance on APP 1.7–1.9 (automated decision-making disclosure, effective 10 December 2026)
- **Security of Critical Infrastructure Act (SOCI)** and the **Cyber Security Act 2025**

---

*If you spot an error or a missing attribution, open an issue on the repo — corrections are welcome and get credited.*
