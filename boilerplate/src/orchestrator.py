"""
Chapter 2 — Agent Orchestration
==================================
The hub-and-spoke pattern, made concrete: an ORCHESTRATOR classifies an
incoming ticket and either (a) handles it directly via RAG for FAQ
questions, or (b) delegates to the BILLING WORKER over A2A for account
questions. The worker uses MCP to call the real (mocked) billing backend.

This is the one file where every other chapter's module gets used together —
read it after reading the chapter-specific files, not before.
"""
import sys
sys.path.insert(0, ".")  # allow local imports when run directly

from mcp_tools import ToolClient, ticketing_server
from a2a_protocol import AgentCard, AgentEnvelope, AgentResult, AgentRegistry
from rag import search as rag_search, WorkingMemory
from model_router import cascade_call
from evals import evaluate
from governance import AgentIdentity, AuditLog, enforce
from cost_per_outcome import CostPerOutcomeLedger


# --- Governance: scoped identities for each agent --------------------------
audit = AuditLog()
orchestrator_identity = AgentIdentity(
    "orchestrator", allowed_tools=set(), allowed_agents={"billing-worker"}
)
billing_worker_identity = AgentIdentity(
    "billing-worker", allowed_tools={"lookup_billing_account"}, allowed_agents=set()
)


# --- The billing worker: a specialist agent with its own MCP client -------
mcp_client = ToolClient(ticketing_server)


def billing_worker_handler(envelope: AgentEnvelope) -> AgentResult:
    customer_id = envelope.payload.get("customer_id", "UNKNOWN")

    enforce(billing_worker_identity, "lookup_billing_account", audit)          # Ch10 governance
    account = mcp_client.invoke("lookup_billing_account", customer_id=customer_id)  # Ch1 MCP

    prompt = f"Customer asked: {envelope.goal}\nAccount data: {account}"
    response, call_record = cascade_call(prompt)                              # Ch5/6 routing+cost

    return AgentResult(
        task_id=envelope.task_id,
        from_agent="billing-worker",
        status="completed",
        result={
            "response": response,
            "account": account,
            "cost_usd": call_record.cost_usd,
            "escalated": call_record.escalated,
        },
        cost_tokens=call_record.tokens,
    )


registry = AgentRegistry()
registry.register(
    AgentCard("billing-worker", "Billing Specialist",
              "Handles account/billing status questions", ["billing_lookup"]),
    billing_worker_handler,
)


# --- The orchestrator ------------------------------------------------------
def classify_intent(ticket_text: str) -> str:
    """Deliberately simple keyword classifier — a real system would use the
    reasoning layer (L2) itself, but the point here is the routing decision,
    not the classifier's sophistication."""
    if any(w in ticket_text.lower() for w in ["bill", "invoice", "charge", "account", "dispute"]):
        return "billing"
    return "faq"


def handle_ticket(ticket_id: str, customer_id: str, ticket_text: str,
                   memory: WorkingMemory, ledger: CostPerOutcomeLedger):
    memory.add("customer", ticket_text)
    intent = classify_intent(ticket_text)

    if intent == "billing":
        # Delegate over A2A — this agent doesn't touch the billing tool itself
        assert orchestrator_identity.can_delegate_to("billing-worker")        # Ch10 governance
        envelope = AgentEnvelope(
            from_agent="orchestrator", to_agent="billing-worker",
            goal=ticket_text, payload={"customer_id": customer_id},
        )
        result = registry.send(envelope)                                      # Ch7 A2A
        response_text = result.result["response"]
        cost_usd = result.result["cost_usd"]
        escalated = result.result["escalated"]
    else:
        # Handle directly: RAG + cheap-model cascade, no delegation needed
        context_chunks = rag_search(ticket_text)                              # Ch3 RAG
        prompt = f"Question: {ticket_text}\nContext: {' '.join(context_chunks)}"
        response_text, call_record = cascade_call(prompt)                     # Ch5/6
        cost_usd = call_record.cost_usd
        escalated = call_record.escalated

    memory.add("assistant", response_text)

    high_stakes = (intent == "billing")
    eval_result = evaluate(response_text, ticket_text, high_stakes=high_stakes)  # Ch4 evals
    ledger.log(ticket_id, cost_usd, eval_result.verified, escalated)             # Ch11 instrument

    return {
        "ticket_id": ticket_id,
        "intent": intent,
        "response": response_text,
        "verified": eval_result.verified,
        "eval_reason": eval_result.reason,
        "cost_usd": round(cost_usd, 6),
    }
