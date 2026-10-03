# Build-System skill

Reproducible, hermetic, warning-free builds for firmware and embedded Linux:
CMake discipline, toolchain management, dependency pinning, CI integration,
and artifact provenance from source to flashable image.

## 1. Purpose and scope

**Purpose.** Any engineer, on any machine, reproduces the identical binary
from the same source revision — with zero warnings, pinned tools, and traced
artifacts.

**In scope.** CMake project structure (3.20+ floor), presets and toolchains,
cross-compilation files, compiler flag policy, dependency management
(FetchContent/submodules with pins), ccache/sccache acceleration, CI build
matrices (gcc + clang, all target arches), SBOM/provenance generation, and
build-performance budgets.

**Non-goals.** Yocto distribution builds (see `embedded-linux` §3) and release
signing ceremonies (see `release`). Ends at verified build artifacts with
provenance.

## 2. Normative sources (verified Phase 2, high confidence)

| # | Standard | Version / status | Clause / scope | Source |
|---|----------|------------------|----------------|--------|
| 1 | CMake | 3.20 minimum floor (project policy) | Presets, toolchain files, cross-compilation model | `https://cmake.org/cmake/help/latest/` |
| 2 | LLVM/Clang | Current stable | Second compiler for warnings parity and static analysis | `https://clang.llvm.org/` |
| 3 | SLSA provenance | v1.0 (2023) | Build provenance levels for supply-chain integrity | `https://slsa.dev/spec/v1.0/levels` |
| 4 | SPDX SBOM | ISO/IEC 5962:2021 | Artifact inventory format | `https://spdx.dev/` |

## 3. Build rules

1. **Warnings are errors.** `-Wall -Wextra -Werror` on gcc and clang for all
   targets including tests and examples (per `configs/skill-update.yaml`); a
   warning introduced is a build failure, not a message.
2. **Pinned everything.** CMake minimum, compiler versions, FetchContent
   tags/SHAs, and container images pinned; floating `main` dependencies are
   blocking findings. `cmake --preset` configures from clean state without
   manual steps.
3. **Target separation.** One toolchain file per target triple; host tools and
   target firmware never share a build directory. Cross-compiling silently
   with the host compiler is the classic build defect — the toolchain file
   asserts the compiler on configure.
4. **Artifact provenance.** Every release artifact records source revision,
   toolchain versions, build flags, and SBOM; SLSA-style provenance attached
   where the release process (see `release`) requires it.
5. **Build performance budgeted.** Full clean build and incremental
   null-build times tracked in CI with tripwires; ccache configured but never
   required for correctness.

## 4. Release gates (blocking)

1. Clean-configure build passes on gcc + clang with zero warnings.
2. All target architectures build from the same source revision.
3. Dependency pins verified (no floating refs); SBOM generated.
4. Reproducibility spot-check: two builders, bit-identical artifacts (or
   documented nondeterminism with cause).

## 5. Verification of this skill (Phase 4 gate)

- Standards carry number + version + clause + URL (§2).
