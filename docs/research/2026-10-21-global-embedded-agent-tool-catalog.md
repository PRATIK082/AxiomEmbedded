# Global Embedded Agent — pluggable tool catalogue and milestone plan

- **Date:** 2026-10-21
- **Branch:** `feat/pluggable-tool-packs`
- **Status:** plan (M0 complete — survey recorded and machine-validated)
- **Machine-readable source of truth:** `registries/tool-candidates.yaml`
  (181 candidates: 162 adoptable, 19 informational/rejected)
- **Schema:** `schemas/tool-candidate.schema.json`
- **Validator:** `python scripts/validate_tool_candidates.py`
- **Resolver:** `packages/toolpacks/candidates.py` → `axiom tools`

---

## 1. Vision

AxiomEmbedded is already a domain-neutral engineering platform: one core, a
manifest-driven plugin surface, and overlay packages per domain, platform and
standard. What it is *not* yet is a **global embedded agent** — an agent that
can pick up any embedded project (automotive ECU, aerospace RTOS, industrial
Linux gateway, robotics edge node) and act competently in it, with real
tooling behind it.

The gap is not skills. The repo has ~200 skills across 14 domains and 28
platforms. The gap is **tools**: the deterministic operations the skills
assume exist — static analysis, coverage, SBOM, UDS execution, flash and
debug, simulation, requirement tracing — are mostly *named* but not *wired*.
Today Axiom ships 12 tool adapters, most of them thin placeholders
(`static-analysis-aggregator`, `coverage-ingestor`, `test-generator`).

This plan closes that gap using **open-source tools that already exist**,
wired through the existing plugin contract rather than reinvented. The
platform stays domain-neutral: the tool set is *selected* per project, never
*hard-coded* into core.

**The one-line thesis:** *AxiomEmbedded should not build embedded tooling; it
should become the manifest-driven contract through which the best open-source
embedded tooling is selected, invoked, and turned into evidence.*

---

## 2. How the plugin surface works today

Nine extension points exist. Three of them matter for this plan.

### 2.1 Tool adapter — `tools/<id>/manifest.yaml`

Schema (`schemas/tool.schema.json`): required `id`, `version`, `purpose`;
optional `inputs`, `outputs`, `permissions`, `deterministic`, `evidence`.

The reference implementation is `tools/diag-extract-bridge/manifest.yaml`,
which extends the base with:

```yaml
external:
  pip: acme-diag-extract>=2.1,<3
  entry_point: acme_diag_extract.extract
  cli: acme-diag-extract
  supported_inputs: [arxml, odx, pdx, cdd, xlsx, xls]
  supported_autosar: [R20-11 ... R25-11]
dependencies:
- acme-diag-extract>=2.1,<3
facets:
  domains: [automotive]
  platforms: [mcu, mpu, soc, mpsoc, autosar-classic, autosar-adaptive]
  standards: [ISO 14229-1, AUTOSAR DEXT]
```

`docs/external-packs.md` is the normative recipe: *"Develop independent, map
here."* The bridge validates shape and records provenance; the upstream pack
owns format knowledge. The bridge fails closed with an actionable
`pip install …` message and never silently coerces.

### 2.2 Facet selection — `registries/tool-facets.yaml` → `registries/tool-index.json`

`python scripts/build_tool_index.py` indexes the facets and stamps them back
into each manifest. Matching rule: a tool engages when `"all"` is in its
facets **or** the requested value is listed. An empty `standards` facet means
"generic, always matches".

`packages/toolpacks/select.py` → `select_packs(domain, platform, standards)`
returns `{tools, tool_count, install, agents, skills, manifests}`, exposed
identically by the CLI (`axiom packs`), the SDK
(`axiom_sdk.select_toolpacks`), the MCP server (`packs`) and REST
(`/v1/packs`). All four agree by construction — enforced by
`tests/test_toolpacks.py` and `tests/test_interfaces.py`.

### 2.3 The candidate surface (new in this change)

`axiom packs` answers *"which tools are adopted?"*. The new
`axiom tools` answers *"which open-source tools could serve this project, and
what would each one buy me?"* — the proposal layer that feeds the next
milestone.

```
registries/tool-candidates.yaml   # 181 surveyed tools: licence, channel, plugin point, benefit
        │
        ├── scripts/validate_tool_candidates.py   # deterministic contract + licence checks
        │
        └── packages/toolpacks/candidates.py      # facet resolver
                    │
                    ├── axiom tools  (CLI)
                    ├── axiom_sdk.list_tool_candidates()
                    └── MCP tool_candidates
```

`select_candidates()` returns the candidate set plus `by_channel`,
`by_milestone` and `pip_install`, so an operator can see at a glance which
options are a one-line `pip install` and which need a container or a system
package. `reference` and `rejected` entries are retained for auditability but
are never proposed by default.

---

## 3. The catalogue

181 candidates, verified against upstream (GitHub API, `LICENSE` files, PyPI
JSON) on 2026-10-21. Install channels across the adoptable set:

| Channel | Count | Meaning |
| --- | --- | --- |
| `pip` | 62 | Python package — trivially adoptable, no toolchain |
| `source` | 48 | Source tree — build is out of band, Axiom ships a thin adapter |
| `binary` | 43 | Standalone release binary or apt package |
| `apt` | 12 | Distro package (CI-friendly, do not build from source) |
| `container` | 9 | Container image |
| `npm` | 5 | Node CLI |
| `gem` / `cargo` | 1 / 1 | Ruby gem / Rust crate |

### 3.1 Static analysis, MISRA and CERT — 18 candidates

| Tool | Licence | Channel | Benefit |
| --- | --- | --- | --- |
| **clang-tidy** | Apache-2.0 + LLVM-ex | binary | One adapter covers `cert-*` (SEI CERT), `cppcoreguidelines-*`, `bugprone-*` and `llvm-header-guard`; consumes the `compile_commands.json` Axiom already produces per target triple. |
| **Clang Static Analyzer** | Apache-2.0 + LLVM-ex | binary | Path-sensitive dataflow findings (null deref, leak, use-after-free) that clang-tidy cannot produce; emits plist/SARIF that Axiom normalises into evidence rows. |
| **semgrep** | LGPL-2.1 | pip | Cheapest way to encode project-specific embedded rules ("no dynamic allocation in an ISR", "no `printf` in task context") as versioned per-domain overlay rule packs. |
| **reviewdog** | MIT | binary | The universal normaliser: filters *any* linter's output to the diff and re-emits SARIF or a PR comment, so twenty heterogeneous analysers become one evidence stream. |
| **cppcheck** (+ `misra.py`) | GPL-3.0 | binary | The only practical *build-free* analyser for vendor/legacy MCU code: tolerates inline asm, missing headers and non-standard syntax; ships a 143-rule MISRA C:2012 addon that reports rule **numbers only**. |
| **codeql-coding-standards** | MIT | binary | The strongest OSS MISRA story (MISRA C:2012/2023, MISRA C++:2023, AUTOSAR C++14, SEI CERT) and ISO 26262 Part 8 tool-qualified. ⚠️ The CodeQL *CLI* is separately licensed for closed-source analysis — see §5. |
| **clang-tidy-automotive** | LLVM-ex | source | 172 checks mapped to MISRA C:2012/2023/2025 while **separating rule mapping from check implementation** — the architectural precedent Axiom's profile packages should imitate. |
| **naivesystems/analyze** | GPL-3.0 | container | MISRA C:2012/2019, MISRA C++:2008, AUTOSAR C++14 in a container. ⚠️ Fedora-based images only. |
| **coccinelle** | GPL-2.0 | binary | SmML semantic patches for bespoke internal rules no off-the-shelf linter has (e.g. "no blocking call in ISR"). |
| **CBMC** | BSD-4-Clause | binary | Bounded model checker — the closest OSS path to *proof-grade* evidence for ISO 26262 / EN 50128. |
| **lizard** | Other | pip | Complexity and clone detection with no headers and no compile DB — the only analyser that works on an unbuildable vendor tree. |
| **flawfinder** | GPL-2.0 | pip | Lexical CWE scan of dangerous C functions that still works on code that does not compile. |

### 3.2 Coverage, hardening and supply chain — 18 candidates

| Tool | Licence | Channel | Benefit |
| --- | --- | --- | --- |
| **gcovr** | BSD-3 | pip | One pip dependency turns gcov/llvm-cov output into Cobertura, JaCoCo, Clover, LCOV, SonarQube, JSON, CSV and Markdown — one adapter, every downstream consumer. |
| **llvm-cov** | Apache-2.0 + LLVM-ex | binary | Region-precise coverage for cross-compiled targets; the companion to clang-tidy and libFuzzer when the GCC gcov runtime is unavailable. |
| **kcov** | GPL-2.0 | binary | Coverage from DWARF **without recompilation** — the only option for pre-built vendor objects. |
| **checksec.py** / Go port | GPL-3.0 | pip / binary | Proves the shipped ECU/rootfs image actually carries RELRO, Canary, NX, PIE, FORTIFY. The Go port's `--fail-if` turns hardening into a blocking CI check. |
| **syft** | Apache-2.0 | binary | Generates SPDX + CycloneDX SBOMs from directories, archives and container images — the foundation for firmware-image SBOM. |
| **grype** | Apache-2.0 | binary | Matches an SBOM against CVEs with EPSS/KEV scoring and OpenVEX support: "what is in this image" → "what is exploitable in this image". |
| **osv-scanner** | Apache-2.0 | binary | Detects **vendored** C/C++ with call analysis, cutting the false-positive rate that makes embedded SCA unusable; `--offline` mode for air-gapped CI. |
| **cve-bin-tool** | GPL-3.0 | pip | 450+ binary checkers fingerprint the libraries actually *compiled into* a shipped ECU image — the question no source-level SCA tool answers. |
| **cyclonedx-python-lib** / **spdx-tools** | Apache-2.0 | pip | Emit and validate both major SBOM dialects natively in-process. |
| **reuse-tool** | GPL-3.0 | pip | Per-file SPDX header compliance — a traceability requirement, not just a legal one. |
| **pip-licenses** | MIT | pip | `--fail-on="GPL-3.0"` turns Axiom's own licence hygiene into a build failure instead of a surprise. |
| **OpenSCAP** | LGPL-2.1 | binary | NIST SCAP 1.2 certified — the OSS route to CIS-benchmark evidence for an embedded-Linux BSP. ⚠️ Benchmark content is separately licensed. |

### 3.3 Test frameworks and execution — 20 candidates

| Tool | Licence | Channel | Benefit |
| --- | --- | --- | --- |
| **Unity** | MIT | source | The de-facto embedded unit-test framework (~1 KB RAM, C99, no OS) — a zero-dependency unit-test substrate for every Axiom target profile. |
| **CMock** | MIT | source | Auto-generates mocks from headers: an interface-contract artifact becomes a compilable mock and a hardware-free test double. |
| **Ceedling** | MIT | gem | Orchestrates Unity+CMock+CException into one CI target that builds, links, runs host-simulated tests and emits coverage XML. |
| **Robot Framework** | Apache-2.0 | pip | The only realistic way to encode a HIL test plan as reviewable, diff-able, traceable text that humans *and* agents can edit. |
| **gcov / llvm-cov** | GPL-3.0+RLE / Apache-2.0 | binary | GCC Runtime Library Exception means gcov instrumentation does **not** infect a proprietary embedded product — critical for automotive IP. |
| **cocotb** | BSD-3 | pip | Python HDL verification — the standard for verification-IP and bus-functional-model work. |
| **RobotFramework-UDS** | Apache-2.0 | pip | Bosch-supplied ISO 14229 keywords: an Axiom UDS vector set becomes executable bench steps. |

### 3.4 Debug, flash and target access — 12 candidates

| Tool | Licence | Channel | Benefit |
| --- | --- | --- | --- |
| **pyOCD** | Apache-2.0 | pip | Pure-pip CMSIS-DAP flash + debug + GDB server with no vendor SDK — the single highest-leverage adapter for bringing up an unknown Cortex-M target. Replaces J-Link/Ozone. |
| **OpenOCD** | GPL-2.0 + exception | apt | The OSS JTAG/SWD GDB server every attach workflow needs, with a target matrix no single vendor probe provides. |
| **stlink** | BSD-3 | apt | Open replacement for STM32CubeProgrammer's flashing step. |
| **esptool** | GPL-2.0 | pip | A complete flash-and-verify adapter for ESP32 in one pip dependency. |
| **IntelHex** | BSD-3 | pip | HEX/ELF/BIN conversion so the flashed binary and the evidence-attested binary are provably the same bytes. |

### 3.5 Emulation, HIL and fault injection — 14 candidates

| Tool | Licence | Channel | Benefit |
| --- | --- | --- | --- |
| **Renode** | MIT | binary | Multi-arch MCU simulator (Cortex-M/A/R, RISC-V, Xtensa) running **unmodified** binaries — the only OSS path to reproducible HIL-without-hardware. |
| **QEMU** | GPL-2.0 | apt | System emulation for Linux-class targets. |
| **Unicorn** | GPL-2.0 | pip | Multi-arch CPU emulator with Python bindings — the cheapest deterministic instruction-level fault injector. |
| **Fuzzware** | Apache-2.0 | binary | The only verified OSS fuzzer purpose-built for **ARM Cortex-M firmware images** with MMIO modelling (USENIX Sec '22). |
| **AFL++** | AGPL-3.0 | source | The general workhorse; `afl-cmin`/`tmin`, unicorn and QEMU modes. ⚠️ AGPL §13 if exposed as a network service. |
| **boofuzz** | GPL-2.0 | pip | Protocol fuzzing over serial/TCP/UDP/raw sockets — the right tool for UDS, DoIP and bootloader attack surfaces. |
| **angr** | BSD-2 | pip | Cleanest pip-installable binary-analysis library: CFG, decompilation, symbolic execution, reachability for firmware images. |
| **Ghidra** / **Rizin** / **radare2** | Apache-2.0 / LGPL-3.0 | binary / source | Binary triage of shipped images; `analyzeHeadless` is a legitimate CI adapter. |
| **FLOSS** | Apache-2.0 | pip | Extracts obfuscated/stack/tight strings — surfaces hidden credentials, CAN IDs and diagnostic keys. |
| **Binwalk** | MIT | cargo | Extracts embedded filesystems and partitions from ECU flash images. |

### 3.6 RTOS, BSP and platform targets — 18 candidates

`zephyr` (+ `west`, `zephyr-sdk`), `freertos`, `nuttx`, `tock`, `riot`,
`threadx` (now genuinely OSS under Eclipse), `rtems`, `esp-idf`, `buildroot`,
`yocto-bitbake`, `mcuboot`, `trusted-firmware-m`, `arm-tf-a`, `cmsis-core`,
`libopencm3`, `mbed-tls`, `openthread`.

Benefit in one line: they turn Axiom's `platforms/*` and `skills/rtos`,
`skills/bootloader`, `skills/drivers` from *descriptions* into *buildable
targets* with real, pinned, reproducible workspaces (`west` is the
reproducibility mechanism; `zephyr-sdk` removes the longest unreproducible
step from any embedded CI).

### 3.7 AUTOSAR, UDS, DoIP and CAN — 16 candidates

| Tool | Licence | Channel | Benefit |
| --- | --- | --- | --- |
| **odxtools** | MIT | pip | **Replaces the placeholder `acme-diag-extract` dependency with a real pack**: parses ODX/PDX, resolves diagnostic layers and DIDs, encodes/decodes genuine ISO 14229 requests into the canonical UDS test-spec. |
| **autosar-data-py** | Apache-2.0 | pip | The strongest pip-installable ARXML reader/writer, with strict schema validation on load — it can *prove* an ARXML matches the declared AUTOSAR version. |
| **py-armodel** | MIT | pip | The most mature pure-Python ARXML parser/writer (auto-detect 4.0.3→R24-11) — the portable fallback when the Rust wheel is unavailable. |
| **udsoncan** | MIT | pip | The reference ISO 14229-1 client: closes the loop by turning Axiom's generated UDS vectors into *executable* requests against a real ECU or vECU, producing pass/fail evidence rows. |
| **python-can** | LGPL-3.0 | pip | One uniform CAN/CAN-FD backend over SocketCAN, Vector, PCAN, slcan and **vcan** — the virtual bus is what makes Axiom's CAN CI hardware-free. |
| **can-isotp** | MIT | pip | ISO 15765-2 segmentation — the difference between "UDS works on the bench" and "UDS works on a real ECU". |
| **doipclient** | MIT | pip | Pure-Python ISO 13400 client designed as the udsoncan transport — the missing DoIP layer behind `axiom-diagnostics-doip`. |
| **canmatrix** | BSD-2 | pip | Ingests DBC, DBF, KCD, ARXML, SYM, XLS, LDF, ODX, EDS and FIBEX and exports them back; `canconvert` is a ready-made bridge CLI. |
| **cantools** | MIT | pip | Reads ARXML 3 & 4 plus CDD and **generates C source** from a DBC — closing the loop from communication matrix to compilable driver stubs. |
| **ldfparser** | MIT | pip | LIN (ISO 17987-1) is the one bus family in Axiom's scope with **no parser at all**; this closes the gap. |
| **FibexConverter** | GPL-2.0 | source | FIBEX 4 → text, Wireshark dissector, CSV/XLSX, topology graph and Peach fuzz models — the only open FIBEX path. |
| **vSomeIP** | MPL-2.0 | source | The reference SOME/IP stack with service discovery and E2E — a concrete runtime to validate zonal-architecture designs against. |
| **asammdf** | LGPL-3.0 | pip | Reads CAN and LIN logs from ASAM MDF4 using DBC/LDF/ARXML — closes the loop from canonical spec back to real measurements. |
| **CaringCaribou** | GPL-3.0 | source | DoIP/UDS security testing and fuzzing — a direct fit for `axiom-vehicle-cybersecurity`. |

### 3.8 Requirements, traceability, compliance and policy — 18 candidates

| Tool | Licence | Channel | Benefit |
| --- | --- | --- | --- |
| **openFastTrace** | GPL-3.0 | binary | Headless requirement→implementation tracing with a deterministic exit code and a `failBuild` switch; already ships `.agents/skills` for agent use. |
| **sphinx-needs** | MIT | pip | `.. req::` keeps requirement prose *and* its metadata (id, status, links, applicability) in one file — exactly Axiom's requirement-artifact shape — and emits a traceability matrix natively. |
| **StrictDoc** | Apache-2.0 | pip | Text-based requirements with real hierarchy, traceability-graph validation and ReqIF export. |
| **reqif** | Apache-2.0 | pip | The canonical OSS ReqIF parser/validator — the neutral interchange layer with DOORS, Jama and Polarion **without redistributing anyone's proprietary text**. |
| **OPA / Rego** | Apache-2.0 | binary | Encodes rule ID, applicability predicate and evidence requirement with **zero standards text** — the single best fit for Axiom's "standards metadata ≠ normative text" rule, and it becomes a machine-checkable rule artifact. |
| **Compliance Trestle** | Apache-2.0 | pip | NIST OSCAL 1.2.1 object model: a profile is a *subset of control IDs* with tailoring metadata — exactly the metadata/text split Axiom needs. |
| **Doxygen** | GPL-2.0 | apt | `\requirement` / `\ref` custom tags let the *code* carry requirement IDs — the natural bridge from Axiom requirements into embedded C/C++/Rust. |
| **ast-grep** | MIT | npm | Structural pattern search finds requirement anchors in embedded C/C++ **without a full build** — far cheaper than CodeQL or clang for a first pass, and it works on vendor blobs. |
| **lychee** | Apache-2.0 | binary | A traceability claim is only as good as the links behind it; lychee makes a dead requirement→code link a CI failure. |
| **DuckDB** | MIT | pip | Queries the traceability matrix and evidence ledger as SQL over Parquet/CSV — Axiom's CLI stays thin while "what is untraced?" is answered deterministically and offline. |

### 3.9 Documentation, diagrams, architecture and code knowledge — 22 candidates

`plantuml` (one JAR, headless, renders sequence/state/timing/gantt — first-class
in embedded review), `mermaid` (markdown-native, survives inside
agent-edited markdown), `d2` (deterministic layout — a diagram that renders
differently each run is not auditable evidence), `graphviz`, `sphinx`,
`mkdocs`, `madr` + `log4brains` (docs-as-code ADRs), `ctags`, `tree-sitter`,
`zoekt`, `kythe`, `markdownlint`, `pandoc`.

### 3.10 Bench, instruments, data and retrieval — 20 candidates

`pyvisa` + `RsInstrument` (vendor-neutral instrument abstraction),
`pymodbus`, `pyserial`, `sigrok-decode` (protocol decoders for logic
analysers), `sqlite-vec` (vector search inside SQLite — zero infrastructure
for a local ledger), `lancedb`, `gprof`, `perf`, `perfetto`, `bpftrace`,
`scalene`, `gitea`/`woodpecker` (self-hosted Git+CI for lab networks),
`in-toto` + `slsa-verifier` (build provenance).

### 3.11 MBD, simulation, robotics, FPGA and EDA — 28 candidates

`openmodelica` + `fmpy` + `python-control` (open MBD loop),
`ros2` + `micro-ros` (the MCU↔ROS2 bridge), `nav2`, `gazebo`, `sumo`,
`ns-3`, `yosys` + `nextpnr` + `icestorm`, `litex`, `amaranth`, `kicad`
(`kicad-cli` gives headless netlist/DRC/BOM), `klayout`, `openroad`,
`openlane`, `gdsfactory`.

### 3.12 Rejected — 13 candidates, with reasons

`reject-pvs-studio` (proprietary; free licence excludes corporate use),
`reject-codefactor` (proprietary SaaS), `reject-codeql-cli-commercial`
(CLI separately licensed for closed-source analysis),
`reject-infer` (last release 2021-05), `reject-tern` (Docker/OCI only),
`reject-safety-cli` (v3 requires paid auth for commercial use),
`reject-cve-search` (AGPL + MongoDB), `reject-adr-tools` (unmaintained since
2020), `reject-embunit` (dead since 2015), `reject-pysomeip` and
`reject-python-uds` (archived), `reject-modelio-for-compliance` (ships
vendor SysML profiles — safe for architecture, unsafe for standards-derived
content), `reject-unverified-projects` (named projects that could not be
verified to exist: `autosar-compliance-checker`, `CANtastic` as an analyser,
`ICsee`, `OpenFlightStack`, `mercedes-benz/ipcexamples`, `mercedes-benz/pyxdd`).

---

## 4. Milestone plan

Each milestone has a scope, a deliverable set, and an acceptance criterion
that is machine-checkable. Milestones are ordered by *risk reduction per unit
of work*, not by tool count.

### M0 — Survey and contract (COMPLETE)

- **Scope:** establish the machine-readable candidate registry, its schema, its
  validator, and the resolver exposed on every interface.
- **Deliverables:** `schemas/tool-candidate.schema.json`,
  `registries/tool-candidates.yaml` (181 candidates),
  `packages/toolpacks/candidates.py`,
  `scripts/validate_tool_candidates.py`, `tests/test_tool_candidates.py`,
  `axiom tools` CLI, `tool_candidates` MCP tool, `axiom_sdk.list_tool_candidates()`.
- **Acceptance:** `python scripts/validate_tool_candidates.py` exits 0 and
  reports `PASS (181 candidates, 162 adoptable)`; `pytest tests/test_tool_candidates.py`
  passes; CLI, MCP and SDK return byte-identical JSON for the same request.

### M1 — Evidence and policy backbone (25 candidates)

*Highest leverage: these tools convert "the agent says the code is fine" into
"the tool produced this finding, at this location, under this rule."*

- **Scope:** static analysis, coverage, SBOM/SCA, requirements traceability,
  machine-checkable policy.
- **Key tools:** clang-tidy, Clang Static Analyzer, semgrep, reviewdog, lizard,
  flawfinder, gcovr, syft, grype, osv-scanner, cve-bin-tool,
  cyclonedx-python-lib, spdx-tools, reuse-tool, pip-licenses, openFastTrace,
  sphinx-needs, strictdoc, reqif, OPA, lychee, sphinx, ast-grep, ctags, DuckDB.
- **Deliverables:** real implementations behind the placeholder adapters
  `static-analysis-aggregator`, `coverage-ingestor`, `dependency-analyzer`,
  `traceability-checker`; a `rules/` overlay package expressing applicability
  as Rego; a compliance-matrix artifact shape carrying
  `standard_id + edition + clause_id + applicability + project_interpretation + evidence_refs + status`.
- **Acceptance:** for one automotive MCU profile, `axiom run` produces a
  traceability matrix and a coverage report from tool output alone, with
  **zero** standard normative text present in the repository (verifiable by
  scanning the tree for standard clause prose); a deliberately seeded MISRA
  violation is detected and appears as an evidence row with a rule **ID**, not
  rule text.

### M2 — Target access, test substrate and build reproducibility (43 candidates)

*Turns Axiom from "can describe a bring-up" into "can perform a bring-up".*

- **Scope:** flash/debug, unit-test frameworks, RTOS/BSP targets, build systems.
- **Key tools:** pyOCD, OpenOCD, stlink, esptool, IntelHex, Unity, CMock,
  Ceedling, FFF, doctest, cppcheck, llvm-cov, checksec (py + Go), zephyr +
  west + zephyr-sdk, FreeRTOS, NuttX, Tock, RIOT, ThreadX, ESP-IDF, MCUboot,
  CMSIS-Core, libopencm3, Buildroot, Yocto/bitbake, RTEMS, CMake/CTest, Meson,
  Ninja, Conan, Doorstop, Doxygen, MADR/log4brains, MkDocs, PlantUML, Mermaid,
  D2, Graphviz, markdownlint, tree-sitter.
- **Deliverables:** `skills/hardware-bringup` gains a real flash-and-verify
  path; `skills/unit-test` gains a host-simulated target; `platforms/zephyr`
  gains a pinned, reproducible workspace; `skills/build-system` gains a
  declared build contract with a normalised result schema.
- **Acceptance:** a bring-up against a real CMSIS-DAP probe completes
  flash → verify → (optionally) GDB attach and emits an evidence record with
  the firmware hash; a Unity/CMock test suite runs headless in CI and its
  coverage is ingested by `coverage-ingestor`; the Zephyr workspace resolves
  from a clean checkout to a pinned module set with no network drift.

### M3 — Automotive diagnostics closed loop (16 candidates)

*Replaces the placeholder dependency with real, maintainable tooling and
completes the generate → execute → evidence loop.*

- **Scope:** AUTOSAR/ARXML, ODX, UDS, DoIP, CAN/LIN, SOME/IP, measurement.
- **Key tools:** odxtools, autosar-data-py, py-armodel, cogu/autosar,
  udsoncan, python-can, can-isotp, doipclient, canmatrix, cantools, ldfparser,
  FibexConverter, vSomeIP, Robot Framework, RobotFramework-UDS, pyserial,
  asammdf.
- **Deliverables:** `tools/diag-extract-bridge` swaps `acme-diag-extract` for
  real, versioned packs (ODX first, ARXML second), each with its own bridge
  and a stubbed contract test; `tools/diag-uds-testgen` gains an **execution**
  backend, not just generation; a new LIN pack.
- **Acceptance:** an ODX/PDX file and an ARXML file both produce a valid
  canonical UDS test-spec (`schemas/uds-test-spec.schema.json`) with recorded
  provenance (pack id/version, input hash); the generated vectors execute
  against a `vcan` virtual ECU with `udsoncan` and produce pass/fail evidence
  rows in the traceability matrix — **with no CAN hardware present**.

### M4 — Assurance, forensics and formal verification (52 candidates)

*The safety/security case: fuzzing, binary analysis, formal proofs, hardening
attestation, traceability of findings back to requirements.*

- **Scope:** fuzzing, binary analysis, fault injection, emulation, hardening,
  policy packs for safety/security standards, threat modelling support.
- **Key tools:** Fuzzware, AFL++, honggfuzz, libFuzzer, OSS-Fuzz/CIFuzz,
  boofuzz, unicorn, syzkaller, Ghidra, angr, Rizin, FLOSS, Binwalk, Trivy,
  Scancode, ORT, Scorecard, GUAC, Renode, QEMU, simavr, OPA packs, CBMC,
  Coccinelle, OpenSCAP, IWYU, autocheck, naivesystems/analyze,
  codeql-coding-standards, clang-tidy-automotive, mcuboot/TF-M/TF-A, mbed-tls,
  OpenThread, asammdf, pymodbus, pyvisa, RsInstrument, sigrok, ROS 2,
  micro-ROS, Nav2, Gazebo, SUMO, perf, perfetto, bpftrace, gprof, scalene,
  HDiffPatch.
- **Acceptance:** a firmware image is fuzzed (Fuzzware on Cortex-M, or AFL++
  in unicorn mode) and a reproducible crash is turned into a defect artifact
  with a stack trace; the same image is triaged headlessly (angr or Ghidra
  `analyzeHeadless`) and its hardening flags are attested (checksec) into the
  evidence ledger; the SBOM of the image (syft) resolves to a CVE match
  (grype/osv-scanner) with a recorded false-positive decision.

### M5 — Governance, provenance and the long tail (32 candidates)

*The platform becomes self-hosting: it can prove where its own artifacts came
from, and it can host the rest of the ecosystem.*

- **Scope:** reproducible builds, build provenance, self-hosted CI, SysML/MBSE
  sources, MBD co-simulation, FPGA/EDA, additional standards profiles, vector
  retrieval for agent context.
- **Key tools:** nix, bazel, in-toto, slsa-verifier, gitea, woodpecker,
  compliance-trestle, fret, oslc-client, structurizr, arc42, vale, pandoc,
  zoekt, kythe, sqlite-vec, lancedb, openmodelica, fmpy, python-control, ns-3,
  yosys, litex, amaranth, kicad, klayout, openroad, vehicle-signal-specification.
- **Acceptance:** a released firmware artifact carries a verifiable SLSA
  provenance attestation (`in-toto` → `slsa-verifier`); the same artifact can
  be rebuilt bit-identically in a hermetic environment (nix); Axiom's own
  repository passes a supply-chain audit with the same tools it ships
  (syft + grype + osv-scanner + scorecard).

### Milestone dependency view

```
M0 survey
 ├── M1 evidence backbone ──┬── M4 assurance & forensics
 │                          └── M5 governance (needs M1 evidence model)
 ├── M2 target access ──────┬── M3 automotive diagnostics closed loop
 │                          └── M4 (fuzzing needs a build + a target)
 └── M3 ──────────────────────► M4 (UDS execution feeds the security case)
```

---

## 5. Policies that constrain every milestone

### 5.1 Standards metadata is not normative text

AxiomEmbedded's existing rule — *keep standards metadata and applicability
separate from proprietary normative text* — is the single most important
constraint on this plan, because most of the relevant tools (cppcheck,
CodeQL, autocheck, naivesystems) **want** the rule text and will happily
vendor it.

The pattern that works:

| Store in the repo | Never store in the repo |
| --- | --- |
| `standard_id`, `edition`, `clause_id` | The licensed prose of the clause |
| `applicability_predicate` (machine-checkable) | Tool catalogues that embed standard checklists |
| `project_interpretation` (project-authored) | CIS/OpenSCAP benchmark content |
| `evidence_refs`, `status`, `deviation_record` | Third-party requirement text imported verbatim |

Consequences:

- MISRA/CERT checkers report **rule identifiers**. The user supplies the
  licensed text at run time; it is never committed.
- Applicability is expressed as **data**, not prose — OPA/Rego policies over
  `{standard_id, clause_id, applies_to}` — so enforcement is machine-checkable
  without the standard text ever entering the tree.
- A compliance artifact is validated against an **OSCAL profile**
  (Compliance Trestle) — a profile is a *subset of control IDs* plus
  project-authored tailoring remarks, by design.
- No adapter may claim certification or standards compliance from a heuristic
  check. The adapter reports findings; the human gate decides.

### 5.2 Licence policy

| Licence class | Permitted linkage | Notes |
| --- | --- | --- |
| MIT / Apache-2.0 / BSD / ISC | import or subprocess | Default. |
| LGPL / MPL / EPL | import (record the licence) | Python-exception caveats for LGPL in pip deps. |
| **GPL / AGPL** | **subprocess only** | Never linked into Axiom packages or bridge modules. AGPL additionally triggers source-offer obligations if the adapter is exposed as a network service. |

The validator enforces the strong-copyleft rule mechanically: a candidate
whose `license` contains `gpl`/`agpl` and whose `linkage` is `import` fails
`python scripts/validate_tool_candidates.py`.

Where a permissive alternative exists, prefer it: `gcovr` over LCOV
(PyPI `lcov` is an unrelated Python port — a name-collision trap),
`osv-scanner` over `cve-search` (AGPL + MongoDB), `angr` over most binary
tooling, `syft` over `tern` (Docker-only), `opencv` over `safety` (paid
auth in v3).

### 5.3 Adapter contract

Every adapter, regardless of channel:

1. **fails closed** with an actionable message when the tool is missing
   (`pip install X` / `apt install X` / `docker pull X`);
2. **never parses** a format the upstream tool owns — validate shape only;
3. **records provenance** (upstream id/version, input hash) in its output;
4. **is covered** by a deterministic test that stubs the upstream tool, so CI
   never needs the real toolchain;
5. **normalises output** into a single Axiom evidence shape, so a reviewer
   does not have to know which of twenty tools produced a row.

---

## 6. Known traps

- **Name-collision traps.** PyPI `lcov` is an unrelated Python port; PyPI
  `uds` is an UrbanDictionary CLI; PyPI `isoparser` is an ISO 9660 parser;
  the OBD package is `obd`, not `python-obd`.
- **Repossessed projects.** `danmar/cppcheck` → `cppcheck-opensource/cppcheck`;
  `intel/cve-bin-tool` → `ossf/cve-bin-tool`;
  `jeremylong/DependencyCheck` → `dependency-check/DependencyCheck`;
  `lcovgeninfo/lcov` → `linux-test-project/lcov`;
  `jdufresne/pip-licenses` → `raimon49/pip-licenses`;
  `bminor/binutils-gdb` was **removed in 2026** → `gnutools/binutils-gdb`.
- **Empty GitHub stubs.** `graphviz/graphviz` and `openocd/openocd` are
  hollow, archived mirrors — the real repositories are on GitLab. Some
  projects (Antora, Eclipse Papyrus, cmocka, dfu-util, stm32flash, avrdude)
  have **no GitHub home**; the manifest must carry the correct upstream URL.
- **GUI-only tools are not adapters.** SavvyCAN, CANgaroo, CANtrip, BUSMASTER,
  TSMaster, Capella, Papyrus, Modelio and draw.io are excellent *tools* but
  cannot be invoked headlessly by an agent.
- **Non-existent projects.** `autosar-compliance-checker`, `CANtastic` (as an
  analyser), `ICsee`, `OpenFlightStack`, `mercedes-benz/ipcexamples` and
  `mercedes-benz/pyxdd` do not exist as claimed — do not plan around them.
- **CodeQL's CLI is not free for closed-source code.** The queries are MIT;
  the CLI is separately licensed. Axiom must have a separate clang-tidy-based
  MISRA path for customer code.
- **A claim in a manifest is not a capability.** Every adapter that moves
  from `candidate` to `accepted` must have shipped code, a stubbed contract
  test, and a demonstrated evidence row. The registry is a proposal, not a
  promise.

---

## 7. How to use this today

```bash
# What open-source tools could serve this project?
axiom tools --domain automotive --platform mcu --standard "ISO 14229-1"

# Narrow by capability.
axiom tools --category diagnostics
axiom tools --category static-analysis --platform mcu

# Audit view: include reference and rejected entries.
axiom tools --include-informational

# Which of them are a one-line pip install?
axiom tools --domain automotive | jq '.by_channel'

# Validate the registry contract.
python scripts/validate_tool_candidates.py
```

From an agent (MCP):

```json
{"tool": "tool_candidates", "arguments": {"domain": "automotive", "platform": "mcu"}}
```

From Python:

```python
from packages import axiom_sdk
sel = axiom_sdk.list_tool_candidates("automotive", "mcu", ["ISO 14229-1"])
sel["candidates"], sel["by_channel"], sel["by_milestone"]
```

---

## 8. Next action

M0 is complete and machine-validated. The next concrete step is **M1**:
replace the placeholder adapters `static-analysis-aggregator`,
`coverage-ingestor` and `dependency-analyzer` with real implementations
backed by clang-tidy/reviewdog, gcovr and syft/grype/osv-scanner
respectively, each with a stubbed contract test, and express MISRA/CERT
applicability as an OPA policy over `{standard_id, clause_id, applies_to}`
rather than as vendored rule text.

Per `AGENTS.md`, a change is not complete until verification and evidence
artifacts are updated, and safety-/security-critical changes stop at the
configured approval gate. M1 changes the evidence model, so it needs an
impact assessment and a human gate before merge.
