# Production Technology & Blockers

## Technology options, by control tier

**Sovereign public cloud** (fastest to production, IRAP-backed)
- Azure — IRAP-assessed to PROTECTED level (reassessed every 24 months); Sovereign Landing Zone; in-country Copilot processing live in Australia
- AWS — Sydney availability zones; $20B AUD Australian data-centre investment
- GovAI Hosting — whole-of-government offering on GovTEAMS, pre-aligned to ISM/PSPF, capped at OFFICIAL:Sensitive

**Sovereign private cloud / disconnected** (highest control, PROTECTED+/classified)
- Azure Local + Foundry Local — large models fully on-premises or disconnected; NVIDIA-certified hardware; governance/identity/audit stay inside the customer boundary. Disconnected-ops GA landed early 2026.
- Confidential computing — hardware-level attestation so even the cloud operator can't access data/model in use

**Low-code / pro-code layering** (the actual 2026 production pattern)
- Copilot Studio for fast departmental agents (hours to first version, ~500-document ceiling)
- Azure AI Foundry for model-level control, fine-tuning, custom RAG, eval gates
- Connected via A2A, governed through a unified control plane

## Key blockers and mitigations

| Blocker | Mitigation |
|---|---|
| "Australian hosting" claims often cover storage only — inference can route offshore at peak load | Demand explicit Standard Regional deployment documentation; use on-boundary inference (e.g. Foundry Local) when ambiguity is unacceptable |
| GPU capacity scarcity — 36–52 week hardware lead times, reserved pools locked, on-demand 2–3x pricier | Favor distilled/quantized models that fit available hardware over frontier models you can't provision; pre-commit compute 6+ months ahead for predictable workloads |
| Compliance treated as point-in-time, not continuous — IRAP certifies the platform, not your configuration | Build evidence generation into the platform itself (model registry with artifact hashes, dataset lineage, eval outputs, attestation records) rather than bolting on audit prep afterward |
| Skills gap in operating sovereign AI infrastructure | Lead with enablement/training as a genuine differentiator, not just compliance — it reduces real deployment risk |
| "Full-stack sovereignty" is largely a myth — even national programs depend on foreign hardware/corpora | Reframe from "sovereignty" to "resilience and control" using the four-layer model — harder for a competitor to counter with a cheaper "we're local too" claim |

## The synthesis

The technology to hit PROTECTED-level production exists and is maturing fast. The real blockers have shifted from "can we build this" to "can we prove and sustain it under audit while GPU supply is constrained." That makes this a services-and-governance sale as much as a platform sale.
