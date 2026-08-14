# Agent Orchestration

## Two different axes, easily conflated

- **MCP** — vertical: how one agent talks to tools and data
- **Orchestration / A2A** — horizontal: how agents talk to each other, as peers

MCP doesn't orchestrate. It makes an individual agent capable; orchestration decides which agent does what, when.

## The dominant pattern: hub-and-spoke

Roughly two-thirds of deployed multi-agent systems use orchestrator-worker (hub-and-spoke), not exotic swarm architectures:

- A **lead/orchestrator agent** decomposes a task and routes sub-tasks
- Each **worker agent** has its own scoped MCP connections to the tools it needs
- The orchestrator talks to workers via **A2A** (or a framework like LangGraph/CrewAI) — not MCP, because MCP wasn't built to make an agent look like a peer

A useful simplification: some architectures expose a whole sub-agent as if it were just another MCP tool to the orchestrator, flattening "call a database" and "delegate to a specialist" into the same interface.

## Reference architecture (vendor-agnostic layering)

```
L0 Interaction    — chat UI / IDE / voice / API caller
L1 Host/Runtime   — session, context window, conversation state
L2 Reasoning      — planning, decomposition (ReAct, Plan-Execute-Verify)
L3 Model          — fully interchangeable (Claude / GPT / Gemini / local)
L4 Orchestration  — multi-agent coordination (OPTIONAL — see below)
L5 Tool Protocol  — MCP: discover & invoke capabilities
L6 Capability     — individual MCP servers; auth, schema, rate limits
L7 System of Record — the actual APIs / databases / SaaS platforms
Governance plane  — cross-cutting: identity, audit, cost metering, evals, kill switches
```

Every horizontal boundary is a **contract, not a product**. L2↔L3 is "prompt in, completion out" — swap models freely. L4↔L5 is "discover and call a capability" — the MCP contract, protocol-agnostic in principle. The only layers where real vendor lock-in tends to hide are L1 (host) and L4 (orchestration framework) — L3 and L5 are comparatively open.

## L4 is optional — and premature orchestration is a real failure mode

Most production systems today are a single agent doing L1→L2→L3→L5→L6→L7 directly. Add L4 only when one agent's job genuinely splits into distinct specialist roles with separate tool access. Only ~28% of enterprises attempting multi-agent deployments hit sustained production success — the failures are usually coordination problems (two agents booking the same resource) and governance gaps (no cost tracking per agent, no kill switch), not model-capability problems.

## Reference implementation

From `src/orchestrator.py` in the companion repo. The orchestrator classifies intent, then either handles it directly (no L4 needed) or delegates over A2A to a scoped specialist worker:

```python
def handle_ticket(ticket_id, customer_id, ticket_text, memory, ledger):
    intent = classify_intent(ticket_text)

    if intent == "billing":
        # Delegate — this agent never touches the billing tool itself
        assert orchestrator_identity.can_delegate_to("billing-worker")
        envelope = AgentEnvelope(
            from_agent="orchestrator", to_agent="billing-worker",
            goal=ticket_text, payload={"customer_id": customer_id},
        )
        result = registry.send(envelope)                 # A2A hop
    else:
        # Handle directly: RAG + cascade, no delegation needed
        context_chunks = rag_search(ticket_text)
        response_text, call_record = cascade_call(prompt)
    ...
```

Notice `intent == "faq"` never touches L4 at all — it's the single-agent path from the [reference architecture](#reference-architecture-vendor-agnostic-layering) above. Only the billing path exercises orchestration, which is the point: **add L4 only where the task shape actually requires a peer handoff.**

## Framework-agnostic doesn't mean build-your-own

At L4, being framework-agnostic means defining the *delegation contract* (what's handed off, what comes back, how failure/retry is handled) independent of any specific framework's API — then picking whichever framework implements that contract with the least custom code, and treating it as replaceable. Migrating off an orchestration framework is closer to refactoring internal code than renegotiating a vendor relationship — lower-stakes than L1 or L3 lock-in.
