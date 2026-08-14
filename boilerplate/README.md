# Support Copilot — Boilerplate Reference Implementation

A runnable, minimal implementation of every pattern in *The AI Architecture
Field Guide*, threaded through one simple use case: a support-ticket
copilot that answers FAQ questions via RAG and routes billing questions to
a specialist agent.

**Zero API keys required.** LLM calls are mocked (clearly marked, one
function each) so you can read and run the architecture without spending
money or needing credentials. Swap in a real API in `model_router.py`'s
`call_llm()` when you're ready.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate   # optional
python main.py
```

No dependencies beyond the Python 3.10+ standard library.

## What each file demonstrates

| File | Guide chapter | What it shows |
|---|---|---|
| `src/mcp_tools.py` | 1 — MCP | Tool server/client: discover, then invoke by name |
| `src/orchestrator.py` | 2 — Orchestration | Hub-and-spoke: direct handling vs. delegation |
| `src/rag.py` | 3 — Context/Memory/RAG | Just-in-time retrieval; working vs. semantic memory |
| `src/evals.py` | 4 — Evals | Three-tier cascade: deterministic → lightweight → full judge |
| `src/model_router.py` | 5, 6 — Model economics, Inference economics | Prompt/RAG/fine-tune/distill lever; model cascade for cost |
| `src/a2a_protocol.py` | 7 — Protocols | Agent-to-agent task delegation, A2A-shaped |
| `src/governance.py` | 10 — Enterprise governance | Scoped, time-bound agent identity; audit log; enforced denial |
| `src/cost_per_outcome.py` | 11 — The Instrument | Cost tagged to verified outcome, not just token count |
| `main.py` | — | Wires all of the above together on 5 sample tickets |

## Read order

Read each chapter in the field guide first — the "Reference implementation"
section at the end of each links straight to the matching file above. Then
run `main.py` and trace one ticket end to end through the files it touches.

## Extending it

- Add a second worker (e.g. a "technical support" specialist) to see a
  genuine three-way hub-and-spoke, not just orchestrator + one worker.
- Replace `rag.py`'s keyword search with real embeddings.
- Replace `model_router.py`'s `call_llm()` with a real Anthropic/OpenAI call.
- Add a second AgentIdentity scope test to `governance.py` to see the
  audit log capture both an approval and a denial for the same agent.

## Licence

MIT — see `LICENSE-CODE` in the repository root. The written guide this accompanies is CC BY 4.0.
