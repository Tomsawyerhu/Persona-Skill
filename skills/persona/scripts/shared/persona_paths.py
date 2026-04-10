#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_alias(value: str) -> str:
    return value.strip().casefold()


def unique_aliases(values: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    aliases: List[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned:
            continue
        key = normalize_alias(cleaned)
        if key in seen:
            continue
        seen.add(key)
        aliases.append(cleaned)
    return aliases


def alias_candidates(persona_path: Path, data: Dict[str, Any], catalog_entry: Dict[str, Any] | None = None) -> List[str]:
    dir_name = persona_path.parent.name
    values: List[str] = [
        data.get("persona_id", ""),
        data.get("display_name", data.get("name", "")),
        dir_name,
        dir_name.lstrip("_"),
    ]
    if catalog_entry:
        values.extend(catalog_entry.get("aliases", []))
        values.append(catalog_entry.get("persona_id", ""))
        values.append(catalog_entry.get("display_name", ""))
    return unique_aliases(values)


def resolve_persona(persona_arg: str, personas_dir: Path) -> Path:
    arg_path = Path(persona_arg)
    if arg_path.exists():
        if arg_path.is_dir():
            persona_json = arg_path / "persona.json"
            if persona_json.exists():
                return persona_json.resolve()
        if arg_path.is_file():
            return arg_path.resolve()

    target = normalize_alias(persona_arg)
    catalog_path = personas_dir / "catalog.json"
    if catalog_path.exists():
        catalog = load_json(catalog_path)
        for entry in catalog.get("personas", []):
            persona_path = (personas_dir.parent / entry["path"]).resolve()
            if not persona_path.exists():
                continue
            data = load_json(persona_path)
            aliases = alias_candidates(persona_path, data, entry)
            if target in {normalize_alias(alias) for alias in aliases}:
                return persona_path

    for persona_path in personas_dir.glob("*/persona.json"):
        data = load_json(persona_path)
        aliases = alias_candidates(persona_path, data)
        if target in {normalize_alias(alias) for alias in aliases}:
            return persona_path.resolve()

    raise FileNotFoundError(f"persona not found: {persona_arg}")
