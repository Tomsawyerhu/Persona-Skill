# Quality Rubric

Use this rubric before calling a persona artifact done.

## 1. Grounding

- Major claims trace to evidence ids.
- Evidence comes from real sources, not memory alone.
- Primary and secondary sources are not silently mixed.

## 2. Behavioral Specificity

- The artifact explains how the person thinks and acts.
- Traits are operational, not decorative.
- Scenario answers feel derived from the dimensions.

## 3. Generality

- The artifact is not overfit to one downstream use case.
- Another consumer could use the same JSON for analysis, evaluation, or simulation.
- Nothing in the schema assumes politics, leadership, or celebrity.

## 4. Contradiction Handling

- Tensions are preserved rather than averaged away.
- Time drift is recorded when important.
- Unknowns remain explicit.

## 5. Voice Fidelity

- The voice model captures structure, not just catchphrases.
- The simulator can sound like the person without parroting famous lines.

## 6. Engineering Hygiene

- ids are stable
- references resolve
- paths are real
- markdown mirrors render cleanly
- validators pass
- runtime modules are coherent and not arbitrarily sliced
- load profiles are scene-appropriate and avoid loading the whole persona by default
