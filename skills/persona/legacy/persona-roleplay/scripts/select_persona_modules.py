#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select the appropriate runtime modules for a persona invocation.")
    parser.add_argument("--persona", required=True, help="Persona id or path to persona.json")
    parser.add_argument("--scene", default="default", help="Scene tag such as default, conflict, decision, analysis")
    parser.add_argument("--personas-dir", default="personas", help="Root personas directory for id lookup")
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_persona(persona_arg: str, personas_dir: Path) -> Path:
    arg_path = Path(persona_arg)
    if arg_path.exists():
        return arg_path.resolve()
    for path in personas_dir.glob("*/persona.json"):
        data = load_json(path)
        if persona_arg in {data.get("persona_id", ""), data.get("display_name", data.get("name", ""))}:
            return path.resolve()
    raise FileNotFoundError(f"persona not found: {persona_arg}")


def choose_profile(data: Dict[str, Any], scene: str) -> Dict[str, Any]:
    if not data.get("module_registry") or not data.get("load_profiles"):
        raise ValueError("persona is not router-ready: missing module_registry or load_profiles")
    for profile in data.get("load_profiles", []):
        if scene in profile.get("scene_tags", []):
            return profile
    for profile in data.get("load_profiles", []):
        if profile.get("default"):
            return profile
    return {"id": "", "module_refs": []}


def main() -> None:
    args = parse_args()
    personas_dir = Path(args.personas_dir).resolve()
    persona_path = resolve_persona(args.persona, personas_dir)
    data = load_json(persona_path)
    profile = choose_profile(data, args.scene)
    module_lookup = {item["id"]: item for item in data.get("module_registry", [])}
    selected: List[Dict[str, Any]] = []
    for ref in profile.get("module_refs", []):
        module = module_lookup.get(ref)
        if not module:
            continue
        module_path = persona_path.parent / module["path"]
        payload = load_json(module_path) if module_path.exists() else {}
        selected.append(
            {
                "id": module["id"],
                "label": module["label"],
                "kind": module["kind"],
                "path": module["path"],
                "payload": payload,
            }
        )
    print(
        json.dumps(
            {
                "persona_id": data.get("persona_id", ""),
                "display_name": data.get("display_name", data.get("name", "")),
                "scene": args.scene,
                "selected_profile": profile,
                "modules": selected,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
