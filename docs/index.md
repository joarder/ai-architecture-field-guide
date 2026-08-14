# The AI Architecture Field Guide

*A practitioner's reference for architecting, governing, and costing agentic AI systems — from protocol to production.*

---

Most AI content sits at one of two extremes: hype-driven trend pieces, or vendor documentation too narrow to reason from. This guide sits in between. It's a working reference, built one topic at a time, for people who have to make defensible architecture and investment decisions about agentic AI — not just talk about it.

It's organized around one governing idea: **the unit of account is the verified outcome, not the token.** Every chapter below feeds that instrument — cost, quality, governance, and protocol choice are all levers on the same equation.

## The stack at a glance

Click any block to jump to the chapter that covers it.

<div class="stack-map" markdown="0">

  <div class="tier">
    <span class="tier-label">Process tier <span>— lives for days, weeks, months</span></span>
    <a class="blk" href="02-orchestration/#reference-architecture-vendor-agnostic-layering">
      <span class="id">PROC</span>Declarative graph · append-only event log · reconciler
      <span class="note">Holds rows, not running processes — so coverage is computed, not remembered</span>
    </a>
  </div>

  <div class="flow">&#9662;&nbsp; dispatches one step</div>

  <div class="tier">
    <span class="tier-label">Run tier <span>— lives for seconds</span></span>

    <a class="blk" href="02-orchestration/">
      <span class="id">L0</span>Interaction
      <span class="note">Chat UI · IDE · voice · API caller</span>
    </a>
    <a class="blk" href="03-context-memory-rag/">
      <span class="id">L1</span>Host / Runtime
      <span class="note">Session, context window, conversation state</span>
    </a>

    <div class="chokepoint">
      <a class="chokepoint-hd" href="14-runtime-controls/" style="text-decoration:none">&#9670; The chokepoint — one path, no bypass</a>
      <div class="chokepoint-seq">resolve &rarr; authorize &rarr; precondition &rarr; budget &rarr; assemble &rarr; render &rarr; generate &rarr; validate &rarr; persist &rarr; gate &rarr; emit</div>

      <a class="blk" href="02-orchestration/">
        <span class="id">L2</span>Reasoning
        <span class="note">Planning, decomposition</span>
      </a>
      <a class="blk" href="05-model-economics/">
        <span class="id">L3</span>Model
        <span class="note">Interchangeable — prompt in, completion out</span>
      </a>
      <a class="blk" href="12-agent-reliability/">
        <span class="id">L4</span>Orchestration <em>(optional)</em>
        <span class="note">Multi-agent coordination — add only for read-heavy work</span>
      </a>
      <a class="blk" href="01-mcp/">
        <span class="id">L5</span>Tool Protocol — MCP
        <span class="note">Discover and invoke capabilities</span>
      </a>
    </div>

    <a class="blk" href="01-mcp/">
      <span class="id">L6</span>Capability Servers
      <span class="note">Auth, schema validation, rate limits</span>
    </a>
    <a class="blk" href="09-production-tech/">
      <span class="id">L7</span>System of Record
      <span class="note">Your actual APIs, databases, SaaS platforms</span>
    </a>
  </div>

  <div class="flow">&#9662;&nbsp; emits</div>

  <div class="tier">
    <span class="tier-label">Run record</span>
    <a class="blk" href="14-runtime-controls/#the-run-record">
      <span class="id">REC</span>Audit pack <em>and</em> training signal — the same rows
      <span class="note">Assembled context + hash · retrieved IDs · policy decisions · prompt version · tokens · cost · groundedness</span>
    </a>
  </div>

  <div class="rail">
    <a href="04-evals-observability/">Evals &amp; Observability</a>
    <a href="13-agent-security/">Security</a>
    <a href="11-cost-per-outcome-instrument/">Cost per Verified Outcome</a>
    <a href="10-enterprise-governance/">Identity &amp; Governance</a>
    <a href="15-build-order/">Build Order</a>
  </div>

  <div class="hint">Cross-cutting concerns above touch every layer.</div>

</div>

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
