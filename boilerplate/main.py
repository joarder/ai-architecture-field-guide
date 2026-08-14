"""
Run this to see the whole guide execute end to end on five sample tickets.

    python main.py

Every chapter's pattern fires at least once: MCP tool calls, A2A delegation,
RAG retrieval, memory, model-cascade routing, tiered evals, governance
enforcement, and the final cost-per-verified-outcome report.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from orchestrator import handle_ticket, audit
from rag import WorkingMemory
from cost_per_outcome import CostPerOutcomeLedger


TICKETS = [
    ("T-1001", "CUST-001", "How do I upgrade my plan?"),
    ("T-1002", "CUST-002", "Why was I charged when my account is past due? I want to dispute this."),
    ("T-1003", "CUST-001", "What's your refund policy?"),
    ("T-1004", "CUST-002", "Can you check my billing account status?"),
    ("T-1005", "CUST-001", "How do I reset my password?"),
]


def main():
    memory = WorkingMemory()
    ledger = CostPerOutcomeLedger()

    print("=== Support Copilot — end-to-end run ===\n")
    for ticket_id, customer_id, text in TICKETS:
        result = handle_ticket(ticket_id, customer_id, text, memory, ledger)
        print(f"[{result['ticket_id']}] intent={result['intent']:<8} "
              f"verified={result['verified']!s:<5} cost=${result['cost_usd']:.6f}")
        print(f"   -> {result['response']}")
        print(f"   -> eval: {result['eval_reason']}\n")

    ledger.report()

    print("\n--- Audit trail (Chapter 10 governance) --------------------")
    audit.dump()

    print("\n--- Governance denial demo (Ch10) ---------------------------")
    from governance import enforce
    try:
        # The orchestrator is NOT scoped to call billing tools directly —
        # only the billing-worker is. This should be denied and logged.
        enforce(orchestrator_identity_for_demo(), "lookup_billing_account", audit)
    except PermissionError as e:
        print(f"  Denied as expected: {e}")


def orchestrator_identity_for_demo():
    from orchestrator import orchestrator_identity
    return orchestrator_identity


if __name__ == "__main__":
    main()
