#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def default_runtime_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "store" / "runtime"


def default_session_file() -> Path:
    return default_runtime_dir() / "session.json"


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_session_state(path: Path | None = None) -> Dict[str, Any]:
    session_path = path or default_session_file()
    if not session_path.exists():
        return {}
    return load_json(session_path)


def save_session_state(payload: Dict[str, Any], path: Path | None = None) -> Path:
    session_path = path or default_session_file()
    write_json(session_path, payload)
    return session_path


def get_language_override(path: Path | None = None) -> str:
    state = load_session_state(path)
    return str(state.get("response_language_override", "")).strip()


def set_language_override(language: str, path: Path | None = None) -> Path:
    state = load_session_state(path)
    state["response_language_override"] = language.strip()
    return save_session_state(state, path)


def clear_language_override(path: Path | None = None) -> Path:
    state = load_session_state(path)
    state.pop("response_language_override", None)
    return save_session_state(state, path)
