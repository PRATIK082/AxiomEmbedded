# Standards map (identifiers only)

Source of truth: `standards/registry.yaml` at the repository root. This file
lists candidate identifiers for automotive applicability work. It carries no
normative text -- consult the licensed originals for requirements.

## Process

| ID | Title (short) | Use in applicability work |
|----|---------------|---------------------------|
| automotive-spice | Automotive SPICE PAM | Applicable when contractually required; record PAM version and scope |
| iso-26262 | Road vehicles -- Functional safety | Applicable only with safety scope + governing safety plan |
| iso-sae-21434 | Road vehicles -- Cybersecurity engineering | Applicable only with cybersecurity scope + risk assessment |
| iso-21448 | SOTIF | Applicable when intended-functionality safety scope exists |
| unece-r155 | UN R155 cyber security | Applicable when type-approval scope includes it |
| unece-r156 | UN R156 software update | Applicable when type-approval scope includes it |

## Coding guidelines

| ID | Title (short) | Use in applicability work |
|----|---------------|---------------------------|
| misra-c | MISRA C | Applicable when project coding guidelines select it; record edition |
| misra-cpp | MISRA C++ | Applicable when project coding guidelines select it; record edition |
| autosar-cpp14 | AUTOSAR C++14 Guidelines | Applicable when project coding guidelines select it |
| sei-cert-c | SEI CERT C | Optional hardening reference; record only if selected |
| sei-cert-cpp | SEI CERT C++ | Optional hardening reference; record only if selected |

## Lifecycle rule

- `published` -> may be cited as normative basis.
- `pre-release` / `draft` / `proposed` -> informative only; must not replace
  the published edition as requirement basis.
- `withdrawn` / `superseded` -> must not be used for new work.

Verify the current lifecycle state in `standards/registry.yaml` at time of
use; this map does not duplicate it.
