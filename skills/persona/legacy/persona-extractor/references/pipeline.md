# Pipeline

This skill is designed as a small extraction system, not a one-off prompt.

## Stages

1. `scaffold`
   Create a workspace for one persona.

2. `scope`
   Define corpus boundaries and known blind spots.

3. `index`
   Normalize sources into source-level and passage-level inventories.

4. `candidate mining`
   Use dimension-specific seed terms and questions to pull likely evidence.

5. `synthesis`
   Write dimension summaries, tensions, voice model, and scenario library.

6. `module packaging`
   Slice the full artifact into runtime modules and define scene-aware load profiles.

7. `validation`
   Check referential integrity, missing fields, empty dimensions, and unsupported claims.

8. `render`
   Export review-friendly markdown mirrors.

## Why This Structure Exists

- Large corpora are too noisy for direct freeform summarization.
- Evidence must be reusable across extraction and roleplay.
- Full artifacts are too large to load on every invocation, so runtime modules must be precomputed.
- Persona artifacts should survive model changes and new downstream consumers.
- Validation catches low-grade failures that are otherwise easy to miss:
  - dangling evidence refs
  - weak scenario grounding
  - empty dimensions
  - hidden source gaps

## Working Principle

The pipeline should remain generic:

- no person-specific dimensions
- no ideology-specific assumptions
- no public-figure-only framing
- no roleplay-only schema

The same workflow should work for:

- political figures
- founders
- artists
- scientists
- fictional characters with source canon
- interview subjects
- memoir-based private individuals
