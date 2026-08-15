# Connecting a Model to Your Systems

## The glue code problem

Let's start building the support assistant from the introduction.

The first version is easy. A customer asks "what's your refund policy?", you paste your policy document into the prompt alongside the question, and the model answers. No architecture required.

Then a ticket arrives that reads: *"Why was I charged $49 this month? I thought I cancelled."*

Your policy document cannot answer that. Only your billing system knows. And here you meet the first of the three facts head-on: **the model is stateless**. It has no connection to anything. It cannot look, it cannot fetch, it cannot check. It can only respond to text you put in front of it.

So you write some glue. You give the model a description of a function called `lookup_billing_account`, formatted the particular way your model provider expects. When the model decides to call it, your code catches that, calls your real billing API, and feeds the result back. It takes an afternoon. It works.

Now watch what happens over the next quarter.

**Your team wants to try a different model provider** — cheaper, or better at this task, or your procurement team has a preference. The tool description you wrote is in your current provider's format. The new one expects a different shape. You rewrite it.

**Support wants the assistant to check shipping status too.** That's a second system. More glue.

**Another team inside the company** — the one building an internal ops assistant — needs to reach the same billing system. They don't know your glue exists, or it's tangled into your application. They write their own.

**The billing API adds a required field.** Now you find out how many copies of that glue exist, one 500 error at a time.

Nothing here is difficult. That's what makes it dangerous — it's *tedious*, and tedious work quietly multiplies. Four models across five systems is twenty integrations, each written separately, each breaking separately. This is the **N×M problem**: N models times M systems, and the cost of integration grows by multiplication rather than addition.

That is the problem the Model Context Protocol was built to kill.

## What MCP actually is

MCP is an agreement about *how* a model asks to use something.

Instead of every application inventing its own way to describe tools to a model, MCP defines one format. Your billing system gets described once, in that format, and any model or application that speaks MCP can use it — without you writing anything model-specific.

Twenty integrations become nine: five systems described once each, four models that already speak the protocol. N×M becomes **N+M**. That's the whole pitch, and it is the same argument that made SQL, USB, and HTTP worth adopting — not that any one of them was clever, but that everyone agreeing on one boring interface beat everyone optimising their own.

There are three roles:

- A **server** exposes one system's capabilities. You'd write one for billing, one for shipping.
- A **client** is what talks to a server. Your agent holds one.
- A **host** is the application everything runs inside — your support assistant.

And three things a server can offer:

| Primitive | What it is | In our support assistant |
|---|---|---|
| **Tools** | Actions the model can invoke | `lookup_billing_account`, `issue_refund` |
| **Resources** | Data the model can read | The refund policy document, FAQ articles |
| **Prompts** | Reusable templates the server provides | A standard "summarise this ticket" format |

Most of what you'll build is tools. Resources matter more than they first appear — they're how a server offers *context* rather than *actions*, which becomes the whole subject of [Context, Memory & RAG](03-context-memory-rag.md).

## The part that isn't obvious: discovery

If MCP were only a file format for describing tools, it would be useful but unremarkable.

The part that changes system design is that discovery happens **at runtime**. Your agent doesn't have `lookup_billing_account` compiled into it. It asks the server what's available, gets back a list of names and descriptions, and decides what to call.

In the reference implementation accompanying this guide, that looks like this:

```python
client = ToolClient(ticketing_server)

tools = client.discover()          # asks: what can you do?
client.invoke("lookup_billing_account", customer_id="CUST-002")
```

The client never imports `lookup_billing_account`. It never knows which system is behind it — REST API, database, third-party SaaS. It knows a name and some arguments.

That indirection is what makes the architecture in this guide possible. Because the agent is decoupled from the systems it uses, you can put something *between* them: a permission check, a budget ceiling, an audit log entry. Every control described in [Runtime Control Patterns](14-runtime-controls.md) lives in that gap. Without it, the agent calls your billing API directly and there is nowhere to stand.

!!! note "A useful way to hold this"
    MCP is to agents roughly what a device driver interface is to an operating system. The OS doesn't know how your specific printer works. It knows there is a thing that accepts print jobs, and the driver bridges the gap. New printer, same OS, no rewrite.

    The analogy also flags the risk: a driver runs with real privileges. So does an MCP server.

## Isn't this just an API? Didn't REST solve this?

This is the right objection, and worth taking seriously rather than waving away.

REST and GraphQL standardised how a **client** talks to a **service**. They did that well. But they assume a competent developer on the other end who reads the documentation, understands what the endpoints mean, and writes correct code. The standardisation is in the *transport and shape* — not in the meaning.

An agent has no developer. It's deciding, at runtime, from a description it just read, whether this is the right thing to call. That's a different problem, and it needs things REST has no concept of:

- **Runtime discovery** — REST assumes you already know the endpoints. An agent may be meeting your system for the first time, mid-conversation.
- **Descriptions written for a reader, not an implementer** — `GET /accounts/{id}` tells you the shape. It doesn't tell you *when calling this is the right move*.
- **Bidirectional flow** — an MCP server can ask the client's model to do something (sampling), which no REST API can do.

An MCP server is usually **a thin wrapper around your existing REST API**, not a replacement for it. You keep everything you have. You add an agent-facing description layer on top.

```python
@ticketing_server.register(
    "lookup_billing_account",
    "Look up a customer's billing account status by customer_id",
    {"customer_id": "string"},
)
def lookup_billing_account(customer_id: str) -> dict:
    # Behind here is your ordinary REST call to the billing system.
    ...
```

The function body is boring. The registration above it is the interesting part — that's the contract the model reads.

### Where OpenAPI fits

If you already maintain OpenAPI specs, you're closer than you think, and there's a real trap.

An entire tooling ecosystem now generates MCP servers directly from OpenAPI specs, which sounds like the end of the story: you already have the specs, press the button, done. In practice the emerging pattern is *"OpenAPI in, MCP out"* — the spec stays your system of record for the API contract, and the MCP layer is generated from it so the two can't drift.

But a study of production MCP servers found something worth pausing on: the great majority are thin wrappers over REST, yet they expose a median of only around **19%** of the underlying API's operations. The gap isn't laziness. It's that OpenAPI describes **structure** — endpoint, parameters, response shape — and an agent needs **intent**: when should I use this, and when shouldn't I?

A generated tool called `list` with the description "lists items" is technically correct and practically useless to a model choosing between forty options. `listAllOverdueInvoicesForCustomer` earns its length.

This is the first place in the guide where a task that looks like plumbing turns out to be a design job. Writing tool descriptions is writing for a reader who has no context, no colleague to ask, and one shot at choosing correctly.

## Where MCP stands

MCP was released in November 2024 and moved fast:

- **Donated to the Linux Foundation's Agentic AI Foundation** in December 2025, so governance is now multi-vendor rather than one company's
- **Adopted across Anthropic, OpenAI, Google, and Microsoft**, with 18,000+ community-indexed servers
- **A stateless transport rework** shipping mid-2026, so servers no longer need session affinity and can scale behind an ordinary load balancer

For architecture decisions, the practical read is: **MCP has effectively won its layer.** Choosing it is no longer a bet. That's worth saying plainly, because it's unusual — most protocol contests take years to resolve, and this one largely settled in eighteen months.

What has *not* settled is everything around it.

## What it doesn't solve

Adopting MCP solves the integration format. It does not solve four things, and mistaking one for the other is how the six-month stall in the introduction happens.

**It costs context.** Every tool description from every connected server is loaded into the model's context on every call — used or not. Connect five servers with twenty tools each and you're paying for a hundred descriptions on every question, including "what's your refund policy?" This is fact three arriving early: an architecture decision that is really a cost decision. The mitigation — load tools on demand rather than all at once — is covered in [Context, Memory & RAG](03-context-memory-rag.md), where one measured case cut context by 95% this way.

**Tool descriptions are attacker-influenceable.** The model reads descriptions to decide what to call. That makes them input — and input can be poisoned. Instructions hidden in a tool's description are read by the model but easily missed by a human reviewer skimming a config file. This was disclosed as a systemic issue across MCP's SDKs in May 2026. The mitigation is unglamorous: pin tool definitions and review a description change with the same seriousness as a code change. A registry whose contents can change without review isn't a control. [Agent Security](13-agent-security.md) covers this properly.

**It concentrates credentials.** Your billing MCP server holds billing credentials. Your shipping server holds shipping credentials. That's good design — until one server is compromised and becomes a single point of access to everything behind it.

**It says nothing about who's allowed to do what.** MCP describes *how* to call a tool. It has no opinion on whether this particular agent, acting for this particular user, should be permitted to issue a refund. That's yours to build, and it's the subject of [Enterprise Governance](10-enterprise-governance.md).

That last point deserves emphasis because it's the most common misreading. MCP gives you the *place* to put a permission check — the gap between agent and system that discovery creates. It does not give you the check.

## Back to the support assistant

Where does this leave our system?

The billing lookup now lives behind an MCP server rather than inside the application. The assistant discovers it at runtime instead of importing it. If the team switches models next quarter, nothing about the billing integration changes. When the ops team needs the same lookup, they connect to the same server instead of writing their own.

And there is now a defined point where every call to the billing system passes through — which is where, in later chapters, we'll put the permission check, the budget ceiling, and the audit record.

What we have not solved: the assistant can now *reach* the billing system, but nothing decides whether it should be allowed to. Nothing checks whether its answer was right. Nothing counts what the answer cost.

Those are the next three chapters.

## Summary

- The model is stateless and cannot reach your systems. Connecting it requires glue, and hand-written glue grows as N×M — models times systems.
- MCP standardises that glue into one format. N×M becomes N+M.
- Three roles (host, client, server) and three primitives (tools, resources, prompts).
- The design-changing property is **runtime discovery** — the agent asks what's available rather than having it compiled in. That indirection is where every later control lives.
- It complements REST rather than replacing it; an MCP server usually wraps an existing API. If you have OpenAPI specs, generate from them — but expect to invest in **intent-carrying descriptions**, because structure alone doesn't tell a model when to call something.
- MCP has effectively won its layer. Adopting it is safe. It leaves context cost, description poisoning, credential concentration, and authorisation entirely to you.

## Try it

The reference implementation in `boilerplate/src/mcp_tools.py` is a working server and client in about eighty lines. Run the whole system with:

```bash
cd boilerplate && python3 main.py
```

Two things worth doing rather than just reading:

1. **Add a tool.** Register `check_shipping_status` on the ticketing server. Notice you don't touch the client at all — that's discovery doing its job.
2. **Break a description.** Change `lookup_billing_account`'s description to something vague like "gets data". Then re-read the section on intent above and ask whether a model choosing among forty tools would still pick it correctly.
