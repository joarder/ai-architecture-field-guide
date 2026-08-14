# Beyond MCP: A2A and the Protocol Landscape

## The map settled faster than expected

Two protocols matter in mid-2026:

- **MCP** — agent-to-*tool* (vertical). Effectively won its layer: infrastructure, not a bet.
- **A2A** (Google's Agent2Agent) — agent-to-*agent* (horizontal). Donated to the Linux Foundation, 50+ launch partners (AWS, Microsoft, Salesforce, SAP). Uses "Agent Cards" for capability discovery; built on HTTP/SSE/JSON-RPC with OAuth 2.1 for mutual auth — reused web standards rather than new transport.

**Recent consolidation**: IBM's ACP (Agent Communication Protocol), once a third contender, wound down independent development and folded into A2A. The "three competing standards" framing from Q1 2026 has already collapsed to two — unusually fast for a standards fight.

**Adjacent, narrower**: AP2/UCP (Agent Payments/Commerce protocols) — a separate spec for agent-to-agent *transactions*, since paying on another agent's behalf is a distinct trust/authorization problem from generic task delegation.

## The standing recommendation

MCP for all tool access (mature, broadly supported) + A2A when cross-vendor or cross-organization agent coordination is genuinely needed. This validates the L4/L5 split in the [orchestration reference architecture](02-orchestration.md) — it's not a hypothetical layering exercise, it's how the two dominant standards bodies converged on dividing the problem.

## Reference implementation

From `src/a2a_protocol.py` — the same discover-then-invoke shape as MCP, one layer up (agents, not tools). An `AgentCard` is the A2A analogue of MCP's tool schema; an `AgentEnvelope` is a delegated task:

```python
@dataclass
class AgentEnvelope:
    """A task delegated from one agent to another."""
    task_id: str
    from_agent: str
    to_agent: str
    goal: str
    payload: dict

class AgentRegistry:
    def send(self, envelope: AgentEnvelope) -> AgentResult:
        _, handler = self._agents[envelope.to_agent]
        return handler(envelope)
```

In the orchestrator, delegation is a single line — the orchestrator never knows *how* the billing worker does its job, only that it can hand off a goal and get a typed result back:

```python
result = registry.send(envelope)   # the entire A2A hop, from the orchestrator's view
```

**Swap-in point**: replace `AgentRegistry.send()` with the official A2A SDK's client for real cross-process calls between agents running as separate services.

## What's still unsettled

Not the protocol layer — the orchestration *framework* layer (which implementation of A2A you build against) and whether the commerce/payments layer matures before you need it.
