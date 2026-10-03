# AxiomEmbedded Product Specification

## Product objective

Provide a reusable engineering substrate that AI agents and human engineers can use to manage embedded and cyber-physical product development across domains and technologies without duplicating the lifecycle engine.

## Stable concepts

- **Artifact:** a typed engineering object such as requirement, architecture element, code unit, test, defect, change, risk or evidence.
- **Relationship:** a typed edge between artifacts, such as satisfies, realizes, verifies, depends-on or derived-from.
- **Profile:** composition of domain, platform, language, OS, lifecycle, standards metadata and enabled capabilities.
- **Skill:** a reusable human/agent capability with inputs, outputs, tools, guardrails and verification.
- **Agent:** an executor/analyst that uses skills and tools under explicit permissions.
- **Workflow:** stateful lifecycle orchestration with gates and evidence requirements.
- **Evidence:** immutable-ish record of an action, input baseline, toolchain, output and verification result.

## Non-goals

AxiomEmbedded is not a replacement for vendor SDKs, certified safety tools, licensed normative standards, PLM/ALM systems, or an accreditation/certification body.
