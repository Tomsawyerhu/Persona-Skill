#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List


HEADING_RE = re.compile(r"^#\s+(.*)")
DATE_RE = re.compile(r"^[（(]([^）)]+)[）)]$")
SKIP_FILENAMES = {"SUMMARY.md", "目录.md"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a generic evidence pack for persona extraction.")
    parser.add_argument("--source-dir", required=True, help="Directory containing the source corpus.")
    parser.add_argument("--output-dir", required=True, help="Directory to write extraction artifacts.")
    parser.add_argument("--config", help="Path to extractor_config.json created by scaffold_persona_project.py.")
    parser.add_argument("--max-blocks-per-dimension", type=int, default=20)
    parser.add_argument("--max-generic-blocks", type=int, default=50)
    return parser.parse_args()


def normalize_text(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_blocks(text: str) -> List[str]:
    blocks: List[str] = []
    current: List[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.strip() == "------------------":
            break
        if not line.strip():
            if current:
                block = normalize_text(" ".join(current))
                if block:
                    blocks.append(block)
                current = []
            continue
        if line.lstrip().startswith("#"):
            if current:
                block = normalize_text(" ".join(current))
                if block:
                    blocks.append(block)
                current = []
            continue
        current.append(line.strip())
    if current:
        block = normalize_text(" ".join(current))
        if block:
            blocks.append(block)
    return [block for block in blocks if len(block) >= 40]


def parse_document(path: Path, root: Path, source_id: str) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    title = path.stem
    date = ""
    for line in text.splitlines()[:8]:
        stripped = line.strip()
        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            title = heading_match.group(1).strip()
            continue
        date_match = DATE_RE.match(stripped)
        if date_match:
            date = date_match.group(1).strip()
            break
    return {
        "id": source_id,
        "title": title,
        "path": path.relative_to(root).as_posix(),
        "source_type": path.suffix.lstrip(".") or "text",
        "date": date,
        "reliability": "unknown",
        "notes": "",
        "blocks": extract_blocks(text),
    }


def load_config(config_path: Path | None) -> Dict[str, Any]:
    if not config_path:
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def build_source_index(source_dir: Path, root: Path) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    for idx, path in enumerate(sorted(source_dir.rglob("*"))):
        if not path.is_file():
            continue
        if path.name in SKIP_FILENAMES:
            continue
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        source_id = f"src_{idx + 1:04d}"
        docs.append(parse_document(path, root, source_id))
    return docs


def build_block_index(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    counter = 1
    for doc in docs:
        for block_idx, block in enumerate(doc["blocks"], start=1):
            blocks.append(
                {
                    "id": f"blk_{counter:05d}",
                    "source_id": doc["id"],
                    "block_index": block_idx,
                    "text": block,
                    "char_count": len(block),
                }
            )
            counter += 1
    return blocks


def score_block(text: str, seed_terms: List[str]) -> Dict[str, Any]:
    hits: List[str] = []
    score = 0
    for term in seed_terms:
        if not term:
            continue
        count = text.count(term)
        if count:
            score += count * max(1, len(term))
            hits.append(term)
    return {"score": score, "hits": hits}


def build_dimension_candidates(
    block_index: List[Dict[str, Any]],
    config: Dict[str, Any],
    max_blocks: int,
) -> List[Dict[str, Any]]:
    dimensions = config.get("dimensions", [])
    candidates: List[Dict[str, Any]] = []
    for dim in dimensions:
        dim_id = dim.get("id", "")
        label = dim.get("label", dim_id)
        seed_terms = dim.get("seed_terms", [])
        if not seed_terms:
            continue
        scored_blocks: List[Dict[str, Any]] = []
        for block in block_index:
            scored = score_block(block["text"], seed_terms)
            if not scored["score"]:
                continue
            scored_blocks.append(
                {
                    "block_id": block["id"],
                    "source_id": block["source_id"],
                    "score": scored["score"],
                    "hits": scored["hits"],
                    "snippet": block["text"][:500],
                }
            )
        scored_blocks.sort(key=lambda item: (int(item["score"]), len(item["snippet"])), reverse=True)
        candidates.append(
            {
                "dimension_id": dim_id,
                "label": label,
                "seed_terms": seed_terms,
                "questions": dim.get("questions", []),
                "candidates": scored_blocks[:max_blocks],
            }
        )
    return candidates


def build_generic_candidates(block_index: List[Dict[str, Any]], max_blocks: int) -> List[Dict[str, Any]]:
    ranked = sorted(block_index, key=lambda item: item["char_count"], reverse=True)
    return [
        {
            "block_id": block["id"],
            "source_id": block["source_id"],
            "char_count": block["char_count"],
            "snippet": block["text"][:500],
        }
        for block in ranked[:max_blocks]
    ]


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(
    output_dir: Path,
    source_index: List[Dict[str, Any]],
    block_index: List[Dict[str, Any]],
    dimension_candidates: List[Dict[str, Any]],
    generic_candidates: List[Dict[str, Any]],
) -> None:
    lines = [
        "# Candidate Evidence",
        "",
        f"- sources: {len(source_index)}",
        f"- blocks: {len(block_index)}",
        "",
    ]
    if dimension_candidates:
        for dim in dimension_candidates:
            lines.append(f"## {dim['label']} (`{dim['dimension_id']}`)")
            lines.append("")
            if dim.get("questions"):
                lines.append(f"questions: {' | '.join(dim['questions'])}")
                lines.append("")
            for item in dim["candidates"]:
                lines.append(
                    "- "
                    f"{item['block_id']} | "
                    f"{item['source_id']} | "
                    f"score={item['score']} | "
                    f"hits={', '.join(item['hits'])}"
                )
                lines.append(f"  snippet: {item['snippet']}")
                lines.append("")
    else:
        lines.append("## Generic Blocks")
        lines.append("")
        for item in generic_candidates:
            lines.append(
                "- "
                f"{item['block_id']} | "
                f"{item['source_id']} | "
                f"chars={item['char_count']}"
            )
            lines.append(f"  snippet: {item['snippet']}")
            lines.append("")
    output_dir.joinpath("candidate_evidence.md").write_text("\n".join(lines), encoding="utf-8")


def write_source_inventory(output_dir: Path, source_index: List[Dict[str, Any]]) -> None:
    lines = [
        "# Source Inventory",
        "",
        f"- documents: {len(source_index)}",
        "",
    ]
    for item in source_index:
        date = item["date"] or "unknown-date"
        lines.append(f"- `{item['id']}` | `{item['path']}` | {item['title']} | {date}")
    output_dir.joinpath("source_inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path.cwd().resolve()
    source_dir = Path(args.source_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    config = load_config(Path(args.config).resolve() if args.config else None)
    output_dir.mkdir(parents=True, exist_ok=True)

    docs = build_source_index(source_dir, root)
    source_index = [{k: v for k, v in doc.items() if k != "blocks"} for doc in docs]
    block_index = build_block_index(docs)
    dimension_candidates = build_dimension_candidates(block_index, config, args.max_blocks_per_dimension)
    generic_candidates = build_generic_candidates(block_index, args.max_generic_blocks)

    write_json(output_dir.joinpath("source_index.json"), source_index)
    write_json(output_dir.joinpath("block_index.json"), block_index)
    write_json(
        output_dir.joinpath("candidate_passages.json"),
        {
            "config_path": args.config or "",
            "dimension_candidates": dimension_candidates,
            "generic_candidates": generic_candidates,
        },
    )
    write_source_inventory(output_dir, source_index)
    write_markdown(output_dir, source_index, block_index, dimension_candidates, generic_candidates)


if __name__ == "__main__":
    main()
