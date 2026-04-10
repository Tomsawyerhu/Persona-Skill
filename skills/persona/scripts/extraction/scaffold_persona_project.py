#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_DIMENSIONS: List[Dict[str, Any]] = [
    {
        "id": "core_identity",
        "label": "Core Identity",
        "category": "identity",
        "priority": "high",
        "definition": "How this person defines who they are, what role they occupy, and what kind of person they believe themselves to be.",
        "questions": [
            "How does this person name or frame themselves?",
            "What recurring role or duty do they believe they embody?",
            "What kind of person do they explicitly try to be, or refuse to be?"
        ],
    },
    {
        "id": "life_project",
        "label": "Life Project",
        "category": "identity",
        "priority": "high",
        "definition": "The major long-range aim, mission, or historical arc that appears to organize this person's choices.",
        "questions": [
            "What long-term project or mission organizes their life?",
            "What future do they think they are trying to bring about?",
            "What repeated end-state or destiny appears in the corpus?"
        ],
    },
    {
        "id": "world_model",
        "label": "World Model",
        "category": "cognition",
        "priority": "high",
        "definition": "How they think the world works: causality, structure, institutions, incentives, history, order, and breakdown.",
        "questions": [
            "How do they explain how the world, society, or human affairs actually work?",
            "What causal logic do they return to when explaining success and failure?",
            "What recurring concepts organize their understanding of reality?"
        ],
    },
    {
        "id": "motivations",
        "label": "Motivations",
        "category": "motivation",
        "priority": "high",
        "definition": "What they repeatedly seek, protect, avoid, or move toward.",
        "questions": [
            "What do they repeatedly pursue, defend, or preserve?",
            "What do they fear, reject, or try to eliminate?",
            "What rewards or outcomes seem to matter most to them?"
        ],
    },
    {
        "id": "values_and_ethics",
        "label": "Values And Ethics",
        "category": "motivation",
        "priority": "high",
        "definition": "What they praise, condemn, justify, rank above other goods, or treat as morally serious.",
        "questions": [
            "What virtues or standards do they consistently praise?",
            "What do they condemn as wrong, weak, corrupt, or dishonorable?",
            "What goods do they rank above comfort, safety, or popularity?"
        ],
    },
    {
        "id": "red_lines",
        "label": "Red Lines",
        "category": "motivation",
        "priority": "medium",
        "definition": "What they consistently treat as unacceptable, disloyal, shameful, dangerous, or beneath them.",
        "questions": [
            "What actions or positions trigger a hard line from them?",
            "What do they frame as intolerable or non-negotiable?",
            "Where do they stop compromising?"
        ],
    },
    {
        "id": "decision_making",
        "label": "Decision Making",
        "category": "cognition",
        "priority": "high",
        "definition": "How they decide: speed, rigor, intuition, consultation, reversibility, sequencing, and tradeoff style.",
        "questions": [
            "How do they make choices under tradeoffs?",
            "Do they decide quickly, cautiously, analytically, opportunistically, or through principle?",
            "What patterns recur when they choose between bad options?"
        ],
    },
    {
        "id": "epistemology",
        "label": "Epistemology",
        "category": "cognition",
        "priority": "medium",
        "definition": "What they trust as evidence: direct experience, doctrine, metrics, experts, precedent, intuition, or systems.",
        "questions": [
            "What counts as proof for them?",
            "Whose testimony or what type of evidence do they trust most?",
            "How do they handle disagreement between theory and lived experience?"
        ],
    },
    {
        "id": "planning_and_execution",
        "label": "Planning And Execution",
        "category": "agency",
        "priority": "high",
        "definition": "How they turn intent into action: sequencing, patience, discipline, opportunism, iteration, and delegation.",
        "questions": [
            "How do they move from idea to action?",
            "Do they prefer long preparation, incremental iteration, or decisive action?",
            "How do they organize people, timing, and resources?"
        ],
    },
    {
        "id": "stress_and_failure",
        "label": "Stress And Failure",
        "category": "agency",
        "priority": "medium",
        "definition": "How they react when losing, blocked, overloaded, embarrassed, surprised, or facing setbacks.",
        "questions": [
            "What happens to their behavior under pressure or failure?",
            "How do they respond when plans break down or criticism lands?",
            "Do they become harder, narrower, calmer, evasive, or more adaptive?"
        ],
    },
    {
        "id": "relationship_model",
        "label": "Relationship Model",
        "category": "social",
        "priority": "high",
        "definition": "How they form trust, loyalty, intimacy, hierarchy, distance, alliance, and rivalry.",
        "questions": [
            "How do they divide people into allies, followers, rivals, and outsiders?",
            "What earns trust, loyalty, or distance from them?",
            "How do they treat hierarchy and role boundaries?"
        ],
    },
    {
        "id": "leadership_style",
        "label": "Leadership Style",
        "category": "social",
        "priority": "medium",
        "definition": "How they direct others, build authority, distribute ownership, manage dissent, and maintain alignment.",
        "questions": [
            "How do they lead or influence others?",
            "How do they handle disagreement, dissent, or drift inside a group?",
            "Do they teach, command, persuade, test, shame, inspire, or discipline?"
        ],
    },
    {
        "id": "conflict_style",
        "label": "Conflict Style",
        "category": "social",
        "priority": "high",
        "definition": "How they attack, defend, negotiate, escalate, de-escalate, punish, forgive, or reframe conflict.",
        "questions": [
            "How do they express opposition or disagreement?",
            "When challenged, do they explain, attack, redirect, absorb, or wait?",
            "How do they frame enemies, critics, or betrayers?"
        ],
    },
    {
        "id": "communication_style",
        "label": "Communication Style",
        "category": "expression",
        "priority": "high",
        "definition": "How they speak and write: directness, density, cadence, metaphor, compression, examples, and rhetorical habits.",
        "questions": [
            "What does their voice sound like on the page or in speech?",
            "Do they prefer aphorism, exposition, command, teaching, polemic, story, or interrogation?",
            "What phrases, structures, or rhetorical moves recur?"
        ],
    },
    {
        "id": "public_private_split",
        "label": "Public Private Split",
        "category": "expression",
        "priority": "medium",
        "definition": "Differences between formal voice, intimate voice, strategic voice, and self-narration.",
        "questions": [
            "Do they sound different in public statements versus intimate or tactical writing?",
            "What changes between persuasive, reflective, and operational contexts?",
            "What is hidden, softened, or sharpened depending on audience?"
        ],
    },
    {
        "id": "contradictions_and_shadow",
        "label": "Contradictions And Shadow",
        "category": "integration",
        "priority": "high",
        "definition": "Internal tensions, blind spots, hypocrisy, overreactions, compensations, or unresolved splits.",
        "questions": [
            "Where does the corpus reveal tension, contradiction, or overcorrection?",
            "What do they condemn yet also enact, or claim yet fail to sustain?",
            "What pressures reveal their shadow side?"
        ],
    },
    {
        "id": "evolution_over_time",
        "label": "Evolution Over Time",
        "category": "integration",
        "priority": "medium",
        "definition": "What changed across life stages or contexts, and what remained stable.",
        "questions": [
            "What changed over time in stance, method, tone, or priorities?",
            "What remained stable across periods, roles, or crises?",
            "What important period drift should the final persona preserve?"
        ],
    },
]


DEFAULT_SCENE_GUIDES: List[Dict[str, Any]] = [
    {
        "id": "scene_explain_beliefs",
        "scene": "Explaining their beliefs",
        "purpose": "Expose world model, values, and communication style.",
    },
    {
        "id": "scene_decision_tradeoff",
        "scene": "Making a difficult decision",
        "purpose": "Expose decision style, priorities, and red lines.",
    },
    {
        "id": "scene_receive_criticism",
        "scene": "Receiving criticism",
        "purpose": "Expose conflict style, stress response, and self-image.",
    },
    {
        "id": "scene_manage_subordinates",
        "scene": "Directing or correcting others",
        "purpose": "Expose leadership style, hierarchy logic, and communication moves.",
    },
    {
        "id": "scene_modern_extrapolation",
        "scene": "Responding to a modern topic outside the source era",
        "purpose": "Expose how synthetic extrapolation should stay consistent with the persona method.",
    },
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
        "distill_method": "agent-direct-reading",
        "corpus_root": "",
        "source_types": [],
        "time_span": "",
        "inclusion_notes": [],
        "exclusion_notes": [],
        "known_blind_spots": [],
        "recommended_dimensions": DEFAULT_DIMENSIONS,
        "recommended_scenes": DEFAULT_SCENE_GUIDES,
        "authoring_principles": [
            "Use the dimension template as a modeling scaffold, not as permission to invent content.",
            "Keep unsupported dimensions only if they are explicitly marked low confidence or prune them.",
            "Prefer direct quotes for evidence when the corpus clearly supports them.",
            "Where the corpus is thin, use narrow source-grounded synthesis rather than generic character prose.",
            "Preserve tensions, contradiction, and period drift instead of flattening them into one-note traits.",
        ],
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
                "priority": item["priority"],
                "definition": item["definition"],
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
            for item in DEFAULT_DIMENSIONS
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
            "identity_frame": f"This is a source-grounded persona simulation of {display_name} built from extracted materials, not a claim of literal presence or hidden private knowledge.",
            "grounding_order": [
                "Use direct source logic when the corpus already answers the question.",
                "Otherwise answer with source-grounded synthesis based on extracted dimensions, evidence, and scenarios.",
                "If the topic is not covered, use explicit synthetic extrapolation that stays consistent with the persona method and values."
            ],
            "truthfulness_policy": "Do not invent firsthand factual knowledge outside the corpus. When the corpus is thin, keep the answer narrow and grounded in extracted evidence or clearly marked extrapolation.",
            "uncertainty_policy": "If evidence is weak, conflicting, or period-sensitive, preserve the persona voice but acknowledge that the answer is a best-fit synthesis.",
            "modern_topic_policy": "For modern issues outside the source era, answer in character by extending the extracted reasoning style rather than pretending direct contemporary knowledge.",
            "citation_policy": "In ordinary roleplay, stay in character without footnotes. In analysis mode, you may briefly label the answer as direct-source, source-grounded synthesis, or synthetic extrapolation.",
            "default_response_language": "source-dominant",
            "language_policy": "If a /persona language override is active, answer in that language while preserving persona voice and method. Otherwise answer in the persona default language.",
            "stay_in_character_policy": f"Once persona mode begins, remain fully in character for ordinary dialogue, prefix every in-character reply with `({display_name}) `, and do not fall back to neutral assistant voice unless the user exits or explicitly requests out-of-character analysis.",
            "identity_answer_policy": f"In ordinary in-character conversation, answer in first person as {display_name} and prefix the reply with `({display_name}) `. If asked who you are, identify yourself as {display_name}. If asked whether you are literally the real person or the underlying system, answer truthfully that this is a persona-based simulation and then continue according to the user's requested mode.",
            "persistence_policy": f"Persona mode is persistent. Continue fully in character across turns until an explicit exit command or a clear out-of-character request is given, and keep the `({display_name}) ` prefix on every in-character reply.",
            "exit_policy": "Exit persona mode when the user says /persona exit, /persona off, /persona quit, 退出persona, 退出角色, or 退出skill."
        },
        "module_registry": [],
        "load_profiles": [],
        "open_questions": [
            "Which dimensions in the template are strongly supported, weakly supported, or unsupported by the corpus?",
            "What are the persona's Layer 0 non-negotiable behavior rules or method constraints?",
            "Which sources are the strongest anchors for voice, decision logic, and red lines?",
            "Where are the most important tensions, contradictions, or period shifts that should remain visible in the final persona?",
            "Which scenarios best reveal the persona under criticism, tradeoff, pressure, and modern extrapolation?"
        ]
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
                "1. Set corpus metadata in extractor_config.json",
                "2. Inspect the raw corpus directory directly",
                "3. Use the dimension template as a scaffold, then prune unsupported dimensions",
                "4. Decide evidence, voice, and scenarios from actual source reading",
                "5. Author persona.json from persona.template.json",
                "6. Validate with validate_persona.py",
                "7. Build runtime modules with build_persona_modules.py",
                "",
                "Do not generate keyword candidates or heuristic evidence packs.",
                "Use only source-grounded reading and manual synthesis.",
                "Do not leave the persona as an empty scaffold if the intent is full distillation.",
                "",
                "Keep source ids, evidence ids, and scenario ids stable once the artifact is in use.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
