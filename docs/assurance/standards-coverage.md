# Standards coverage map

Only number, title, edition/year, and clause numbers are cited. Requirement
summaries are original language; no normative text is reproduced.

| Skill | Standards considered |
|---|---|
| axiom-scope-context (+review) | ISO 12100:2010, ISO 10218-2:2011, ISO 11161:2007 |
| axiom-hazard-risk (+review) | ISO 12100:2010, ISO 10218-1:2011, ISO 10218-2:2011, ISO/TS 15066:2016, ISO 13849-1:2023, ISO 13850:2015, ISO 14118:2017 |
| axiom-safety-requirements (+review) | ISO 12100:2010, ISO 13849-1:2023, ISO 13850:2015, ISO 14118:2017, IEC 62061:2021, IEC 61508:2010 |
| axiom-vnv-plan (+review) | ISO 12100:2010, ISO 13849-2:2012, ISO/TS 15066:2016, IEC 62061:2021 |
| axiom-threat-model (+review) | IEC 62443-3-3:2013, IEC 62443-3-2:2020, IEC 62443-4-1:2018, IEC 62443-4-2:2019 |

Family registrations live in `standards/industrial/` (`iso-12100`,
`iso-10218`, `iso-ts-15066`, `iso-13849`, `iso-13850`, `iso-14118`,
`iso-11161`, `iec-62061`, plus the pre-existing `iec-61508` and `iec-62443`).
Each skill's `references/standard-map.md` records which clauses were
considered and separates mandatory requirements, recommended practice,
project decisions, assumptions, and open questions.

## Dependent skills and domains

The assurance skills are cross-domain `industrial` + `robotics` (primary
catalog domain stays `industrial` for grouping). Bidirectional
`related_skills` links connect each builder to the existing skill that owns
the adjacent lifecycle stage:

| Assurance builder | Dependent existing skill |
|---|---|
| axiom-scope-context | axiom-robotics-system-integration (cell integration scope) |
| axiom-hazard-risk | axiom-functional-safety (integrity-level workflow) |
| axiom-safety-requirements | safety (generic HARA-to-safety-case lifecycle) |
| axiom-vnv-plan | axiom-industrial-control-review (control review) |
| axiom-threat-model | security (product-security lifecycle) |

## Deliberately out of scope for this cell

- ISO 3691-4:2023 (driverless trucks/AMR) — the example cell is fixed; no
  mobile platform. Add it if an AMR feed is introduced.
- ISO 13482:2014 (personal-care robots) — wrong product class.
- IEC 60204-1:2016 (electrical equipment of machines) — panel-build detail
  below the assurance-artifact level; referenced by SR-001 rationale only.
- Automotive (ISO 26262:2018, ISO/SAE 21434:2021), aerospace (DO-178C/DO-254),
  defense (MIL-STD-882E) — covered by existing skills and the roadmap; they
  extend this table in future verticals without changing the envelope.

Official sources: iso.org, iec.ch. Future verticals extend the table above;
they do not change the envelope.
