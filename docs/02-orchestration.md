# Coordinating the Work

## When one agent stops being enough

Our support assistant can now reach the billing system. So we keep going.

Shipping status gets added. Then subscription changes, then the refund tool, then a way to look up past tickets from the same customer, then order history. Each one takes an afternoon and each one is obviously useful. Within a month the assistant has around forty tools.

And it gets *worse*, not better.

Tickets that used to work now sometimes fail. The assistant calls `lookup_order_history` when it should have called `lookup_billing_account` — reasonable-looking mistake, wrong answer. Every question now carries forty tool descriptions in its context, so the cheap ones cost more than they used to. And the system prompt has grown into a wall of rules: *if the customer mentions a refund, first check the purchase date, unless they're on an annual plan, in which case…*

Someone in the team review says the obvious thing: **"why don't we split it into specialist agents?"** A billing agent. A shipping agent. A refunds agent. Each one focused, each with a handful of tools.

It sounds right. Often it is right. But it's worth knowing exactly what you're trading before you do it, because this is the decision that determines whether the system reaches production — and the evidence suggests most teams get it wrong in the same direction.

## First, what an agent actually is

Worth pinning down, because "agent" is used for wildly different things.

An agent is a **loop**. The model receives a task, decides on an action, something executes that action, the result comes back, and the model decides again — until it concludes it's done.

That's it. The loop is the whole idea. Ordinary software follows a path someone wrote in advance; an agent decides its own next step each time round.

This matters because it explains where the difficulty comes from. A system that decides its own next step can also decide *not to stop*, decide to repeat work it already did, or decide on something nobody anticipated. Every control in this guide exists because of the loop.

It also gives us a useful three-way distinction, and it's worth being honest about which one you're building:

| | What it is | What it costs |
|---|---|---|
| **Workflow** | Fixed sequence of model calls. The path is written in advance. | Predictable — you can estimate it before you run it |
| **Pipeline** | Branching logic, some model-driven routing, finite decision space | Bounded within a known range |
| **True agent** | The model chooses its next step; loops until a stop condition | **Unbounded until you bound it** |

Most things sold as agents are pipelines. That's not a criticism — pipelines are often the correct choice, and their costs are knowable in advance, which is worth a great deal. But calling a pipeline an agent, or building a true agent when a pipeline would do, is how teams end up surprised by their bill.

!!! note "The honest default"
    If your task has a knowable sequence of steps, write a workflow. You get determinism, testability, and a cost you can quote. Reach for a true agent when the sequence genuinely can't be known in advance — not because agents are the interesting thing to build.

## The single-agent-first rule

Back to the forty tools.

The instinct to split into specialists is sound, but the timing usually isn't. Only around **28% of enterprises attempting multi-agent deployments reach sustained production success** — and when the failures are examined, they're rarely model-capability problems. They're coordination problems: two agents acting on the same resource, one agent overwriting work another was mid-way through, context lost in a handoff so the second agent doesn't know what the first established.

Those are problems you did not have before you split. You created them, in exchange for solving a tool-selection problem.

So the rule is: **one agent until it demonstrably can't cope.** Not until it feels crowded — until you have evidence, ideally from an eval set, that it's choosing wrong in ways a narrower scope would fix.

And before splitting, try the cheaper fixes first:

- **Load tools on demand** rather than all forty upfront. Most of the context cost and a fair share of the confusion goes away. ([Context, Memory & RAG](03-context-memory-rag.md) covers this.)
- **Write better tool descriptions.** As Chapter 1 argued, `lookup_billing_account` beats `lookup` — and a model choosing among forty options needs intent, not just structure.
- **Move rules out of the prompt** into code. If the refund logic is deterministic, it doesn't belong in a paragraph of instructions the model has to reason about.

## The real question: is the work read-heavy or write-heavy?

When you do split, there's a sharper test than "is this complex enough," and it comes out of a genuinely useful public disagreement.

In 2025 two well-argued positions landed close together. **Cognition** published a case *against* multi-agent designs: sub-agents make implicit decisions about style and edge cases that don't reconcile, and context fragments across agents that needed to share it. **Anthropic** published, at almost the same time, an account of a multi-agent research system working well in production.

Both were right, which is what makes the reconciliation valuable. **LangChain's framing:** multi-agent works for **read-heavy** tasks and breaks down on **write-heavy** ones.

Research fans out cleanly over reading — ten agents can each read a different source and one can synthesise, and nothing conflicts, because reading doesn't change anything. Coding doesn't parallelise the same way, because two agents editing the same codebase produce incompatible edits, and merging them is a harder problem than the one you were solving.

For our support assistant, that's clarifying. Reading a customer's billing status, shipping status, and ticket history are three independent lookups — genuinely parallel, no conflict. Issuing a refund and updating the subscription are writes, and if two agents both decide a refund is warranted, you've refunded twice.

**So: fan out on the reads, keep the writes on one path.** That single rule prevents a large fraction of the coordination failures above.

## The shape that actually gets deployed

When you do need coordination, roughly two-thirds of production multi-agent systems use one shape: **hub-and-spoke**, also called orchestrator-worker.

One **orchestrator** receives the task, decides which specialist should handle what, and routes. Each **worker** is narrow, has only the tools it needs, and returns a result. Workers don't talk to each other.

The academic literature is full of more interesting topologies — swarms, negotiating peers, emergent coordination. They're not what ships. Hub-and-spoke wins because it has one place where decisions are made, which means one place to look when something goes wrong.

For our assistant: an orchestrator classifies the incoming ticket, and either answers directly from the FAQ or hands the ticket to a billing specialist that has the billing tools and nothing else.

```python
def handle_ticket(ticket_id, customer_id, ticket_text, memory, ledger):
    intent = classify_intent(ticket_text)

    if intent == "billing":
        # Delegate — this agent never touches the billing tools itself
        envelope = AgentEnvelope(
            from_agent="orchestrator", to_agent="billing-worker",
            goal=ticket_text, payload={"customer_id": customer_id},
        )
        result = registry.send(envelope)
    else:
        # Handle directly — no delegation needed
        context_chunks = rag_search(ticket_text)
        response_text, call_record = cascade_call(prompt)
```

Notice the `else` branch. FAQ tickets never touch the orchestration machinery at all — they're a single agent doing a single job. **The multi-agent path is the exception, not the default**, even in a system that has one.

## Two protocols, two directions

There's a vocabulary point here that causes real confusion, and it's simpler than it sounds.

- **MCP** connects an agent **downward** to tools and data. Vertical.
- **A2A** connects an agent **sideways** to another agent, as a peer. Horizontal.

They're not competitors. Our billing worker uses MCP to reach the billing system, and the orchestrator uses A2A to hand it the ticket.

Why two protocols rather than one? Because delegating a *goal* is a different act from calling a *function*. A function call has known arguments and a known return shape. A delegation says "handle this" and may come back with partial progress, a request for clarification, or a refusal. MCP wasn't built to make an agent look like a peer.

**A2A** (Google's Agent2Agent) covers that gap. Agents publish "Agent Cards" describing what they can do — the same discover-then-invoke shape as MCP, one level up. It sits on ordinary web standards (HTTP, JSON-RPC, OAuth 2.1) rather than inventing new transport, which is a good sign for longevity.

The landscape has consolidated faster than expected. IBM's competing ACP wound down and folded into A2A, and both MCP and A2A are now governed under the Linux Foundation. **The standing recommendation is uncontroversial: MCP for tools, A2A when you need agents to coordinate across teams or organisations.** Inside one codebase, a function call is usually enough — you don't need a protocol to talk to yourself.

## The architecture, and two arguments inside it

Here's the full picture. Two things in it are arguments rather than conventions, and I'll defend both.

```
╔═══════════════════════════════════════════════════════════════╗
║  PROCESS TIER  — lives for days/weeks/months                  ║
║  Declarative graph of what should happen · append-only event  ║
║  log of what did · reconciler comparing desired vs actual     ║
║  Holds ROWS, not running processes                            ║
╚════════════════════════════╤══════════════════════════════════╝
                             │  dispatches a single step
╔════════════════════════════▼══════════════════════════════════╗
║  RUN TIER — lives for seconds                                 ║
║                                                               ║
║  L0 Interaction    — chat UI / IDE / voice / API caller       ║
║  L1 Host/Runtime   — session, context window, conv. state     ║
║          │                                                    ║
║  ┌───────▼─────────────────────────────────────────────────┐  ║
║  │ ▓▓ THE CHOKEPOINT ▓▓  one path, no bypass               │  ║
║  │  resolve → authorize → precondition → budget →          │  ║
║  │  assemble context → render → generate → validate →      │  ║
║  │  persist → gate → emit                                  │  ║
║  │                                                          │  ║
║  │   L2 Reasoning   — planning, decomposition               │  ║
║  │   L3 Model       — interchangeable; prompt in, text out  │  ║
║  │   L4 Orchestr.   — multi-agent coordination (OPTIONAL)   │  ║
║  │   L5 Tool Proto  — MCP: discover & invoke capabilities   │  ║
║  └───────┬─────────────────────────────────────────────────┘  ║
║          │                                                    ║
║  L6 Capability     — MCP servers; auth, schema, rate limits   ║
║  L7 System of Record — actual APIs / databases / SaaS         ║
╚════════════════════════════╤══════════════════════════════════╝
                             │  emits
╔════════════════════════════▼══════════════════════════════════╗
║  RUN RECORD — the audit pack and the training signal          ║
║  assembled context + hash · retrieved IDs · upstream run IDs  ║
║  · policy decisions with reasons · prompt version · model ·   ║
║  tokens · cost · latency · groundedness map                   ║
╚═══════════════════════════════════════════════════════════════╝
```

Reading the chokepoint sequence in plain terms: **who is asking** (resolve), **are they permitted to do this** (authorize), **is the system in a state where this makes sense** (precondition), **can we afford it** (budget), **what should the model see** (assemble context), **ask the model** (render, generate), **is the answer well-formed** (validate), **save it** (persist), **does a human need to approve before it takes effect** (gate), and **tell whoever is waiting** (emit).

Not every system needs all eleven. The property that matters is that whichever ones you have, every request passes through them in the same order, with no second route.

!!! note "Attribution"
    The two-clocks separation, the single-chokepoint principle, and the run-record-as-audit-pack idea are drawn from Uchit Vyas's published reference architecture for agentic systems in regulated environments ([hellouchit.com](https://hellouchit.com/)) — the most developed public treatment of this material I've found. They're integrated into the stack here rather than kept as a separate model because they generalise well beyond the regulated context they were written for. The original is worth reading directly.

### Argument one: governance goes in the path, not beside it

Most architecture diagrams draw controls as a layer floating alongside everything else — a box labelled "security and governance" with a bracket spanning the stack.

That box is the one teams defer. Not through carelessness: because nothing *structurally* requires it. The system works without it. It gets scheduled for phase two, and phase two is when the deadline arrives.

Drawing the controls as a single path every request must pass through changes the claim being made. Not *we have controls* — **there is no way around them**. Concretely, that means one function every agent execution enters, and a direct call to a model provider's SDK anywhere else in the codebase treated as a lint failure.

The test is simple: **a control you can bypass by importing the SDK is not a control.**

### Argument two: two clocks, not one

A customer's complaint lives for a week. An agent run lives for four seconds.

If you model only the run, then "which tickets are still unresolved?" becomes something a person tracks in a spreadsheet. Split them, and it becomes a query: the process tier holds durable rows describing what should happen and what did, and a reconciler compares them. Coverage is **computed rather than remembered**.

The run tier then has one job — execute a single step well, with retries, timeouts and fallback — and none of that leaks into your model of the business process.

### Everything else is a contract, not a product

Every horizontal boundary in that diagram is an **interface**, not a vendor choice. L2↔L3 is "send a prompt, get a completion" — swap Claude for GPT for a local model and nothing above it changes. L4↔L5 is "discover and call a capability."

That's what makes this portable. If someone asks whether adopting this locks you into a vendor, the answer is in the diagram: the only layers where lock-in genuinely hides are L1 (your host runtime) and L4 (your orchestration framework). L3 and L5 are protected by convergent APIs and open protocols respectively.

And on L4 specifically: framework-agnostic doesn't mean writing your own. It means defining the *delegation contract* — what gets handed off, what comes back, how failures propagate — before picking a framework, so the framework implements your contract rather than dictating it. Migrating off an orchestration framework later is closer to refactoring internal code than renegotiating a vendor relationship. It's the least dangerous lock-in on the board.

## Back to the support assistant

The assistant now routes: FAQ tickets handled directly, billing tickets delegated to a specialist with scoped tools. There's one execution path, so there's somewhere to put a permission check. There's a process tier that knows which tickets are still open.

What's still missing is significant. The assistant can reach the billing system and decide who handles what — but nothing yet decides *what it should know* when it answers, and nothing checks whether the answer was right.

Those are the next two chapters.

## Summary

- An agent is a loop: decide, act, observe, decide again. Everything hard follows from the loop being able to continue.
- Workflow, pipeline, and true agent are different things with different cost profiles. Most "agents" are pipelines, and that's often correct.
- **Start with one agent.** Only around 28% of multi-agent attempts reach sustained production, and the failures are coordination problems that splitting *created*.
- Before splitting, try on-demand tool loading, better tool descriptions, and moving deterministic rules into code.
- The sharp test for splitting is **read-heavy vs write-heavy**, not complexity. Fan out on reads; keep writes on one path.
- **Hub-and-spoke** is what actually ships — one orchestrator, narrow workers, no worker-to-worker chatter.
- **MCP goes down to tools; A2A goes sideways to agents.** Inside one codebase a function call is usually enough.
- Governance belongs **inside** the execution path, and the process clock belongs **separate** from the run clock.

## Try it

In `boilerplate/`, `src/orchestrator.py` implements the hub-and-spoke split and `src/a2a_protocol.py` the delegation envelope.

1. **Trace one ticket of each kind.** Run `python3 main.py` and follow `T-1001` (FAQ, handled directly) and `T-1002` (billing, delegated). Notice how much less machinery the FAQ path uses.
2. **Add a shipping worker.** Register a third agent and route to it. You'll immediately meet the question this chapter is about: does the orchestrator need to know shipping's tools, or only that shipping exists?
