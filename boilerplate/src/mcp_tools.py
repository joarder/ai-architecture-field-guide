"""
Chapter 1 — MCP (Model Context Protocol)
=========================================
Minimal illustration of MCP's shape: a SERVER exposes TOOLS with a schema;
a CLIENT discovers what's available at runtime and calls them by name.

Real MCP uses JSON-RPC over stdio/HTTP with a proper SDK. This file keeps
the same *shape* (discover -> describe -> invoke) without the transport,
so the architecture is legible without standing up a real server.

Swap-in point: replace ToolServer's registry with `mcp.server.Server` from
the official Python SDK (`pip install mcp`) when you're ready for the real
transport — the discover/invoke contract below maps directly onto it.
"""
from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class Tool:
    name: str
    description: str
    schema: dict          # what arguments this tool expects
    fn: Callable[..., Any]


class ToolServer:
    """The MCP 'server' role: owns capabilities, exposes them by schema."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, schema: dict):
        def decorator(fn):
            self._tools[name] = Tool(name, description, schema, fn)
            return fn
        return decorator

    def list_tools(self) -> list[dict]:
        """What a client sees when it discovers this server — no code, just contracts."""
        return [
            {"name": t.name, "description": t.description, "schema": t.schema}
            for t in self._tools.values()
        ]

    def call(self, name: str, **kwargs) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found on this server")
        return self._tools[name].fn(**kwargs)


# --- A concrete server: the "ticketing system" backend --------------------
ticketing_server = ToolServer()


@ticketing_server.register(
    "lookup_billing_account",
    "Look up a customer's billing account status by customer_id",
    {"customer_id": "string"},
)
def lookup_billing_account(customer_id: str) -> dict:
    # Stand-in for a real REST/GraphQL call to a billing system.
    # This is the "MCP server wraps a REST API" pattern from Chapter 1.
    mock_db = {
        "CUST-001": {"plan": "Pro", "status": "active", "balance_due": 0.0},
        "CUST-002": {"plan": "Starter", "status": "past_due", "balance_due": 49.00},
    }
    return mock_db.get(customer_id, {"error": "customer not found"})


@ticketing_server.register(
    "search_faq",
    "Keyword search over the FAQ knowledge base",
    {"query": "string"},
)
def search_faq(query: str) -> list[str]:
    from rag import search as rag_search   # local import keeps this file standalone-readable
    return rag_search(query)


class ToolClient:
    """The MCP 'client' role: discovers what's available, then invokes by name.
    An orchestrator or worker agent holds one of these — it never hardcodes
    which backend it's calling, only the tool name and arguments."""

    def __init__(self, server: ToolServer):
        self._server = server

    def discover(self) -> list[dict]:
        return self._server.list_tools()

    def invoke(self, name: str, **kwargs):
        return self._server.call(name, **kwargs)


if __name__ == "__main__":
    client = ToolClient(ticketing_server)
    print("Discovered tools:")
    for t in client.discover():
        print(f"  - {t['name']}: {t['description']}")
    print("\nInvoking lookup_billing_account:")
    print(" ", client.invoke("lookup_billing_account", customer_id="CUST-002"))
