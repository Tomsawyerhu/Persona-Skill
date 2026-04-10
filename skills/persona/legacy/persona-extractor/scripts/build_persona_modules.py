#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build runtime modules and load profiles from a full persona artifact.")
    parser.add_argument("persona_json", help="Path to persona.json")
    return parser.parse_args()


def load_persona(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_core_module(data: Dict[str, Any]) -> Dict[str, Any]:
    dims = [d for d in data.get("dimensions", []) if d.get("priority") == "high"][:4]
    return {
        "label": "Core",
        "kind": "core",
        "payload": {
            "summary": data.get("summary", {}),
            "dimensions": dims,
            "open_questions": data.get("open_questions", [])[:8],
        },
        "contains": {
            "dimension_ids": [d["id"] for d in dims],
            "scenario_ids": [],
            "includes_voice": False,
            "includes_contract": False,
        },
        "tags": ["default", "core"],
        "priority": "high",
    }


def build_category_modules(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for dim in data.get("dimensions", []):
        grouped[dim.get("category", "other")].append(dim)

    modules: List[Dict[str, Any]] = []
    for category, dims in grouped.items():
        modules.append(
            {
                "label": f"Category: {category}",
                "kind": "dimension-group",
                "payload": {
                    "category": category,
                    "dimensions": dims,
                },
                "contains": {
                    "dimension_ids": [d["id"] for d in dims],
                    "scenario_ids": [],
                    "includes_voice": False,
                    "includes_contract": False,
                },
                "tags": [category],
                "priority": "medium",
            }
        )
    return modules


def build_voice_module(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "label": "Voice Model",
        "kind": "voice",
        "payload": data.get("voice_model", {}),
        "contains": {
            "dimension_ids": [],
            "scenario_ids": [],
            "includes_voice": True,
            "includes_contract": False,
        },
        "tags": ["voice", "style"],
        "priority": "high",
    }


def build_contract_module(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "label": "Simulation Contract",
        "kind": "contract",
        "payload": data.get("simulation_contract", {}),
        "contains": {
            "dimension_ids": [],
            "scenario_ids": [],
            "includes_voice": False,
            "includes_contract": True,
        },
        "tags": ["contract", "runtime"],
        "priority": "high",
    }


def build_scenario_modules(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for scene in data.get("scenario_library", []):
        tags = scene.get("scene_tags", []) or ["default"]
        for tag in tags:
            grouped[tag].append(scene)
    modules: List[Dict[str, Any]] = []
    for tag, scenes in grouped.items():
        modules.append(
            {
                "label": f"Scenarios: {tag}",
                "kind": "scenario-group",
                "payload": {
                    "scene_tag": tag,
                    "scenarios": scenes,
                },
                "contains": {
                    "dimension_ids": [],
                    "scenario_ids": [s["id"] for s in scenes],
                    "includes_voice": False,
                    "includes_contract": False,
                },
                "tags": ["scenarios", tag],
                "priority": "medium",
            }
        )
    return modules


def assign_ids_and_write(persona_path: Path, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    modules_dir = persona_path.parent / "modules"
    modules_dir.mkdir(parents=True, exist_ok=True)
    registry: List[Dict[str, Any]] = []
    for index, module in enumerate(modules, start=1):
        module_id = f"mod_{index:03d}"
        file_name = f"{module_id}.json"
        write_json(modules_dir / file_name, module["payload"])
        registry.append(
            {
                "id": module_id,
                "label": module["label"],
                "kind": module["kind"],
                "path": f"modules/{file_name}",
                "contains": module["contains"],
                "tags": module["tags"],
                "priority": module["priority"],
            }
        )
    return registry


def infer_profile_modules(registry: List[Dict[str, Any]], required_tags: List[str]) -> List[str]:
    refs: List[str] = []
    for item in registry:
        if any(tag in item.get("tags", []) for tag in required_tags):
            refs.append(item["id"])
    for item in registry:
        if item["kind"] in {"core", "voice", "contract"} and item["id"] not in refs:
            refs.append(item["id"])
    return refs


def build_load_profiles(registry: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": "default_chat",
            "label": "Default Chat",
            "description": "General in-character dialogue",
            "scene_tags": ["default", "chat"],
            "module_refs": infer_profile_modules(registry, ["default", "identity", "social", "voice"]),
            "default": True,
        },
        {
            "id": "decision_mode",
            "label": "Decision Mode",
            "description": "Decision-heavy or advisory interaction",
            "scene_tags": ["decision", "advice", "uncertainty"],
            "module_refs": infer_profile_modules(registry, ["cognition", "motivation", "voice"]),
            "default": False,
        },
        {
            "id": "conflict_mode",
            "label": "Conflict Mode",
            "description": "Conflict, disagreement, blame, criticism",
            "scene_tags": ["conflict", "feedback", "pressure"],
            "module_refs": infer_profile_modules(registry, ["social", "integration", "voice", "conflict"]),
            "default": False,
        },
        {
            "id": "analysis_mode",
            "label": "Analysis Mode",
            "description": "Explain the persona explicitly or inspect behavior",
            "scene_tags": ["analysis", "explanation"],
            "module_refs": infer_profile_modules(registry, ["core", "cognition", "integration", "voice"]),
            "default": False,
        },
    ]


def main() -> None:
    args = parse_args()
    persona_path = Path(args.persona_json).resolve()
    data = load_persona(persona_path)

    modules = [
        build_core_module(data),
        *build_category_modules(data),
        build_voice_module(data),
        build_contract_module(data),
        *build_scenario_modules(data),
    ]
    registry = assign_ids_and_write(persona_path, modules)
    profiles = build_load_profiles(registry)

    data["module_registry"] = registry
    data["load_profiles"] = profiles
    write_json(persona_path, data)


if __name__ == "__main__":
    main()
