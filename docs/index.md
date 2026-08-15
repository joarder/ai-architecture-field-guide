# The AI Architecture Field Guide

*Designing, governing, and costing agentic AI systems — from first principles.*

---

## Start with a familiar failure

A team builds an AI assistant. It demos beautifully. Everyone in the room agrees it should go into production.

Six months later it is still not in production, and nobody can quite explain why. The demo still works. But somewhere between "it works" and "we can run this," a set of questions appeared that nobody had answers for. What does it cost per use — not per million tokens, but per actual customer question answered correctly? How do we know it answered correctly? What happens when it doesn't? Who decided software is allowed to touch a customer's account, and where is that written down? When it does something wrong at 2am, can we reconstruct what it saw and why it chose that?

This is the normal outcome, not the unlucky one. Industry surveys through 2026 consistently find that the large majority of agent pilots never reach production, and Gartner projects that a substantial share of agentic projects will be cancelled outright by 2027. The failures are rarely about model capability. The models are good. The failures are architectural: the system was built to demonstrate a capability, not to be operated.

This guide is about the difference.

## The three facts everything follows from

There is one idea underneath every chapter here, and it is worth stating plainly before anything else.

**Almost everything in agentic AI architecture is a compensation for three properties of language models.**

Not a feature. A compensation — engineering added to work around something the model fundamentally cannot do.

**One: the model is stateless.** Every call starts from nothing. The model has no memory of the previous message, the previous session, or the customer's history. It knows only what you put in front of it, this instant. Everything you want it to "know" must be assembled and sent, every single time.

*Consequence:* you need a discipline for deciding **what** to assemble. That discipline is context engineering, and memory and retrieval are its machinery.

**Two: the model is non-deterministic.** The same input can produce different outputs. There is no test that proves it works, only evidence that it usually does. You cannot know an output is correct by inspecting the code that produced it.

*Consequence:* you need a separate mechanism to check the output — evaluation. And because you cannot predict behaviour, you must instead constrain and record it, which is where governance, permissions, and audit trails come from.

**Three: the model is metered.** Every call costs money in proportion to how much text goes in and comes out. Work that would be free in ordinary software has a running meter attached.

*Consequence:* architecture becomes an economic decision. How much context you load, how many times an agent retries, whether a cheaper model could have handled it — these are cost decisions wearing technical clothing.

Everything else in this guide falls out of those three. Protocols like MCP exist because connecting a stateless model to many systems is combinatorially expensive. Multi-agent orchestration exists because context is finite. Run records exist because non-determinism means you cannot reason backwards from code to behaviour.

When something in the field seems arbitrary or faddish, this is the test worth applying: *which of the three is this compensating for?* If the answer is none, it is probably fashion.

## The unit of account

One more idea, which follows from facts two and three together.

If the model is non-deterministic **and** metered, then counting tokens tells you nothing about whether you got value. A thousand tokens spent producing a wrong answer costs exactly what a thousand spent on a right one costs. Spend and value come apart.

So the unit of account in this guide is not the token. It is the **verified outcome** — a result that something checked before you counted it. That single shift reorganises everything downstream: it makes evaluation a prerequisite rather than a nice-to-have, turns model selection into a break-even calculation, and gives you a number you can put in front of a CFO without flinching.

You will see this thread reappear in every chapter. It is the spine.

## Who this is for

This guide is written for people who have to make a decision and defend it:

- **Architects and technical leads** designing an agentic system and choosing where the boundaries go
- **Forward-deployed and delivery engineers** who have to land something real against a date, inside someone else's constraints
- **Engineering and product managers** deciding whether to build, what it will cost, and what could go wrong

You do not need to have built an agent before. You do need to be comfortable with the idea of an API and a database. Where code appears, it is there to make an idea concrete — you can follow every argument without reading it.

The balance is roughly **70% architecture, cost and governance; 30% implementation**. This is a book about decisions, with enough code to keep the decisions honest.

## A note on scope, and on judgment

Agentic architecture is not the right answer to most problems. A great deal of what is currently built as an agent would work better, cheaper, and more reliably as a script with one model call in the middle of it.

The aim here is not to sell you agents. It is to give you the judgment to know when the complexity is earned — and, just as often, when it isn't. Several chapters spend as much time on what to **defer** as on what to build. That is deliberate.

## The example we'll build on

Rather than switching examples each chapter, one scenario runs the whole way through.

**A mid-sized company wants to help its customer support team.** Tickets arrive by email. Some are simple questions whose answers are already written down somewhere — refund windows, how to upgrade a plan. Others need a look at the customer's actual account: why was I charged, what's my balance, is my subscription active. A few are genuinely thorny and a human should handle them.

It is a deliberately ordinary problem. No glamour, no research challenge. But it contains, in miniature, nearly every decision in this guide: what the system needs to know, how it reaches your billing platform, when to hand off, how you check the answer was right, what it costs per resolved ticket, and who is allowed to let software touch a customer's account.

Each chapter develops this scenario a little further. By the end it is a complete system — and there is a **runnable implementation** in this repository under `boilerplate/` that you can execute in one command, with no API keys, to watch the whole thing work.

!!! note "About the numbers in this scenario"
    Where the support example carries figures — ticket volumes, costs — they are illustrative, chosen to make the arithmetic visible. They are not measurements of a real deployment. Figures drawn from published research are cited in [References](references.md); anything I could not verify at source has been left out.

## The map

Here is the whole system, in the order a support ticket travels through it. You don't need to understand it yet — it's here so you have somewhere to come back to. Each chapter fills in one piece.

<div class="stack-map" markdown="0">

  <div class="tier">
    <span class="tier-label">The long game &mdash; a ticket stays open for days or weeks</span>
    <span class="tier-sub">Tracks the customer's whole issue from arrival to resolution.</span>
    <a class="blk" href="02-orchestration/#the-architecture-and-two-arguments-inside-it">
      <span class="ttl">What still needs doing</span><span class="tech">process tier</span>
      <span class="note">A list of steps and a log of what's happened. Because it's stored rather than held in memory, you can <em>ask</em> what's outstanding instead of hoping someone tracked it.</span>
    </a>
  </div>

  <div class="flow">&#9660;&nbsp; sends one step to be worked on</div>

  <div class="tier">
    <span class="tier-label">A single attempt &mdash; a few seconds</span>
    <span class="tier-sub">One step of the ticket, start to finish.</span>

    <a class="blk" href="02-orchestration/">
      <span class="ttl">Where the request arrives</span><span class="tech">L0 &middot; interaction</span>
      <span class="note">An email, a chat message, a form. However the ticket reaches you.</span>
    </a>
    <a class="blk" href="03-context-memory-rag/">
      <span class="ttl">Keeping track of the conversation</span><span class="tech">L1 &middot; host / runtime</span>
      <span class="note">Holds what's been said so far &mdash; and decides how much of it still fits in the model's limited attention.</span>
    </a>

    <div class="chokepoint">
      <a class="chokepoint-hd" href="14-runtime-controls/">&#9670; One way in &mdash; no shortcuts</a>
      <div class="chokepoint-seq">Who's asking? &rarr; Are they allowed? &rarr; What's the budget? &rarr; What should the model see? &rarr; Was the answer valid? &rarr; Write it all down.</div>

      <a class="blk" href="02-orchestration/">
        <span class="ttl">Working out what to do</span><span class="tech">L2 &middot; reasoning</span>
        <span class="note">Is this a policy question or an account question? What's the next step?</span>
      </a>
      <a class="blk" href="05-model-economics/">
        <span class="ttl">The part that actually thinks</span><span class="tech">L3 &middot; the model</span>
        <span class="note">Text goes in, text comes out. Swappable &mdash; nothing above or below needs to know which model this is.</span>
      </a>
      <a class="blk" href="12-agent-reliability/">
        <span class="ttl">Splitting work between specialists <em>(only if needed)</em></span><span class="tech">L4 &middot; orchestration</span>
        <span class="note">A billing specialist, a shipping specialist. Most systems don't need this &mdash; and adding it too early causes more problems than it solves.</span>
      </a>
      <a class="blk" href="01-mcp/">
        <span class="ttl">Asking to use one of your systems</span><span class="tech">L5 &middot; tool protocol (MCP)</span>
        <span class="note">A standard way for the model to find out what it can do, and to request it by name.</span>
      </a>
    </div>

    <a class="blk" href="01-mcp/">
      <span class="ttl">Your systems, safely wrapped</span><span class="tech">L6 &middot; capability servers</span>
      <span class="note">One wrapper per system. This is where credentials live and where "is this allowed?" gets enforced.</span>
    </a>
    <a class="blk" href="09-production-tech/">
      <span class="ttl">Your actual systems</span><span class="tech">L7 &middot; systems of record</span>
      <span class="note">Billing, shipping, the customer database. Unchanged &mdash; the AI wraps these, it doesn't replace them.</span>
    </a>
  </div>

  <div class="flow">&#9660;&nbsp; and afterwards, writes down what happened</div>

  <div class="tier">
    <span class="tier-label">The record of what happened</span>
    <span class="tier-sub">Kept for every single run.</span>
    <a class="blk" href="14-runtime-controls/#the-run-record">
      <span class="ttl">What it saw, chose, cost &mdash; and whether it was right</span><span class="tech">run record</span>
      <span class="note">The same rows answer an auditor's question and tell you how to improve the system. Most teams fund those as two separate projects.</span>
    </a>
  </div>

  <div class="rail">
    <a href="04-evals-observability/">Checking the answer</a>
    <a href="13-agent-security/">Security</a>
    <a href="11-cost-per-outcome-instrument/">What it costs</a>
    <a href="10-enterprise-governance/">Permissions &amp; audit</a>
    <a href="15-build-order/">Where to start</a>
  </div>

  <div class="hint">Click any block to jump to the chapter that covers it. The five above apply at every level, not just one.</div>

</div>

Two things in that picture are arguments rather than conventions, and they're worth noticing early.

**The checks sit in the road, not next to it.** Most diagrams draw security and governance as a box off to the side. That's the box teams postpone, because the system runs fine without it. Drawing it as a gate every request must pass through changes the claim from *we have controls* to *there's no way around them*.

**There are two clocks.** A customer's complaint lives for a week; a single attempt to answer it lives for four seconds. Keeping those separate is what lets you ask "which tickets are still stuck?" as a question, rather than tracking it in someone's head.

## How to read this

If you are new to the material, read straight through. The chapters escalate deliberately.

If you already build these systems and want the sharp end: [Agent Reliability](12-agent-reliability.md) for how they fail, [Agent Security](13-agent-security.md) for how they're attacked, and [Cost per Verified Outcome](11-cost-per-outcome-instrument.md) for the economics.

If you are about to start building and want the short version: [Build Order](15-build-order.md) says what to do first and — equally important — what to leave until later on purpose.

If you want to reason about a specific workload right now, the [Workload Analyzer](tool/index.md) gives you a first-pass architecture to pressure-test against the rest of the guide.

---

*This is a living document. Chapters are added and revised as the field moves — that's the point of publishing it this way rather than as a static report.*

**Licence.** The written content is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse it, including commercially, with attribution. The reference implementation and the analyzer tool are MIT. Where a framing here is distinctly another author's, it's credited in the chapter and in [References](references.md).
