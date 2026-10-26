# AI agent working agreement

AxiomEmbedded treats AI as an engineering assistant operating over structured project state.

## Golden rules

1. **Graph before grep:** identify relevant artifacts and dependencies before opening many files.
2. **Evidence before assertion:** distinguish observed facts, tool output, hypothesis and recommendation.
3. **Minimal context:** load only what the task requires.
4. **Minimal diff:** change the smallest surface that satisfies the task.
5. **Verification is part of the change:** add or update tests and evidence.
6. **Domain overlays must not leak into core:** keep automotive/aerospace/etc. policies composable.
7. **Human gates remain explicit:** sensitive actions are not auto-approved because an agent is confident.
