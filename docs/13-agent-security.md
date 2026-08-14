# Agent Security

Chapter 1 flagged tool poisoning; Chapter 10 flagged prompt injection at the governance layer. This chapter is the security material in one place, because it's the area where the gap between "we configured guardrails" and "we have a control" is widest.

## The lethal trifecta

Simon Willison's framing is the most useful mental model in this space, precisely because it's structural rather than a list of mitigations. An agent is exploitable when it has all three of:

1. **Access to private data**
2. **Exposure to untrusted content**
3. **The ability to communicate externally**

Any agent with all three can be induced to exfiltrate — the untrusted content carries the instruction, the private data is the payload, and the external channel is the exit. Willison's position is that this is **structural, not fixable by prompt hardening**. If your architecture puts all three in one agent, the mitigation isn't a better system prompt; it's removing one of the three legs.

Practically, that means the design question is: *can this agent be split so no single one holds all three?* A retrieval agent that reads untrusted content but has no external send capability, handing structured output to a separate agent that can send — that's the shape.

## Prompt injection is not jailbreaking

Worth keeping distinct, because conflating them leads to the wrong defence:

- **Jailbreaking** — persuading the model to violate its own policies. A model-alignment problem.
- **Prompt injection** — mixing trusted instructions and untrusted content in one context, so the model can't tell which is which. An *architecture* problem.

The second is the one that matters for agents, and no amount of model alignment solves it, because the model is behaving correctly given a context it has no way to partition.

**Indirect injection is the real vector.** The payload doesn't arrive in the user's message where your input guardrail is watching — it arrives later, inside a retrieved document, a tool result, or a web page the agent fetched. The guardrail already ran.

## Tool descriptions are model-facing input

This is the sharpest current complication to the "tool registry is the security boundary" principle, and it's worth being precise about.

The registry *is* the right boundary — authorisation enforced outside the model, never in the system prompt. But the model reads tool **descriptions** to decide what to call. That means tool descriptions are attacker-influenceable model-facing input, and a boundary made partly of text an attacker can shape is only half a boundary. The MCP threat literature (see the MCP-38 taxonomy in [References](references.md)) names tool description poisoning specifically.

**The mitigation is unglamorous:** pin tool definitions, review on change, and treat a tool-description diff with the same seriousness as a code diff. A registry whose contents can change without review isn't a control.

## The defence ladder

Roughly in order of maturity:

| Layer | What it does | Limit |
|---|---|---|
| **Input guardrails** | Filter the user's message | Misses indirect injection entirely |
| **Output guardrails** | Classifiers, jailbreak detection, citation enforcement | Only catches what it was tuned for; needs adversarial testing, not just configuration |
| **Architectural separation** | Break the lethal trifecta; treat all retrieved and tool-returned content as untrusted **data**, never as instructions | The strongest structural move available |
| **Runtime detection wrappers** | Re-run the trajectory against a masked prompt and compare (the MELON approach) — published results show large reductions in attack success with task utility broadly intact | Adds inference cost per run |
| **Scoped, short-lived credentials** | Tools carry scoped credentials, not bearer tokens; workload identity per agent | Only bounds the blast radius, doesn't prevent the injection |

The shift worth noting: **"we red-team it" used to be a sufficient answer and no longer is**, now that runtime-detection wrappers with published numbers exist. Adversarial testing plus a runtime defence is the current bar.

## Frameworks to test against

- **OWASP Top 10 for LLM Applications** — particularly LLM01 (prompt injection), LLM06 (excessive agency), LLM09 (misinformation)
- **MITRE ATLAS** — the adversarial-tactics vocabulary for AI systems

The distinction that matters when someone claims compliance: were these frameworks used to *test adversarially*, or just to *configure* a checklist? Only the first is evidence.

## Where identity fits

Every mitigation above bounds damage; none prevents a determined injection. That makes attribution and revocation the last line — which is why workload identity per agent ([Enterprise Governance](10-enterprise-governance.md)) is a security control and not just a governance one. Survey data through 2026 consistently finds most organisations cannot cleanly distinguish agent activity from human activity in their logs, which means they cannot attribute an incident to an agent even after they know one occurred.
