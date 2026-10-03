# Plugin model

Every extension should declare:

- stable id/version
- capabilities
- dependencies
- inputs/outputs
- permissions
- supported domains/platforms
- verification expectations
- evidence hooks

Core packages must not import domain plugins directly.
