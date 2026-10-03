# Applying the AxiomEmbedded upgrade to `PRATIK082/AxiomEmbedded`

The supplied upgrade bundle is a complete repository tree. Because remote GitHub write operations are not exposed in this execution, apply it locally with a normal Git workflow or an AI coding agent.

## Safe replacement workflow

```bash
git clone https://github.com/PRATIK082/AxiomEmbedded.git
cd AxiomEmbedded
git checkout -b chore/axiom-platform-upgrade
```

Copy the contents of the `AxiomEmbedded/` bundle over the checkout while preserving any local work you explicitly need.

Then:

```bash
python -m pip install -e '.[test]'
python -m axiom_cli doctor
python -m pytest -q
git status --short
git diff --stat
```

Create a reviewed commit only after inspecting the diff. Push the branch and open a PR through your normal GitHub workflow.

## AI-agent update command

Use this request with Copilot CLI, OpenCode or another coding agent after the branch is prepared:

```text
Upgrade this repository to the AxiomEmbedded 0.1 architecture using the existing tree as the source of truth. Do not vendor the AxiomEmbedded  legacy tree; migration is supported from an external source. Do not duplicate concepts. Validate AGENTS.md, schemas, registries, profiles, workflows, agent manifests, Copilot instructions and opencode.json. Run the full test/validation suite, show the diff, and stop before git push.
```
