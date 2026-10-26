# Product architecture

AxiomEmbedded separates six concerns:

```text
Project model
  ├─ artifacts + relationships
  ├─ profiles + rules
  ├─ workflows + gates
  ├─ tools + integrations
  ├─ context/indexing
  └─ agents + evidence
```

The product is intentionally not a single AI model and not a single embedded stack. Domain and platform overlays compose around a stable engineering core.
