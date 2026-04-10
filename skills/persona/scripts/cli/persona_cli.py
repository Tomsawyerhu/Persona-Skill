#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent
SCRIPT_ROOT = ROOT.parent
SKILL_ROOT = SCRIPT_ROOT.parent
DEFAULT_PERSONAS_DIR = SKILL_ROOT / "store" / "personas"
SHARED_DIR = SCRIPT_ROOT / "shared"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

from persona_paths import load_json as shared_load_json, normalize_alias, resolve_persona
from runtime_state import clear_language_override, default_session_file, get_language_override, set_language_override


def run_script(script_relative_path: str, args: List[str]) -> None:
    script = SCRIPT_ROOT / script_relative_path
    cmd = [sys.executable, str(script), *args]
    subprocess.run(cmd, check=True)


def run_script_capture(script_relative_path: str, args: List[str]) -> subprocess.CompletedProcess[str]:
    script = SCRIPT_ROOT / script_relative_path
    cmd = [sys.executable, str(script), *args]
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def load_json(path: Path) -> Dict[str, Any]:
    return shared_load_json(path)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def infer_source_types(data_dir: Path) -> List[str]:
    suffixes = sorted({p.suffix.lower().lstrip(".") for p in data_dir.rglob("*") if p.is_file() and p.suffix})
    return suffixes[:12]


def ensure_catalog(personas_dir: Path) -> None:
    personas_dir.mkdir(parents=True, exist_ok=True)
    run_script("runtime/build_persona_catalog.py", ["--personas-dir", str(personas_dir)])


def find_existing_persona(persona_name: str, personas_dir: Path) -> Path | None:
    exact_dir = personas_dir / persona_name
    if exact_dir.exists():
        persona_json = exact_dir / "persona.json"
        return persona_json if persona_json.exists() else exact_dir

    catalog_path = personas_dir / "catalog.json"
    if catalog_path.exists():
        try:
            return resolve_persona(persona_name, personas_dir)
        except FileNotFoundError:
            return None
    return None


def hydrate_distill_artifact(
    persona_json: Path,
    config_path: Path,
    *,
    status: str = "bootstrapped",
) -> None:
    artifact = load_json(persona_json)
    config = load_json(config_path)

    artifact_meta = artifact.setdefault("artifact_meta", {})
    artifact_meta["created_by"] = "persona distill"
    artifact_meta["created_from"] = "scaffold only"
    artifact_meta["last_updated"] = dt.date.today().isoformat()
    artifact_meta["status"] = status

    source_scope = artifact.setdefault("source_scope", {})
    source_scope["corpus_root"] = config.get("corpus_root", "")
    source_scope["source_types"] = config.get("source_types", [])
    source_scope["time_span"] = config.get("time_span", "")
    source_scope["inclusion_notes"] = config.get("inclusion_notes", [])
    source_scope["exclusion_notes"] = config.get("exclusion_notes", [])
    source_scope["known_blind_spots"] = config.get("known_blind_spots", [])

    summary = artifact.setdefault("summary", {})
    if not summary.get("one_liner"):
        summary["one_liner"] = (
            f"Bootstrapped persona workspace for {artifact.get('display_name', artifact.get('persona_id', 'this persona'))}."
        )
    if not summary.get("confidence_notes"):
        summary["confidence_notes"] = (
            "No persona content has been synthesized yet. Final extraction requires direct corpus reading and manual source-grounded authoring."
        )

    write_json(persona_json, artifact)


def cmd_list(args: argparse.Namespace) -> None:
    personas_dir = Path(args.personas_dir).resolve()
    ensure_catalog(personas_dir)
    catalog = load_json(personas_dir / "catalog.json")
    items = catalog.get("personas", [])
    if not args.all:
        items = [item for item in items if item.get("status") != "template"]
    for item in items:
        status = item.get("status", "")
        ready = "router-ready" if item.get("router_ready") else "not-ready"
        print(f"{item['persona_id']}\t{item['display_name']}\t{status}\t{ready}")


def cmd_distill(args: argparse.Namespace) -> None:
    personas_dir = Path(args.personas_dir).resolve()
    data_dir = Path(args.data_dir).resolve()
    if not data_dir.exists() or not data_dir.is_dir():
        raise SystemExit(f"data directory does not exist or is not a directory: {data_dir}")
    ensure_catalog(personas_dir)
    existing = find_existing_persona(args.persona_name, personas_dir)
    if existing:
        existing_path = existing if existing.name == "persona.json" else existing / "persona.json"
        existing_id = args.persona_name
        if existing_path.exists():
            try:
                existing_data = load_json(existing_path)
                existing_id = existing_data.get("persona_id") or existing_data.get("display_name") or existing.parent.name
            except Exception:
                existing_id = existing.parent.name if existing.name == "persona.json" else existing.name
        raise SystemExit(
            f"persona already exists: {existing_id}\n"
            f"existing path: {existing.parent if existing.name == 'persona.json' else existing}\n"
            "delete it first with: /persona delete <name>\n"
            "or choose a different persona name"
        )
    persona_dir = personas_dir / args.persona_name
    display_name = args.display_name or args.persona_name

    run_script(
        "extraction/scaffold_persona_project.py",
        ["--output-dir", str(persona_dir), "--persona-id", args.persona_name, "--display-name", display_name],
    )

    config_path = persona_dir / "extractor_config.json"
    config = load_json(config_path)
    config["corpus_root"] = str(data_dir)
    config["source_types"] = infer_source_types(data_dir)
    write_json(config_path, config)

    template_path = persona_dir / "persona.template.json"
    persona_json = persona_dir / "persona.json"
    if not persona_json.exists():
        persona_json.write_text(template_path.read_text(encoding="utf-8"), encoding="utf-8")

    obsolete_artifacts = [
        "block_index.json",
        "candidate_passages.json",
        "candidate_evidence.md",
        "source_inventory.md",
        "source_index.json",
    ]
    for relative_name in obsolete_artifacts:
        path = persona_dir / relative_name
        if path.exists():
            path.unlink()

    hydrate_distill_artifact(persona_json, config_path, status="bootstrapped")
    ensure_catalog(personas_dir)

    print(f"distill bootstrap ready: {persona_dir}")
    print("status: bootstrapped (not router-ready)")
    print("note: this CLI command only completes the bootstrap stage used by the end-to-end /persona distill skill workflow.")
    print("next steps:")
    print(f"1. read source material directly from: {data_dir}")
    print(f"2. inspect the corpus directory itself instead of generated candidate files")
    print(
        "3. author/refine: "
        f"{persona_dir / 'persona.json'} from direct source reading and your own synthesis"
    )
    print(
        "4. validate with: "
        f"python {SCRIPT_ROOT / 'extraction' / 'validate_persona.py'} {persona_dir / 'persona.json'} --mode final"
    )
    print(
        "5. build modules with: "
        f"python {SCRIPT_ROOT / 'extraction' / 'build_persona_modules.py'} {persona_dir / 'persona.json'}"
    )
    print(
        "6. refresh the catalog with: "
        f"python {SCRIPT_ROOT / 'runtime' / 'build_persona_catalog.py'} --personas-dir {personas_dir}"
    )
    print("note: the active workflow no longer generates candidate passages, block indexes, or heuristic drafts.")


def cmd_use(args: argparse.Namespace) -> None:
    personas_dir = Path(args.personas_dir).resolve()
    scene = args.scene or "default"
    result = run_script_capture(
        "runtime/select_persona_modules.py",
        ["--persona", args.persona_name, "--scene", scene, "--personas-dir", str(personas_dir)],
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip()
        raise SystemExit(message or f"failed to switch persona: {args.persona_name}")
    print(result.stdout.rstrip())


def cmd_delete(args: argparse.Namespace) -> None:
    personas_dir = Path(args.personas_dir).resolve()
    ensure_catalog(personas_dir)
    try:
        persona_path = resolve_persona(args.persona_name, personas_dir)
    except FileNotFoundError:
        print(f"persona does not exist: {args.persona_name}")
        return

    persona_dir = persona_path.parent
    if normalize_alias(persona_dir.name) in {"_starter_template", "starter_template"}:
        raise SystemExit("cannot delete built-in template persona: starter_template")

    shutil.rmtree(persona_dir)
    ensure_catalog(personas_dir)
    print(f"deleted persona: {args.persona_name}")
    print(f"removed path: {persona_dir}")


def cmd_fuse(args: argparse.Namespace) -> None:
    personas_dir = Path(args.personas_dir).resolve()
    ensure_catalog(personas_dir)
    if len(args.source_personas) < 2:
        raise SystemExit("fuse requires at least 2 source personas")
    if len(args.source_personas) > 3:
        raise SystemExit("fuse supports at most 3 source personas by default; more than 3 is not guaranteed")
    existing = find_existing_persona(args.new_persona_name, personas_dir)
    if existing:
        existing_path = existing if existing.name == "persona.json" else existing / "persona.json"
        existing_id = args.new_persona_name
        if existing_path.exists():
            try:
                existing_data = load_json(existing_path)
                existing_id = existing_data.get("persona_id") or existing_data.get("display_name") or existing_path.parent.name
            except Exception:
                existing_id = existing_path.parent.name
        raise SystemExit(
            f"persona already exists: {existing_id}\n"
            f"existing path: {existing_path.parent}\n"
            "delete it first with: /persona delete <name>\n"
            "or choose a different fused persona name"
        )
    fuse_args = [args.new_persona_name, *args.source_personas, "--personas-dir", str(personas_dir)]
    if args.display_name:
        fuse_args.extend(["--display-name", args.display_name])
    run_script("runtime/fuse_personas.py", fuse_args)
    fused_path = personas_dir / args.new_persona_name / "persona.json"
    run_script("extraction/build_persona_modules.py", [str(fused_path)])
    run_script("extraction/validate_persona.py", [str(fused_path), "--mode", "final"])
    ensure_catalog(personas_dir)
    print(f"fused persona ready: {fused_path}")
    print("status: final (router-ready after catalog refresh)")


def cmd_language(args: argparse.Namespace) -> None:
    session_file = Path(args.session_file).resolve() if args.session_file else default_session_file()
    value = (args.language or "").strip()
    if not value:
        current = get_language_override(session_file)
        if current:
            print(f"Current response language override: {current}")
        else:
            print("Current response language override: <persona default>")
        print(f"Session file: {session_file}")
        return

    if value.casefold() in {"default", "reset", "auto", "clear"}:
        clear_language_override(session_file)
        print("Response language override cleared. Persona replies will use the persona default language.")
        print(f"Session file: {session_file}")
        return

    set_language_override(value, session_file)
    print(f"Response language override set to: {value}")
    print(f"Session file: {session_file}")


def cmd_help(_: argparse.Namespace) -> None:
    lines = [
        "Available /persona commands:",
        "/persona help",
        "  Show this command reference.",
        "/persona language",
        "  Show the current response language override and session file.",
        "/persona language <language>",
        "  Override persona reply language while preserving persona voice and stance.",
        "/persona language default",
        "/persona language reset",
        "  Clear the override and fall back to the persona default language.",
        "/persona list",
        "  List distilled personas. Use CLI flag --all to include templates.",
        "/persona distill <name> <data_dir>",
        "  In the skill workflow this is end-to-end; the CLI helper shown here performs the bootstrap stage used by the assistant.",
        "/persona delete <name>",
        "  Delete a distilled persona by id, display name, or alias. If it does not exist, report that explicitly.",
        "/persona <name>",
        "  Enter persona mode with the default runtime profile.",
        "/persona <name> <scene>",
        "  Enter persona mode with a scene hint: default | decision | conflict | analysis.",
        "/persona switch <name> [scene]",
        "  Explicit alias for persona activation.",
        "/persona fuse <new_name> <name1> <name2> [name3]",
        "  Create a fused final persona from 2-3 existing final personas.",
        "/persona exit",
        "/persona off",
        "/persona quit",
        "  Exit persona mode.",
        "Chinese exit aliases:",
        "退出persona",
        "退出角色",
        "退出skill",
        f"Default persona storage: {DEFAULT_PERSONAS_DIR}",
        f"Runtime session file: {default_session_file()}",
    ]
    print("\n".join(lines))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified persona command interface.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_help = sub.add_parser("help", help="Show all available persona commands")
    p_help.set_defaults(func=cmd_help)

    p_language = sub.add_parser("language", help="Show or set persona response language")
    p_language.add_argument("language", nargs="?", default="")
    p_language.add_argument("--session-file", default=str(default_session_file()))
    p_language.set_defaults(func=cmd_language)

    p_list = sub.add_parser("list", help="List all personas")
    p_list.add_argument("--personas-dir", default=str(DEFAULT_PERSONAS_DIR))
    p_list.add_argument("--all", action="store_true", help="Include templates and non-distilled helper personas")
    p_list.set_defaults(func=cmd_list)

    p_distill = sub.add_parser("distill", help="Scaffold a new agent-authored persona from a data directory")
    p_distill.add_argument("persona_name")
    p_distill.add_argument("data_dir")
    p_distill.add_argument("--display-name", default="")
    p_distill.add_argument("--personas-dir", default=str(DEFAULT_PERSONAS_DIR))
    p_distill.set_defaults(func=cmd_distill)

    p_delete = sub.add_parser("delete", help="Delete a persona")
    p_delete.add_argument("persona_name")
    p_delete.add_argument("--personas-dir", default=str(DEFAULT_PERSONAS_DIR))
    p_delete.set_defaults(func=cmd_delete)

    p_use = sub.add_parser("use", help="Select runtime modules for a persona")
    p_use.add_argument("persona_name")
    p_use.add_argument("scene", nargs="?", default="default")
    p_use.add_argument("--personas-dir", default=str(DEFAULT_PERSONAS_DIR))
    p_use.set_defaults(func=cmd_use)

    p_switch = sub.add_parser("switch", help="Explicitly switch into a persona")
    p_switch.add_argument("persona_name")
    p_switch.add_argument("scene", nargs="?", default="default")
    p_switch.add_argument("--personas-dir", default=str(DEFAULT_PERSONAS_DIR))
    p_switch.set_defaults(func=cmd_use)

    p_fuse = sub.add_parser("fuse", help="Fuse 2-3 final personas into a new final persona")
    p_fuse.add_argument("new_persona_name")
    p_fuse.add_argument("source_personas", nargs="+")
    p_fuse.add_argument("--display-name", default="")
    p_fuse.add_argument("--personas-dir", default=str(DEFAULT_PERSONAS_DIR))
    p_fuse.set_defaults(func=cmd_fuse)

    sub.add_parser("exit", help="Exit persona mode")
    sub.add_parser("off", help="Exit persona mode")
    sub.add_parser("quit", help="Exit persona mode")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command in {"exit", "off", "quit"}:
        print("Persona mode exited.")
        return
    args.func(args)


if __name__ == "__main__":
    main()
