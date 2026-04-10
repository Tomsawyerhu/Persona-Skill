# Output Contract

The canonical final artifact is:

- `personas/<persona_slug>/persona.json`

Recommended mirrors:

- `profile.md`
- `evidence.md`
- `qa_samples.md`

Schema version for the engineering-grade contract:

- `2.1`

## Top-Level Shape

```json
{
  "schema_version": "2.1",
  "persona_id": "slug",
  "display_name": "Display Name",
  "artifact_meta": {},
  "source_scope": {},
  "summary": {},
  "source_index": [],
  "evidence_index": [],
  "dimensions": [],
  "voice_model": {},
  "scenario_library": [],
  "simulation_contract": {},
  "module_registry": [],
  "load_profiles": [],
  "open_questions": []
}
```

## `artifact_meta`

Suggested fields:

- `created_by`
- `created_from`
- `last_updated`
- `status`
  Use one of:
  - `template`
  - `bootstrapped`
  - `draft`
  - `final`

## `source_scope`

Suggested fields:

- `corpus_root`
- `source_types`
- `time_span`
- `inclusion_notes`
- `exclusion_notes`
- `known_blind_spots`

## `summary`

Suggested fields:

- `one_liner`
- `core_thesis`
- `confidence_notes`

## `source_index`

This is a manual index of the specific source files the assistant actually relied on when authoring the persona.

Each source item:

```json
{
  "id": "src_001",
  "title": "Source Title",
  "path": "relative/path",
  "source_type": "speech",
  "date": "date string",
  "reliability": "primary",
  "notes": ""
}
```

## `evidence_index`

Each evidence item:

```json
{
  "id": "ev_001",
  "source_id": "src_001",
  "excerpt": "short quote or paraphrase",
  "kind": "quote",
  "loc": "optional local anchor",
  "tags": ["decision_making"],
  "note": "why it matters"
}
```

## `dimensions`

Each dimension:

```json
{
  "id": "decision_making",
  "label": "Decision Making",
  "category": "cognition",
  "priority": "high",
  "definition": "What this dimension is capturing",
  "extraction_questions": ["..."],
  "synthesis": {
    "summary": "one paragraph",
    "patterns": ["..."],
    "anti_patterns": ["..."],
    "tensions": ["..."],
    "drift": ["..."]
  },
  "evidence_refs": ["ev_001", "ev_007"],
  "confidence": "medium"
}
```

## `voice_model`

Suggested fields:

- `register`
- `cadence`
- `lexical_features`
- `rhetorical_moves`
- `response_defaults`
- `avoid`

## `scenario_library`

Each scenario item:

```json
{
  "id": "scene_criticism",
  "scene": "Receiving criticism",
  "scene_tags": ["conflict", "feedback"],
  "user_prompt": "How would this person react to criticism?",
  "answer_mode": "source-grounded synthesis",
  "response_style": "direct",
  "answer": "....",
  "evidence_refs": ["ev_001", "ev_009"],
  "limitations": "optional caveat"
}
```

`answer_mode`:

- `direct-source`
- `source-grounded synthesis`
- `synthetic extrapolation`

## `module_registry`

This is the runtime slicing layer used by the router skill.

Each module item:

```json
{
  "id": "mod_core",
  "label": "Core",
  "kind": "core",
  "path": "modules/mod_core.json",
  "contains": {
    "dimension_ids": ["core_identity", "motivations"],
    "scenario_ids": [],
    "includes_voice": false,
    "includes_contract": false
  },
  "tags": ["default", "identity"],
  "priority": "high"
}
```

Suggested module kinds:

- `core`
- `dimension-group`
- `voice`
- `scenario-group`
- `contract`

## `load_profiles`

Load profiles describe which modules should be loaded in different invocation contexts.

Each load profile:

```json
{
  "id": "default_chat",
  "label": "Default Chat",
  "description": "General in-character dialogue",
  "scene_tags": ["default", "chat"],
  "module_refs": ["mod_core", "mod_social", "mod_voice", "mod_contract"],
  "default": true
}
```

## `simulation_contract`

Suggested fields:

- `identity_frame`
- `grounding_order`
- `truthfulness_policy`
- `uncertainty_policy`
- `modern_topic_policy`
- `citation_policy`
- `default_response_language`
- `language_policy`
- `stay_in_character_policy`
- `identity_answer_policy`
- `persistence_policy`
- `exit_policy`

## Validation Rules

In `final` mode:

- `schema_version` must be `2.1`
- `persona_id` and `display_name` are required
- `source_index` ids must be unique
- `evidence_index` ids must be unique
- `source_index` should contain the specific sources actually used and should not be empty
- `evidence_index` should not be empty
- every `source_id` in `evidence_index` must exist
- every `evidence_ref` in dimensions and scenarios must exist
- every `module_ref` in `load_profiles` must exist
- dimensions should usually be `8-12`
- every dimension should have at least `2` evidence refs unless explicitly marked low confidence
- scenario library should usually contain at least `5` items

In `template` mode:

- referential integrity may be incomplete
- placeholder text is allowed
- empty arrays are allowed
