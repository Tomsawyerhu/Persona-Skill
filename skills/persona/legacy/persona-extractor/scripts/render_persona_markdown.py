#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render markdown mirrors from a persona artifact.")
    parser.add_argument("persona_json", help="Path to persona.json")
    return parser.parse_args()


def build_source_lookup(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item["id"]: item for item in data.get("source_index", [])}


def build_evidence_lookup(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item["id"]: item for item in data.get("evidence_index", [])}


def render_profile(data: Dict[str, Any]) -> str:
    lines = [
        f"# {data['display_name']} Persona Profile",
        "",
        f"- persona_id: `{data['persona_id']}`",
        f"- schema_version: `{data['schema_version']}`",
        f"- status: `{data.get('artifact_meta', {}).get('status', '')}`",
        f"- source_root: `{data.get('source_scope', {}).get('corpus_root', '')}`",
        f"- time_span: {data.get('source_scope', {}).get('time_span', '')}",
        "",
        "## Summary",
        "",
        data.get("summary", {}).get("core_thesis", ""),
        "",
        "## Confidence Notes",
        "",
        data.get("summary", {}).get("confidence_notes", ""),
        "",
        "## Dimensions",
        "",
    ]
    for dim in data.get("dimensions", []):
        lines.append(f"### {dim['label']} (`{dim['id']}`)")
        lines.append("")
        lines.append(dim.get("synthesis", {}).get("summary", ""))
        lines.append("")
        for section_name, key in [
            ("Patterns", "patterns"),
            ("Anti-patterns", "anti_patterns"),
            ("Tensions", "tensions"),
            ("Drift", "drift"),
        ]:
            values = dim.get("synthesis", {}).get(key, [])
            if not values:
                continue
            lines.append(f"{section_name}:")
            for value in values:
                lines.append(f"- {value}")
            lines.append("")
        lines.append(f"confidence: `{dim.get('confidence', '')}`")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_evidence(data: Dict[str, Any]) -> str:
    source_lookup = build_source_lookup(data)
    evidence_lookup = build_evidence_lookup(data)
    lines = [f"# {data['display_name']} Evidence", ""]
    for dim in data.get("dimensions", []):
        lines.append(f"## {dim['label']} (`{dim['id']}`)")
        lines.append("")
        refs = dim.get("evidence_refs", [])
        if not refs:
            lines.append("- no evidence refs")
            lines.append("")
            continue
        for ev_id in refs:
            ev = evidence_lookup.get(ev_id)
            if not ev:
                lines.append(f"- missing evidence ref: `{ev_id}`")
                continue
            src = source_lookup.get(ev["source_id"], {})
            lines.append(
                f"- `{ev['id']}` | `{ev['source_id']}` | "
                f"{src.get('title', 'unknown-source')} | "
                f"`{src.get('path', '')}`"
            )
            lines.append(f"  excerpt: {ev.get('excerpt', '')}")
            lines.append(f"  note: {ev.get('note', '')}")
            if ev.get("tags"):
                lines.append(f"  tags: {', '.join(ev['tags'])}")
            lines.append("")
    return "\n".join(lines)


def render_qa(data: Dict[str, Any]) -> str:
    lines = [f"# {data['display_name']} Scenario Library", ""]
    for item in data.get("scenario_library", []):
        lines.append(f"## {item['scene']}")
        lines.append("")
        lines.append(f"- id: `{item['id']}`")
        lines.append(f"- mode: `{item['answer_mode']}`")
        lines.append(f"- style: `{item.get('response_style', '')}`")
        lines.append(f"- prompt: {item['user_prompt']}")
        lines.append(f"- evidence_refs: {', '.join(item.get('evidence_refs', []))}")
        if item.get("limitations"):
            lines.append(f"- limitations: {item['limitations']}")
        lines.append("")
        lines.append(item.get("answer", ""))
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    persona_path = Path(args.persona_json).resolve()
    data = json.loads(persona_path.read_text(encoding="utf-8"))
    target_dir = persona_path.parent
    target_dir.joinpath("profile.md").write_text(render_profile(data), encoding="utf-8")
    target_dir.joinpath("evidence.md").write_text(render_evidence(data), encoding="utf-8")
    target_dir.joinpath("qa_samples.md").write_text(render_qa(data), encoding="utf-8")


if __name__ == "__main__":
    main()
