# Australian AI Governance & Security

## National policy — deliberately non-binding

Australia rejected a standalone AI Act. The **National AI Plan** (Dec 2025) shelved the 2024 mandatory-guardrails proposal after ~300 consultation submissions, largely on innovation-chilling-effect grounds.

- **Guidance for AI Adoption (GfAA)**, Oct 2025 — supersedes the old Voluntary AI Safety Standard; condenses 10 guardrails into **six essential practices ("AI6")**. Non-binding, but the reference point for governance-maturity assessments.
- **Australian AI Safety Institute (AISI)** — operational early 2026; independent technical safety analysis, not itself a regulator.
- Government approach: manage AI risk through **existing technology-neutral laws** (Privacy Act, Australian Consumer Law, SOCI Act) rather than AI-specific legislation.

## Sensitive information management — where it becomes binding

- **PSPF (Protective Security Policy Framework)** — applies to Commonwealth entities. PSPF Policy Advisory 001-2026 addresses cyber security readiness specifically for the frontier AI era.
- **ISM (Information Security Manual)**, ASD — the technical control set PSPF is measured against. Every AI system touching government data needs ITSA (IT Security Adviser) sign-off or an existing authorisation boundary.
- **ASD's "Engaging with AI" guidance** + AI Data Security information sheet — securing data across the AI lifecycle.
- **Essential Eight** — baseline technical mitigations, used alongside PSPF/ISM in most assessments.
- **IRAP (Infosec Registered Assessors Program)** — the assessment mechanism certifying a *specific tenant configuration* meets ISM. Compliance is a shared-responsibility model: the platform provider (Microsoft/AWS/Google) provides the certified platform; the agency configures, operates, and evidences the controls. IRAP is explicitly not a pass/fail certificate.
- **Home Affairs Policy Advisory on OFFICIAL Information Use with Generative AI** — restricts which generative AI products can be used with government OFFICIAL-classified information.

## Data sovereignty — four layers, not one

Genuine sovereignty is not just data residency:

1. **Data residency** — where it's stored/processed (Hosting Certification Framework)
2. **Provider risk** — foreign ownership/control/influence (FOCI) exposure
3. **Model behaviour/inference control** — do you control what the model *does* with the data, not just where it sits
4. **Auditability** — can you evidence compliance on demand

Layer 1 gets all the marketing attention; layers 2–4 are where deals actually get won or lost on technical credibility.

## Privacy — binding law, with a hard deadline

- **Privacy Act 1988 / Australian Privacy Principles (APPs)**
- **New APP 1.7–1.9, effective 10 December 2026** — must disclose in privacy policies what personal information feeds substantially automated decisions, and the nature of decisions where AI significantly affects individual rights.

## Critical infrastructure & sector overlays

- **SOCI Act** — critical infrastructure operators
- **Cyber Security Act 2025** — ransomware payment reporting, incident review board rules, smart-device security standards (from March 2026)
- Sector regulators (e.g. APRA) apply existing prudential requirements to AI use on top of PSPF/ISM where applicable — often two frameworks simultaneously

## The practical takeaway

Unlike the EU AI Act's binding risk tiers, Australia's model is: prove governance maturity against non-binding guidance (GfAA/AI6), while binding requirements sit in adjacent technology-neutral frameworks. There's no single checklist to point to — which makes demonstrated **auditability and control** (layer 4 of sovereignty) do more persuasive work than "we comply with X Act," because there often isn't an X Act yet.
