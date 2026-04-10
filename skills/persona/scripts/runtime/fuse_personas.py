#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

SHARED_DIR = Path(__file__).resolve().parent.parent / "shared"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

from persona_paths import load_json, resolve_persona

DEFAULT_PERSONAS_DIR = Path(__file__).resolve().parents[2] / "store" / "personas"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fuse 2-3 existing personas into a new router-ready persona artifact.")
    parser.add_argument("new_persona_id", help="New fused persona id")
    parser.add_argument("source_personas", nargs="+", help="2-3 existing persona ids or display names")
    parser.add_argument("--personas-dir", default=str(DEFAULT_PERSONAS_DIR), help="Personas root directory")
    parser.add_argument("--display-name", default="", help="Optional display name for the fused persona")
    return parser.parse_args()

def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def unique_list(values: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def dominant_language(sources: List[Dict[str, Any]]) -> str:
    values = [
        src.get("simulation_contract", {}).get("default_response_language", "").strip()
        for src in sources
        if src.get("simulation_contract", {}).get("default_response_language", "").strip()
    ]
    if not values:
        return "source-dominant"
    return Counter(values).most_common(1)[0][0]


def main() -> None:
    args = parse_args()
    personas_dir = Path(args.personas_dir).resolve()

    if len(args.source_personas) < 2:
        raise SystemExit("fuse requires at least 2 source personas")
    if len(args.source_personas) > 3:
        raise SystemExit("fuse supports at most 3 source personas by default; more than 3 is not guaranteed")
    if len(set(args.source_personas)) != len(args.source_personas):
        raise SystemExit("fuse source personas must be unique")
    if args.new_persona_id in set(args.source_personas):
        raise SystemExit("new fused persona name must differ from all source persona names")

    sources = [load_json(resolve_persona(name, personas_dir)) for name in args.source_personas]
    for source_name, src in zip(args.source_personas, sources):
        status = src.get("artifact_meta", {}).get("status", "")
        if status != "final":
            raise SystemExit(
                f"fuse source persona is not final: {source_name} (status: {status or 'unknown'})"
            )
    output_dir = personas_dir / args.new_persona_id
    output_dir.mkdir(parents=True, exist_ok=True)

    source_prefixes = [src.get("persona_id", f"src{i+1}") for i, src in enumerate(sources)]

    combined_source_index: List[Dict[str, Any]] = []
    combined_evidence_index: List[Dict[str, Any]] = []
    source_id_map: Dict[str, str] = {}
    evidence_id_map: Dict[str, str] = {}

    for prefix, src in zip(source_prefixes, sources):
        for item in src.get("source_index", []):
            new_id = f"{prefix}__{item['id']}"
            source_id_map[f"{prefix}:{item['id']}"] = new_id
            copied = dict(item)
            copied["id"] = new_id
            combined_source_index.append(copied)
        for ev in src.get("evidence_index", []):
            new_id = f"{prefix}__{ev['id']}"
            evidence_id_map[f"{prefix}:{ev['id']}"] = new_id
            copied = dict(ev)
            copied["id"] = new_id
            copied["source_id"] = source_id_map.get(f"{prefix}:{ev['source_id']}", ev["source_id"])
            copied["tags"] = unique_list([prefix, *copied.get("tags", [])])
            combined_evidence_index.append(copied)

    dimension_map: Dict[str, Dict[str, Any]] = {}
    for prefix, src in zip(source_prefixes, sources):
        for dim in src.get("dimensions", []):
            dim_id = dim["id"]
            entry = dimension_map.setdefault(
                dim_id,
                {
                    "id": dim_id,
                    "label": dim.get("label", dim_id),
                    "category": dim.get("category", "other"),
                    "priority": dim.get("priority", "medium"),
                    "definition": dim.get("definition", ""),
                    "extraction_questions": unique_list(dim.get("extraction_questions", [])),
                    "synthesis": {
                        "summary": "",
                        "patterns": [],
                        "anti_patterns": [],
                        "tensions": [],
                        "drift": [],
                    },
                    "evidence_refs": [],
                    "confidence": "medium",
                },
            )
            summary = dim.get("synthesis", {}).get("summary", "")
            if summary:
                entry["synthesis"]["drift"].append(f"[{prefix}] {summary}")
            entry["synthesis"]["patterns"].extend([f"[{prefix}] {x}" for x in dim.get("synthesis", {}).get("patterns", [])])
            entry["synthesis"]["anti_patterns"].extend([f"[{prefix}] {x}" for x in dim.get("synthesis", {}).get("anti_patterns", [])])
            entry["synthesis"]["tensions"].extend([f"[{prefix}] {x}" for x in dim.get("synthesis", {}).get("tensions", [])])
            entry["synthesis"]["drift"].extend([f"[{prefix}] {x}" for x in dim.get("synthesis", {}).get("drift", [])])
            entry["evidence_refs"].extend([evidence_id_map.get(f"{prefix}:{ref}", ref) for ref in dim.get("evidence_refs", [])])

    dimensions = list(dimension_map.values())
    for dim in dimensions:
        parts = dim["synthesis"]["drift"][:3]
        dim["synthesis"]["summary"] = " | ".join(parts) if parts else "Fused draft dimension; refine manually."
        dim["synthesis"]["patterns"] = unique_list(dim["synthesis"]["patterns"])
        dim["synthesis"]["anti_patterns"] = unique_list(dim["synthesis"]["anti_patterns"])
        dim["synthesis"]["tensions"] = unique_list(dim["synthesis"]["tensions"])
        dim["synthesis"]["drift"] = unique_list(dim["synthesis"]["drift"])
        dim["evidence_refs"] = unique_list(dim["evidence_refs"])
        dim["confidence"] = "medium"

    scenario_library: List[Dict[str, Any]] = []
    for prefix, src in zip(source_prefixes, sources):
        for scene in src.get("scenario_library", []):
            copied = dict(scene)
            copied["id"] = f"{prefix}__{scene['id']}"
            copied["scene"] = f"[{prefix}] {scene['scene']}"
            if copied.get("answer_mode") != "synthetic extrapolation":
                copied["answer_mode"] = "source-grounded synthesis"
            copied["limitations"] = (
                (copied.get("limitations", "") + " ").strip()
                + f"Fused from source persona `{prefix}`."
            ).strip()
            copied["evidence_refs"] = [evidence_id_map.get(f"{prefix}:{ref}", ref) for ref in scene.get("evidence_refs", [])]
            scenario_library.append(copied)

    voice_model = {
        "register": unique_list([x for src in sources for x in src.get("voice_model", {}).get("register", [])]),
        "cadence": unique_list([x for src in sources for x in src.get("voice_model", {}).get("cadence", [])]),
        "lexical_features": unique_list([x for src in sources for x in src.get("voice_model", {}).get("lexical_features", [])]),
        "rhetorical_moves": unique_list([x for src in sources for x in src.get("voice_model", {}).get("rhetorical_moves", [])]),
        "response_defaults": unique_list([x for src in sources for x in src.get("voice_model", {}).get("response_defaults", [])]),
        "avoid": unique_list([x for src in sources for x in src.get("voice_model", {}).get("avoid", [])]),
    }

    display_name = args.display_name or args.new_persona_id
    shared_theses = unique_list(
        [
            src.get("summary", {}).get("core_thesis", "").strip()
            for src in sources
            if src.get("summary", {}).get("core_thesis", "").strip()
        ]
    )
    shared_oneliners = unique_list(
        [
            src.get("summary", {}).get("one_liner", "").strip()
            for src in sources
            if src.get("summary", {}).get("one_liner", "").strip()
        ]
    )
    fused_language = dominant_language(sources)
    fused = {
        "schema_version": "2.1",
        "persona_id": args.new_persona_id,
        "display_name": display_name,
        "artifact_meta": {
            "created_by": "persona fuse",
            "created_from": ", ".join(source_prefixes),
            "last_updated": dt.date.today().isoformat(),
            "status": "final",
        },
        "source_scope": {
            "corpus_root": "",
            "source_types": unique_list([t for src in sources for t in src.get("source_scope", {}).get("source_types", [])]),
            "time_span": "fused",
            "inclusion_notes": [f"Fused from personas: {', '.join(source_prefixes)}"],
            "exclusion_notes": [
                "No new raw corpus reading was performed during fusion; this artifact is synthesized from existing persona artifacts only."
            ],
            "known_blind_spots": [
                "Cross-persona fusion can blur contradictions if the source personas diverge sharply.",
                "This fused persona is synthetic, not a literal historical single subject."
            ],
        },
        "summary": {
            "one_liner": (
                f"Synthetic fused persona `{display_name}` combining source-grounded traits from {', '.join(source_prefixes)}."
                if not shared_oneliners
                else f"Fused from {', '.join(source_prefixes)}: " + " | ".join(shared_oneliners[:2])
            ),
            "core_thesis": (
                "This is a synthetic fused persona built from existing final persona artifacts. It should answer as a single roleplayable persona while preserving tensions, overlaps, and dominant shared patterns across the source personas."
                if not shared_theses
                else " | ".join(shared_theses[:2])
            ),
            "confidence_notes": "Fusion is best with 2-3 personas. This artifact is router-ready, but source divergence should still be monitored during roleplay and analysis.",
        },
        "source_index": combined_source_index,
        "evidence_index": combined_evidence_index,
        "dimensions": dimensions,
        "voice_model": voice_model,
        "scenario_library": scenario_library,
        "simulation_contract": {
            "identity_frame": f"This is a source-grounded fused persona simulation named {display_name}, synthesized from {', '.join(source_prefixes)}. It is a synthetic role, not a claim of literal historical identity.",
            "grounding_order": [
                "Prefer patterns shared across the fused sources.",
                "When the sources diverge, surface the tension instead of flattening it.",
                "If the topic is missing from all source personas, use explicit synthetic extrapolation consistent with the fused method."
            ],
            "truthfulness_policy": "Do not invent firsthand facts outside the source personas. For topics not covered directly, answer as a synthetic fused persona and avoid pretending to be a literal historical single subject.",
            "uncertainty_policy": "Where source personas diverge, either acknowledge the tension briefly or answer from the dominant shared pattern without fabricating false certainty.",
            "modern_topic_policy": "Use synthetic extrapolation cautiously and keep it consistent with the fused persona's shared values, reasoning style, and voice.",
            "citation_policy": "In ordinary roleplay, stay in character without footnotes. In analysis mode, you may briefly note which source persona contributed an important pattern or tension.",
            "default_response_language": fused_language,
            "language_policy": "If a /persona language override is active, answer in that language while preserving the fused persona's shared style and method. Otherwise answer in the fused persona default language.",
            "stay_in_character_policy": f"Once persona mode begins, remain fully in character for ordinary dialogue, prefix every in-character reply with `({display_name}) `, and do not fall back to neutral assistant voice unless the user exits or explicitly requests out-of-character analysis.",
            "identity_answer_policy": f"In ordinary in-character conversation, answer in first person as {display_name} and prefix the reply with `({display_name}) `. If asked who you are, identify yourself as {display_name}. If asked whether you are literally the real person or the underlying system, answer truthfully that this is a persona-based fused simulation and then continue according to the user's requested mode.",
            "persistence_policy": f"Persona mode is persistent. Continue fully in character across turns until an explicit exit command or a clear out-of-character request is given, and keep the `({display_name}) ` prefix on every in-character reply.",
            "exit_policy": "Exit on /persona exit, /persona off, /persona quit, 退出persona, 退出角色, or 退出skill.",
        },
        "module_registry": [],
        "load_profiles": [],
        "open_questions": [
            "Monitor whether repeated roleplay reveals unstable contradictions across the fused source personas.",
            "Refine any dimensions where one source persona dominates too heavily unless that dominance is intentional.",
        ],
    }

    write_json(output_dir / "persona.json", fused)
    print(output_dir / "persona.json")


if __name__ == "__main__":
    main()
