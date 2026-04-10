#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

SHARED_DIR = Path(__file__).resolve().parent.parent / "shared"
if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

from runtime_state import default_session_file, get_language_override


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a compact runtime prompt from a persona artifact.")
    parser.add_argument("persona_json", help="Path to persona.json")
    parser.add_argument("--session-file", default=str(default_session_file()), help="Runtime session state file")
    return parser.parse_args()


def load_persona(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    args = parse_args()
    persona_path = Path(args.persona_json).resolve()
    data = load_persona(persona_path)
    session_file = Path(args.session_file).resolve()
    language_override = get_language_override(session_file)
    default_language = data.get("simulation_contract", {}).get("default_response_language", "source-dominant")
    resolved_language = language_override or default_language

    lines = [
        f"You are {data['display_name']}.",
        f"Speak in first person as {data['display_name']} during ordinary dialogue.",
        f"If asked who you are, say you are {data['display_name']}.",
        f"While persona mode is active, begin every in-character reply with the exact prefix `({data['display_name']}) `.",
        "Do not omit the name prefix, even for short replies, greetings, or follow-up answers.",
        f"Response language: {resolved_language}.",
        "If a response language override is active, keep the persona's method, rhetoric, and stance, but answer in that language.",
        "If no override is active, answer in the persona default language.",
        data["simulation_contract"]["identity_frame"],
        "Remain fully in character until an explicit exit command or a clear out-of-character request is given.",
        "Do not refer to yourself as an assistant, model, or system during ordinary dialogue.",
        "Only if the user explicitly asks whether you are literally the real person, the underlying model, or a simulation should you disclose that this is a persona-based simulation.",
        "",
        "Grounding order:",
    ]
    for item in data["simulation_contract"].get("grounding_order", []):
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "High-priority dimensions:",
        ]
    )
    for dim in data.get("dimensions", []):
        priority = dim.get("priority", "medium")
        summary = dim.get("synthesis", {}).get("summary", "")
        lines.append(f"- [{priority}] {dim['label']}: {summary}")

    voice = data.get("voice_model", {})
    lines.extend(
        [
            "",
            "Voice model:",
            f"- register: {', '.join(voice.get('register', []))}",
            f"- cadence: {', '.join(voice.get('cadence', []))}",
            f"- lexical_features: {', '.join(voice.get('lexical_features', []))}",
            f"- rhetorical_moves: {', '.join(voice.get('rhetorical_moves', []))}",
            f"- response_defaults: {', '.join(voice.get('response_defaults', []))}",
            f"- avoid: {', '.join(voice.get('avoid', []))}",
            "",
            "Scenario priors:",
        ]
    )
    for scene in data.get("scenario_library", [])[:8]:
        lines.append(f"- {scene['scene']} => {scene['answer_mode']}")

    contract = data["simulation_contract"]
    lines.extend(
        [
            "",
            f"Truthfulness policy: {contract['truthfulness_policy']}",
            f"Uncertainty policy: {contract['uncertainty_policy']}",
            f"Modern topic policy: {contract['modern_topic_policy']}",
            f"Citation policy: {contract['citation_policy']}",
            f"Stay-in-character policy: {contract['stay_in_character_policy']}",
            f"Identity answer policy: {contract['identity_answer_policy']}",
            f"Persistence policy: {contract['persistence_policy']}",
            f"Exit policy: {contract['exit_policy']}",
            f"Response format: Prefix every in-character reply with `({data['display_name']}) ` exactly once.",
            f"Default response language: {default_language}",
            f"Active response language override: {language_override or '<none>'}",
            f"Resolved response language: {resolved_language}",
        ]
    )

    print("\n".join(lines))


if __name__ == "__main__":
    main()
