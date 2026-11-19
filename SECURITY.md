# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.2.x | yes |
| < 0.2 | no |

## Reporting a vulnerability

Please report security vulnerabilities privately to the maintainer at
**pratik.patil082@gmail.com** with the subject line "AxiomEmbedded security
report". Do not open a public issue for a suspected vulnerability.

We aim to acknowledge reports within 72 hours and to provide a fix or
mitigation plan within 14 days for confirmed issues.

## Scope

AxiomEmbedded is an engineering-process automation tool. It does not ship
runtime firmware, does not execute untrusted code by default, and does not
transmit data off-host. Relevant vulnerability classes include:

- Path traversal in skill runner / tool wrappers (target_files, output_dir)
- Command injection in any subprocess invocation
- Secret leakage in logs, manifests, or generated artifacts
- Unsafe deserialization of YAML/JSON inputs
- MCP server input sanitization (skill_id allowlist, no `..` escape)

## Safe-use boundary

A passing check in AxiomEmbedded is engineering evidence, not proof of
compliance, safety integrity, security certification, or airworthiness. The
adopting project must determine applicable editions, objectives, independence
requirements, and evidence with qualified personnel and authorised tools.
AxiomEmbedded must not be represented as a certification tool.

## Disclosure

We follow coordinated disclosure. After a fix is available we will publish an
advisory in the GitHub Security tab and credit the reporter (unless anonymity
is requested).
