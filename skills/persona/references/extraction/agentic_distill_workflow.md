# Agentic Distill Workflow

Use this workflow for `/persona distill`.

This workflow is mandatory, not advisory.

## Principle

The persona should be extracted by the assistant reading the source corpus directly.
The `/persona distill` command should be treated as one end-to-end workflow, not as a bootstrap-only command.

## Required Workflow

1. Scaffold the persona workspace.
2. Inspect the raw source directory directly.
3. Read representative files or passages from the corpus.
4. Decide which dimensions are actually supported by the corpus.
5. Write `persona.json` from source-grounded interpretation.
6. Add `source_index` and `evidence_index` manually for the sources actually used.
7. Validate, build modules, and refresh the catalog.
8. Return only after the persona is router-ready or a concrete blocker has been reported.

Never stop after step 1 and call the result a completed distill.

## Completion Standard

Do not treat distillation as complete if the artifact is still mostly template content.

At minimum, a completed distill should have:

- a non-empty `source_index`
- a non-empty `evidence_index`
- multiple filled dimensions with real synthesis text
- a populated `scenario_library`
- successful final validation
- runtime modules and load profiles built

## Direct Reading Guidance

Prefer:

- opening the source files themselves
- traversing the corpus directory yourself
- sampling across the corpus rather than overfitting to a few quoted lines
- selecting dimensions that match the material
- preserving tensions, ambiguity, and period drift

Avoid:

- generating keyword candidate packs or search hit lists as pseudo-evidence
- trusting frequency or lexical overlap alone as meaning
- forcing every persona into the same dimension emphasis
- copying generic scaffolding language into the final persona
- stopping after scaffold creation and calling that a finished distill
