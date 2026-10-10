# codeql-standards-bridge

Runs the [CodeQL Coding Standards](https://github.com/github/codeql-coding-standards)
query packs **locally** (MIT licensed) through the CodeQL CLI and ingests
findings into Axiom evidence. This is a **reuse bridge, not a redevelopment**:
~370 AUTOSAR C++14 + ~207 MISRA C 2023 + ~175 MISRA C++ 2023 + CERT rules are
used pristine upstream — their ISO 26262 tool qualification is valid **only
as distributed by GitHub**, so queries are never vendored, forked, or edited
here. What Axiom owns is the deterministic local-run wrapper, SARIF
ingestion, provenance, and the skill rule binding (`static-analysis` §7).

## Prerequisite (once)

```bash
# CodeQL CLI >= 2.23.9 (pinned per supported_codeql_configs.json upstream)
# from https://github.com/github/codeql-cli-binaries/releases — then:
codeql --version
```

Without it the bridge fails closed with this hint. No other dependency:
packs download on first run via `codeql pack download`.

## Use

```bash
python tools/codeql-standards-bridge/bridge.py \
  --source src --build "cmake --build build" --db out/db --out out/codeql \
  --language cpp --pack autosar-cpp --pack-version 2.63.0
python tools/codeql-standards-bridge/bridge.py \
  --source src --build "make" --db out/db --out out/codeql \
  --language c --pack misra-c --suite audit --pack-version 2.63.0
```

Suites: `default` (violations) | `audit` (review candidates) | `strict`
(deliberate-looking contraventions). Pin `--pack-version` in CI; the resolved
versions land in `provenance.json` alongside CLI version and db/sarif hashes.

Outputs: `findings.json`, `provenance.json`. Findings end in the skill
dispositions (fixed / deviation via `coding-standards.yml` / false-positive),
never silent suppressions. See `docs/external-packs.md` (link-don't-bundle).
