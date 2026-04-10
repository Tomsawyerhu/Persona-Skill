# Pipeline

This skill is a direct-reading persona distillation workflow, not a candidate-mining pipeline.

## Stages

1. `scaffold`
   Create a workspace and rich dimension template.

2. `corpus reading`
   Traverse the source directory directly and read representative source files.

3. `source selection`
   Decide which files truly anchor the persona and record them in `source_index`.

4. `evidence extraction`
   Add concrete excerpts or tight paraphrases to `evidence_index`.

5. `dimension synthesis`
   Fill supported dimensions, prune or down-rank unsupported ones, and preserve contradiction or period drift.

6. `voice and scenarios`
   Build `voice_model` and `scenario_library` from the same evidence base.

7. `validation`
   Check referential integrity, empty content, unsupported claims, and final completeness.

8. `module packaging`
   Slice the full artifact into runtime modules and load profiles only after the persona is substantively complete.

9. `runtime confirmation`
   Refresh the catalog and confirm the persona is router-ready.

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

## Anti-Pattern

The following is not a valid completion path:

1. scaffold
2. stop
3. ask the user to continue later

That outcome is only acceptable when there is a real blocker that prevents completion in the current turn.
