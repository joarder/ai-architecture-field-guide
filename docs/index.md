# The AI Architecture Field Guide

*A practitioner's reference for architecting, governing, and costing agentic AI systems — from protocol to production.*

---

Most AI content sits at one of two extremes: hype-driven trend pieces, or vendor documentation too narrow to reason from. This guide sits in between. It's a working reference, built one topic at a time, for people who have to make defensible architecture and investment decisions about agentic AI — not just talk about it.

It's organized around one governing idea: **the unit of account is the verified outcome, not the token.** Every chapter below feeds that instrument — cost, quality, governance, and protocol choice are all levers on the same equation.

## How this guide is structured

The chapters follow the shape of a real system, bottom to top:

| Section | What it covers | Why it's separate |
|---|---|---|
| **Connectivity** | How agents reach tools (MCP) and each other (A2A) | The plumbing — largely settled as of 2026, worth knowing precisely |
| **Cognition** | Orchestration, context, memory, RAG | Where most of the *design* decisions live |
| **Quality & Economics** | Evals, model-selection economics, inference cost | Where "it works" becomes "it's worth what it costs" |
| **Reliability & Security** | How agents fail, and how they're attacked | Both are orthogonal to the stack — they cut across every layer |
| **Governance** | Runtime controls, regulatory and organisational reality | Where the majority of agent pilots die before reaching production |
| **Putting It Together** | Build order, the cost instrument, and a tool to apply it | Synthesis — turning the above into a decision you can defend |

Two structural commitments run through the whole guide, and they're visible in the [reference architecture](02-orchestration.md):

- **Governance sits in the request path, not beside it.** A control that can be bypassed isn't a control — so the architecture is drawn with a single execution chokepoint rather than a governance plane floating alongside the stack.
- **The process clock and the run clock are separate.** A business process lives for months; an agent run lives for seconds. Collapsing them turns "what's still outstanding?" into something you remember rather than something you query.

## Who this is for

Architects, technical leaders, and anyone who needs to walk into a room — a vendor briefing, a board update, a design review — and reason precisely about what an agentic AI system will actually cost, where it will actually break, and what "done well" looks like.

## Using the Workload Analyzer

The [interactive tool](tool/index.md) takes a real workload's characteristics — data sensitivity, task shape, volume, latency, jurisdiction — and returns a first-pass architecture recommendation across every layer in this guide: protocol choice, hosting tier, model-selection lever, and the governance flags that apply. It's a starting hypothesis to pressure-test, not a substitute for the judgment the rest of this guide is here to build.

---

*This is a living document. Chapters are added and revised as the field moves — that's the point of publishing it this way rather than as a static report.*

**Licence.** The written content is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse it, including commercially, with attribution. The reference implementation and the analyzer tool are MIT. Where a framing here is distinctly another author's, it's credited in the chapter and in [References](references.md).

*— Joarder Kamal, PhD*
