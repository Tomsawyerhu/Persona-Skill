#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


BALANCED_DIMENSIONS: List[Dict[str, Any]] = [
    {
        "id": "core_identity",
        "label": "Core Identity",
        "category": "identity",
        "questions": [
            "How does this person define who they are?",
            "What role do they believe they occupy?"
        ],
        "seed_terms": []
    },
    {
        "id": "motivations",
        "label": "Motivations",
        "category": "motivation",
        "questions": [
            "What does this person repeatedly pursue or protect?",
            "What do they avoid, fear, or reject?"
        ],
        "seed_terms": []
    },
    {
        "id": "world_model",
        "label": "World Model",
        "category": "cognition",
        "questions": [
            "How do they think the world works?",
            "What causal model do they rely on?"
        ],
        "seed_terms": []
    },
    {
        "id": "decision_making",
        "label": "Decision Making",
        "category": "cognition",
        "questions": [
            "How do they decide under tradeoffs?",
            "Do they move quickly, cautiously, intuitively, analytically?"
        ],
        "seed_terms": []
    },
    {
        "id": "learning_and_adaptation",
        "label": "Learning And Adaptation",
        "category": "cognition",
        "questions": [
            "How do they respond to contradiction, criticism, and novelty?"
        ],
        "seed_terms": []
    },
    {
        "id": "relationship_model",
        "label": "Relationship Model",
        "category": "social",
        "questions": [
            "How do they build trust, distance, loyalty, and intimacy?"
        ],
        "seed_terms": []
    },
    {
        "id": "conflict_style",
        "label": "Conflict Style",
        "category": "social",
        "questions": [
            "How do they fight, negotiate, punish, forgive, or de-escalate?"
        ],
        "seed_terms": []
    },
    {
        "id": "communication_style",
        "label": "Communication Style",
        "category": "expression",
        "questions": [
            "How do they sound?",
            "What do they optimize for when speaking or writing?"
        ],
        "seed_terms": []
    },
    {
        "id": "emotional_register",
        "label": "Emotional Register",
        "category": "expression",
        "questions": [
            "What emotional surface recurs in the corpus?"
        ],
        "seed_terms": []
    },
    {
        "id": "contradictions_and_shadow",
        "label": "Contradictions And Shadow",
        "category": "integration",
        "questions": [
            "Where does the persona become inconsistent, brittle, blind, or split?"
        ],
        "seed_terms": []
    }
]


SCENARIO_AXES = [
    "receiving criticism",
    "making a difficult decision",
    "handling failure",
    "dealing with disagreement",
    "explaining their beliefs",
    "responding to uncertainty",
    "modern-topic extrapolation"
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold a generic persona extraction workspace.")
    parser.add_argument("--output-dir", required=True, help="Directory to create or update.")
    parser.add_argument("--persona-id", required=True, help="Stable slug for the persona.")
    parser.add_argument("--display-name", required=True, help="Human-readable name.")
    return parser.parse_args()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_config(persona_id: str, display_name: str) -> Dict[str, Any]:
    return {
        "persona_id": persona_id,
        "display_name": display_name,
        "corpus_root": "",
        "source_types": [],
        "time_span": "",
        "inclusion_notes": [],
        "exclusion_notes": [],
        "known_blind_spots": [],
        "dimensions": BALANCED_DIMENSIONS,
        "scenario_axes": SCENARIO_AXES
    }


def build_template(persona_id: str, display_name: str) -> Dict[str, Any]:
    return {
        "schema_version": "2.1",
        "persona_id": persona_id,
        "display_name": display_name,
        "artifact_meta": {
            "created_by": "persona-extractor scaffold",
            "created_from": "",
            "last_updated": "",
            "status": "template"
        },
        "source_scope": {
            "corpus_root": "",
            "source_types": [],
            "time_span": "",
            "inclusion_notes": [],
            "exclusion_notes": [],
            "known_blind_spots": []
        },
        "summary": {
            "one_liner": "",
            "core_thesis": "",
            "confidence_notes": ""
        },
        "source_index": [],
        "evidence_index": [],
        "dimensions": [
            {
                "id": item["id"],
                "label": item["label"],
                "category": item["category"],
                "priority": "high",
                "definition": "",
                "extraction_questions": item["questions"],
                "synthesis": {
                    "summary": "",
                    "patterns": [],
                    "anti_patterns": [],
                    "tensions": [],
                    "drift": []
                },
                "evidence_refs": [],
                "confidence": "low"
            }
            for item in BALANCED_DIMENSIONS
        ],
        "voice_model": {
            "register": [],
            "cadence": [],
            "lexical_features": [],
            "rhetorical_moves": [],
            "response_defaults": [],
            "avoid": []
        },
        "scenario_library": [],
        "simulation_contract": {
            "identity_frame": "",
            "grounding_order": [],
            "truthfulness_policy": "",
            "uncertainty_policy": "",
            "modern_topic_policy": "",
            "citation_policy": "",
            "stay_in_character_policy": "",
            "identity_answer_policy": "",
            "persistence_policy": "",
            "exit_policy": ""
        },
        "module_registry": [],
        "load_profiles": [],
        "open_questions": []
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir.joinpath("extractor_config.json"), build_config(args.persona_id, args.display_name))
    write_json(output_dir.joinpath("persona.template.json"), build_template(args.persona_id, args.display_name))
    output_dir.joinpath("notes.md").write_text(
        "\n".join(
            [
                "# Extraction Notes",
                "",
                "Use this folder as the working directory for one persona.",
                "",
                "Recommended order:",
                "",
                "1. Fill extractor_config.json",
                "2. Run persona_evidence_builder.py",
                "3. Draft persona.json from persona.template.json",
                "4. Validate with validate_persona.py",
                "5. Render markdown mirrors",
                "",
                "Keep evidence ids stable once the artifact is in use.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
