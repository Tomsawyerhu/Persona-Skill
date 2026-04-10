#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "persona_id",
    "display_name",
    "artifact_meta",
    "source_scope",
    "summary",
    "source_index",
    "evidence_index",
    "dimensions",
    "voice_model",
    "scenario_library",
    "simulation_contract",
    "module_registry",
    "load_profiles",
    "open_questions",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a persona artifact.")
    parser.add_argument("persona_json", help="Path to persona.json or persona.template.json")
    parser.add_argument("--mode", choices=["template", "final"], default="final")
    return parser.parse_args()


def load_data(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_top_level(data: Dict[str, Any], errors: List[str]) -> None:
    missing = REQUIRED_TOP_LEVEL - set(data.keys())
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")
    if data.get("schema_version") != "2.1":
        errors.append("schema_version must be '2.1'")


def validate_ids(items: List[Dict[str, Any]], name: str, errors: List[str]) -> Set[str]:
    seen: Set[str] = set()
    for item in items:
        item_id = item.get("id")
        if not item_id:
            errors.append(f"{name} contains item without id")
            continue
        if item_id in seen:
            errors.append(f"duplicate id in {name}: {item_id}")
        seen.add(item_id)
    return seen


def validate_references(data: Dict[str, Any], mode: str, errors: List[str]) -> None:
    source_ids = validate_ids(data.get("source_index", []), "source_index", errors)
    evidence_ids = validate_ids(data.get("evidence_index", []), "evidence_index", errors)

    for item in data.get("evidence_index", []):
        source_id = item.get("source_id")
        if source_id and source_id not in source_ids:
            errors.append(f"evidence `{item.get('id')}` references missing source_id `{source_id}`")

    for dim in data.get("dimensions", []):
        for ref in dim.get("evidence_refs", []):
            if ref not in evidence_ids:
                errors.append(f"dimension `{dim.get('id')}` references missing evidence `{ref}`")

    for scene in data.get("scenario_library", []):
        for ref in scene.get("evidence_refs", []):
            if ref not in evidence_ids:
                errors.append(f"scenario `{scene.get('id')}` references missing evidence `{ref}`")

    module_ids = validate_ids(data.get("module_registry", []), "module_registry", errors)
    for profile in data.get("load_profiles", []):
        for ref in profile.get("module_refs", []):
            if ref not in module_ids:
                errors.append(f"load_profile `{profile.get('id')}` references missing module `{ref}`")

    if mode == "final":
        if len(data.get("source_index", [])) < 3:
            errors.append("final artifact should usually cite at least 3 source items")
        if len(data.get("evidence_index", [])) < 8:
            errors.append("final artifact should usually contain at least 8 evidence items")
        if len(data.get("dimensions", [])) < 8:
            errors.append("final artifact should usually have at least 8 dimensions")
        if len(data.get("scenario_library", [])) < 5:
            errors.append("final artifact should usually have at least 5 scenario items")
        for dim in data.get("dimensions", []):
            if not dim.get("evidence_refs") and dim.get("confidence") != "low":
                errors.append(f"dimension `{dim.get('id')}` has no evidence_refs but is not marked low confidence")


def validate_structure(data: Dict[str, Any], mode: str, errors: List[str]) -> None:
    for dim in data.get("dimensions", []):
        required = {"id", "label", "category", "priority", "definition", "extraction_questions", "synthesis", "evidence_refs", "confidence"}
        missing = required - set(dim.keys())
        if missing:
            errors.append(f"dimension `{dim.get('id', '?')}` missing keys: {sorted(missing)}")
        synthesis = dim.get("synthesis", {})
        for key in ["summary", "patterns", "anti_patterns", "tensions", "drift"]:
            if key not in synthesis:
                errors.append(f"dimension `{dim.get('id', '?')}` missing synthesis.{key}")
        if mode == "final" and not synthesis.get("summary"):
            errors.append(f"dimension `{dim.get('id', '?')}` has empty synthesis.summary")

    contract_required = {
        "identity_frame",
        "grounding_order",
        "truthfulness_policy",
        "uncertainty_policy",
        "modern_topic_policy",
        "citation_policy",
        "default_response_language",
        "language_policy",
        "stay_in_character_policy",
        "identity_answer_policy",
        "persistence_policy",
        "exit_policy",
    }
    missing = contract_required - set(data.get("simulation_contract", {}).keys())
    if missing:
        errors.append(f"simulation_contract missing keys: {sorted(missing)}")

    for scene in data.get("scenario_library", []):
        required = {"id", "scene", "scene_tags", "user_prompt", "answer_mode", "response_style", "answer", "evidence_refs"}
        missing_scene = required - set(scene.keys())
        if missing_scene:
            errors.append(f"scenario `{scene.get('id', '?')}` missing keys: {sorted(missing_scene)}")

    for module in data.get("module_registry", []):
        required = {"id", "label", "kind", "path", "contains", "tags", "priority"}
        missing_module = required - set(module.keys())
        if missing_module:
            errors.append(f"module `{module.get('id', '?')}` missing keys: {sorted(missing_module)}")

    for profile in data.get("load_profiles", []):
        required = {"id", "label", "description", "scene_tags", "module_refs", "default"}
        missing_profile = required - set(profile.keys())
        if missing_profile:
            errors.append(f"load_profile `{profile.get('id', '?')}` missing keys: {sorted(missing_profile)}")

    if mode == "final":
        summary = data.get("summary", {})
        if not summary.get("core_thesis"):
            errors.append("summary.core_thesis is required in final mode")


def main() -> None:
    args = parse_args()
    path = Path(args.persona_json).resolve()
    data = load_data(path)
    errors: List[str] = []
    validate_top_level(data, errors)
    validate_structure(data, args.mode, errors)
    validate_references(data, args.mode, errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        sys.exit(1)
    print(f"OK: {path.name} passed {args.mode} validation")


if __name__ == "__main__":
    main()
