# Agent Reliability & Failure Modes

Chapter 2 covered how orchestration is *supposed* to work. This chapter covers how it actually fails — and the failure literature is now good enough to design against, rather than something you learn only by getting paged.

## First, most "agents" aren't agents

A useful three-tier taxonomy, because cost boundedness and evaluation method break differently at each tier:

| Tier | What it is | Cost behaviour |
|---|---|---|
| **Workflow** | Fixed sequence of LLM calls, deterministic control flow | Bounded and predictable |
| **Pipeline** | Branching logic, some model-driven routing, but a finite decision space | Bounded within a known range |
| **True agent** | Model decides its own next step, loop continues until a stop condition | Unbounded until you bound it |

Most systems sold as agents are pipelines. This matters because a pipeline's cost can be estimated up front and a true agent's cannot — retries, fan-out and growing context mean a single task can cost a large multiple of its estimate. Naming which tier you're actually building is the first honest step in any cost or reliability conversation.

## MAST — the failure taxonomy

The most useful empirical work here is *Why Do Multi-Agent LLM Systems Fail?* (Cemri et al., UC Berkeley), which annotated 1,600+ execution traces across seven frameworks and derived 14 failure modes in three clusters:

| Cluster | Share | Representative modes |
|---|---|---|
| **Specification issues** | ~42% | Task ambiguity, unclear role definition, missing termination conditions |
| **Inter-agent misalignment** | ~37% | Loss of conversation history, state desynchronisation, agents talking past each other |
| **Task verification** | ~21% | No verification step, premature termination, accepting an unverified result |

The paper's own conclusion is the part worth carrying: **better base models will not fix the full taxonomy.** These are architectural failures, not capability failures — an agent with no termination condition doesn't acquire one by upgrading the model underneath it.

Three specific modes worth designing against explicitly, because they're the ones that recur:

- **Step repetition** — the agent redoes work it already completed
- **Unaware of termination conditions** — the loop doesn't know when it's done
- **Loss of conversation history** — context dropped mid-task, usually by bad compaction

Note that the last two are *compaction* failures, which connects reliability directly to the cost discussion in [Context, Memory & RAG](03-context-memory-rag.md): bad compaction costs you money **and** causes the incident. The cheapest context strategy and the most reliable one are not in tension.

## The multi-agent argument, and how it resolves

There was a genuine public disagreement in 2025 that's worth knowing because it produced a better answer than either side started with:

- **Cognition** argued against multi-agent designs — sub-agents making implicit decisions about style and edge cases produce incoherent output, and context fragments across agents that should have shared it. Their prescription: single-threaded agents with hierarchical context compression.
- **Anthropic** published on a successfully deployed multi-agent research system in the same period, with an apparently opposite conclusion.

**The reconciliation (LangChain's framing) is the thing to internalise: multi-agent works for read-heavy tasks and breaks down on write-heavy ones.** Research fans out cleanly over reading — many parallel agents gathering, one synthesising. Coding requires coherent writing, so it doesn't parallelise without producing conflicting edits.

This is a sharper version of the "L4 is optional" rule from Chapter 2. The question isn't "is my task complex enough for multi-agent" — it's **"is my task read-heavy or write-heavy?"** Complexity alone is not the trigger; parallelisable reading is.

## Two failure classes, two different defences

A distinction that keeps teams from thinking they're covered when they're half-covered:

- **Design-time classification** (MAST) tells you *what to look for* — which failures are even possible in the shape you've built
- **Runtime enforcement** (see [Runtime Control Patterns](14-runtime-controls.md)) bounds *what it costs you* when one happens

They're complementary layers, not competing frameworks. Most teams have neither; the ones that have one usually believe they have both.

## Reference implementation

The boilerplate's `src/orchestrator.py` demonstrates the minimum viable versions: a bounded task shape (no open-ended loop), explicit intent classification before delegation (guards against specification ambiguity), and a `high_stakes` flag routing to stricter verification (guards against the task-verification cluster). What it deliberately does **not** have — an unbounded reflection loop, cross-agent shared state — is as instructive as what it does.
