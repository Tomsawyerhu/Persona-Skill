# Distill Execution Prompt

Use this prompt internally whenever the user runs:

- `/persona distill <persona_name> <data_dir>`

## Mission

You are not initializing a workspace.
You are completing a full persona distillation in this turn.

Your job is to produce a usable final persona artifact from the supplied corpus directory.

## Non-Negotiable Rules

1. Do not stop at bootstrap.
2. Do not present “next steps” as the outcome unless blocked.
3. Do not leave `persona.json` as a mostly empty template.
4. Do not treat a `bootstrapped` or unvalidated artifact as success.
5. Do not rely on heuristic candidate search packs or keyword-hit files.
6. Use the dimension template as a checklist, then prune or down-rank unsupported dimensions.
7. Every important claim in the persona should be anchored in real source reading.
8. Remain in execution mode until the persona reaches `final` or a concrete blocker is proven.
9. Do not require the user to send another “continue distill” message.

## Required Execution Sequence

1. Bootstrap the persona workspace if needed.
2. Traverse the corpus directory directly.
3. Read enough representative source files to support detailed modeling.
4. Select and refine the dimension set.
5. Populate `source_index` with the actual sources used.
6. Populate `evidence_index` with concrete excerpts or tight paraphrases.
7. Fill dimension synthesis sections with source-grounded content.
8. Fill `voice_model`.
9. Fill `scenario_library`.
10. Run final validation.
11. Fix deficiencies until validation passes.
12. Build runtime modules.
13. Refresh the catalog.
14. Confirm the persona is router-ready.

## Required Working Style

- Read the corpus directly from the filesystem.
- Use the scaffold only as a starting point.
- Make multiple passes over the sources when needed: source selection, evidence extraction, dimension synthesis, and scenario writing.
- Prefer fewer strong claims with evidence over many generic claims.
- Use validation failures as a to-do list and fix them in the same turn.

## Forbidden Responses

Do not end `/persona distill` with a response whose main content is:

- “bootstrap ready”
- “workspace prepared”
- “next steps”
- “manual synthesis still required”
- “continue distill in another turn”

Those are only acceptable if there is a real blocker that prevents completion now.

## Minimum Done Definition

Do not stop until all are true:

- `artifact_meta.status` is `final`
- `source_index` is non-empty
- `evidence_index` is non-empty
- dimensions contain real synthesis text
- `scenario_library` is populated
- `validate_persona.py --mode final` passes
- runtime modules exist
- the catalog marks the persona as router-ready

## Allowed Blocker

You may stop only if there is a concrete blocker that cannot be solved in the current turn, such as:

- the corpus directory is missing or unreadable
- the sources are too incomplete to satisfy the contract
- an unrecoverable schema or tool failure prevents writing a valid final artifact

If blocked, report:

- the exact blocker
- the exact file or command involved
- what was attempted
- what remains unfinished

## Final Self-Check

Before you stop, verify all of these:

- `artifact_meta.status == "final"`
- `validate_persona.py --mode final` passes
- catalog says `router_ready: true`
- `switch` no longer fails for status-related reasons
