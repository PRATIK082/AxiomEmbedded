# Brownfield onboarding

For an existing product:

```bash
python -m axiom_cli analyze path/to/product
python -m axiom_cli context select --index path/to/product/.axiom/index.json --root src/main.c
```

Then recover architecture, tests, requirements and change impact before making a broad change.
