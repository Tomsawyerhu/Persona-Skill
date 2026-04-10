#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a persona catalog for router-style invocation.")
    parser.add_argument("--personas-dir", required=True, help="Directory containing persona folders.")
    parser.add_argument("--output", default="", help="Optional explicit output path.")
    return parser.parse_args()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    args = parse_args()
    personas_dir = Path(args.personas_dir).resolve()
    catalog: List[Dict[str, Any]] = []
    for path in sorted(personas_dir.glob("*/persona.json")):
        try:
            data = load_json(path)
        except Exception:
            continue
        catalog.append(
            {
                "persona_id": data.get("persona_id", ""),
                "display_name": data.get("display_name", data.get("name", "")),
                "path": path.relative_to(personas_dir.parent).as_posix(),
                "schema_version": data.get("schema_version", ""),
                "status": data.get("artifact_meta", {}).get("status", ""),
                "has_modules": bool(data.get("module_registry")),
                "router_ready": data.get("schema_version", "") == "2.1" and bool(data.get("module_registry")) and bool(data.get("load_profiles")),
                "default_profile": next((p["id"] for p in data.get("load_profiles", []) if p.get("default")), ""),
                "aliases": [data.get("persona_id", ""), data.get("display_name", data.get("name", ""))],
            }
        )
    output = Path(args.output).resolve() if args.output else personas_dir / "catalog.json"
    output.write_text(json.dumps({"personas": catalog}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
