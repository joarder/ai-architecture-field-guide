"""
Chapter 11 — The Instrument: Cost-per-Verified-Outcome
==========================================================
The capstone: tag every call with BOTH cost and eval verdict, then compute
the one number that actually matters — not tokens spent, not calls made,
but cost per outcome that passed verification. This is what makes
"productive vs wasteful" a computable classification instead of a guess.
"""
from dataclasses import dataclass, field


@dataclass
class OutcomeRecord:
    task_id: str
    cost_usd: float
    verified: bool
    escalated: bool


class CostPerOutcomeLedger:
    def __init__(self):
        self.records: list[OutcomeRecord] = []

    def log(self, task_id: str, cost_usd: float, verified: bool, escalated: bool = False):
        self.records.append(OutcomeRecord(task_id, cost_usd, verified, escalated))

    def summary(self) -> dict:
        total_cost = sum(r.cost_usd for r in self.records)
        verified_records = [r for r in self.records if r.verified]
        verified_cost = sum(r.cost_usd for r in verified_records)
        wasted_cost = total_cost - verified_cost

        n = len(self.records)
        n_verified = len(verified_records)

        cost_per_verified_outcome = (
            verified_cost / n_verified if n_verified else float("inf")
        )

        return {
            "total_calls": n,
            "verified_outcomes": n_verified,
            "verification_rate": round(n_verified / n, 3) if n else 0,
            "total_cost_usd": round(total_cost, 5),
            "wasted_cost_usd": round(wasted_cost, 5),
            "cost_per_verified_outcome_usd": round(cost_per_verified_outcome, 5),
            "escalation_rate": round(
                sum(1 for r in self.records if r.escalated) / n, 3
            ) if n else 0,
        }

    def report(self):
        s = self.summary()
        print("\n--- Cost-per-Verified-Outcome Report -----------------------")
        for k, v in s.items():
            print(f"  {k:28s}: {v}")
        print("--------------------------------------------------------------")
        print("  This is the number a CFO conversation should be anchored to —")
        print("  not total spend, not call volume, but cost per outcome that")
        print("  actually passed verification.")
