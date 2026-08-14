"""
Chapter 10 — Enterprise & Principal-Architect Governance
===========================================================
A minimal agent-identity model: every agent gets a scoped, time-bound
capability set rather than standing access to everything. This is the
code-level answer to "92% of enterprises lack visibility into their AI
identities" — the fix starts with making scope explicit and enforced,
not assumed.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class AgentIdentity:
    agent_id: str
    allowed_tools: set[str]
    allowed_agents: set[str]      # which other agents this one may delegate to
    issued_at: datetime = field(default_factory=datetime.utcnow)
    ttl_minutes: int = 30

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.issued_at + timedelta(minutes=self.ttl_minutes)

    def can_use_tool(self, tool_name: str) -> bool:
        return not self.is_expired() and tool_name in self.allowed_tools

    def can_delegate_to(self, agent_id: str) -> bool:
        return not self.is_expired() and agent_id in self.allowed_agents


class AuditLog:
    """Every tool call and delegation gets logged with the identity that
    made it — the minimum bar for 'could we pass a compliance review focused
    on agent behaviour' (only ~half of enterprises currently could)."""

    def __init__(self):
        self.entries: list[dict] = []

    def record(self, agent_id: str, action: str, detail: dict):
        self.entries.append({
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "action": action,
            "detail": detail,
        })

    def dump(self):
        for e in self.entries:
            print(f"  [{e['timestamp']}] {e['agent_id']} :: {e['action']} :: {e['detail']}")


def enforce(identity: AgentIdentity, tool_name: str, audit: AuditLog) -> bool:
    allowed = identity.can_use_tool(tool_name)
    audit.record(identity.agent_id, "tool_call_attempt",
                 {"tool": tool_name, "allowed": allowed})
    if not allowed:
        raise PermissionError(f"Agent '{identity.agent_id}' is not scoped to use '{tool_name}'")
    return True
