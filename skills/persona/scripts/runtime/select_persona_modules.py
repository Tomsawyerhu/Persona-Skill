#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

SHARED_DIR = Path(__file__).resolve().parent.parent / "shared"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

from persona_paths import load_json, resolve_persona

DEFAULT_PERSONAS_DIR = Path(__file__).resolve().parents[2] / "store" / "personas"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select the appropriate runtime modules for a persona invocation.")
    parser.add_argument("--persona", required=True, help="Persona id or path to persona.json")
    parser.add_argument("--scene", default="default", help="Scene tag such as default, conflict, decision, analysis")
    parser.add_argument("--personas-dir", default=str(DEFAULT_PERSONAS_DIR), help="Root personas directory for id lookup")
    return parser.parse_args()


def choose_profile(data: Dict[str, Any], scene: str) -> Dict[str, Any]:
    status = data.get("artifact_meta", {}).get("status", "")
    if status != "final":
        raise ValueError(f"persona is not router-ready: status is `{status or 'unknown'}`, expected `final`")
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
    try:
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
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
