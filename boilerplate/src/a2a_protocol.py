"""
Chapter 7 — A2A-style agent-to-agent messaging
================================================
A2A's real contract uses Agent Cards for capability discovery and JSON-RPC/SSE
for the message exchange. This file keeps the same *shape* — a task handed
from one agent to another, with a typed result handed back — without the
transport, so Chapter 2's orchestrator can delegate to a worker the same way
it would over real A2A.

Swap-in point: replace AgentEnvelope/send() with the official A2A SDK's
client when you're ready for real cross-process agent calls.
"""
from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class AgentCard:
    """What an agent publishes about itself for discovery — A2A's analogue to
    MCP's tool schema, but describing a whole agent's capability, not a function."""
    agent_id: str
    name: str
    description: str
    skills: list[str]


@dataclass
class AgentEnvelope:
    """A task delegated from one agent to another."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    from_agent: str = ""
    to_agent: str = ""
    goal: str = ""
    payload: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    task_id: str
    from_agent: str
    status: str          # "completed" | "failed"
    result: Any
    cost_tokens: int = 0


class AgentRegistry:
    """Where agents publish their AgentCard so an orchestrator can discover
    who's available and route to them — same discover-then-invoke shape as MCP,
    one layer up (agents, not tools)."""

    def __init__(self):
        self._agents: dict[str, tuple[AgentCard, Any]] = {}

    def register(self, card: AgentCard, handler):
        self._agents[card.agent_id] = (card, handler)

    def list_agents(self) -> list[AgentCard]:
        return [card for card, _ in self._agents.values()]

    def send(self, envelope: AgentEnvelope) -> AgentResult:
        if envelope.to_agent not in self._agents:
            return AgentResult(envelope.task_id, envelope.to_agent, "failed",
                                {"error": "agent not found"})
        _, handler = self._agents[envelope.to_agent]
        return handler(envelope)
