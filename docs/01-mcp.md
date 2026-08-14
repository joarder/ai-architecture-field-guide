# Model Context Protocol (MCP)

## The core idea

Before MCP, every AI application needed a bespoke integration for every tool or data source — an N×M problem (N models × M tools). MCP standardizes the middle layer: a **host** (the AI app) talks to **servers** (each exposing one system's capabilities) through a **client**, using three primitives:

- **Tools** — actions the model can invoke
- **Resources** — data the model can read
- **Prompts** — reusable templates a server can expose

This turns N×M integrations into N+M: build one MCP server per system, and any compliant model can use it.

## Not a replacement for REST/GraphQL — a layer above them

REST and GraphQL standardize *client-to-service* communication. MCP standardizes *model-to-tool* discovery and invocation. An MCP server is usually a thin wrapper around a REST or GraphQL API, not a replacement for it. The closest prior art is the OpenAPI/plugin pattern from early ChatGPT plugins — MCP is that idea matured into a governed protocol with standardized discovery and transport.

**OpenAPI's role going forward:** it remains the system of record for the API contract. The emerging best practice is "OpenAPI in, MCP out" — generate the MCP layer from the OpenAPI spec rather than hand-maintaining both. The catch: naive generation captures *structure* but not *intent* — a median of only ~19% of an underlying API's operations get exposed usefully without semantic enrichment of the spec.

## Where it stands (mid-2026)

- Donated to the Linux Foundation's Agentic AI Foundation (Dec 2025) — multi-vendor governance
- 18,000+ community-indexed servers; tens of millions of monthly SDK downloads
- A stateless-transport rework ships July 28, 2026 — servers no longer need session affinity, so they scale behind plain load balancers
- Effectively won its layer — no longer a bet, a foundation

## Known limitations

- **Semantic gap**: auto-generated tools often lack the intent context a model needs to choose correctly
- **Context window tax**: every connected server's tool schemas load into context whether used or not
- **Tool poisoning**: malicious instructions hidden in tool *descriptions* — text the agent reads that a human reviewer never sees. Disclosed as a systemic SDK-level issue in May 2026
- **Credential aggregation risk**: a compromised MCP server can be a single point of failure for every backend it touches
- **Governance lag**: NIST's AI Agent Standards Initiative only launched Feb 2026; no mature interoperability profile until Q4 2026 at earliest

## Reference implementation

From the [`boilerplate/`](https://github.com/joarder/ai-architecture-field-guide/tree/main/boilerplate) directory in this repo — `src/mcp_tools.py`. A `ToolServer` owns capabilities and exposes them by schema; a `ToolClient` discovers what's available and invokes by name, never hardcoding which backend it's calling:

```python
class ToolServer:
    """The MCP 'server' role: owns capabilities, exposes them by schema."""
    def register(self, name, description, schema):
        def decorator(fn):
            self._tools[name] = Tool(name, description, schema, fn)
            return fn
        return decorator

    def list_tools(self):
        return [{"name": t.name, "description": t.description, "schema": t.schema}
                for t in self._tools.values()]

    def call(self, name, **kwargs):
        return self._tools[name].fn(**kwargs)


@ticketing_server.register(
    "lookup_billing_account",
    "Look up a customer's billing account status by customer_id",
    {"customer_id": "string"},
)
def lookup_billing_account(customer_id: str) -> dict:
    # Stand-in for a real REST call — this is the "MCP wraps a REST API" pattern.
    ...
```

The client side never touches `lookup_billing_account` directly — it discovers, then invokes by name:

```python
client = ToolClient(ticketing_server)
tools = client.discover()                       # runtime discovery, not hardcoded imports
client.invoke("lookup_billing_account", customer_id="CUST-002")
```

**Swap-in point**: replace `ToolServer`/`ToolClient` with the official `mcp` Python SDK's `Server`/`Client` classes when moving off the illustrative version — the discover→invoke contract maps directly onto the real transport.

## The takeaway

MCP solves the integration-format problem well. It has not yet solved governance, security, or cost-at-scale — those remain live objections in any serious architecture or procurement conversation.
