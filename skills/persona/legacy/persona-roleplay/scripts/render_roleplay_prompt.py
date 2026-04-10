#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a compact runtime prompt from a persona artifact.")
    parser.add_argument("persona_json", help="Path to persona.json")
    return parser.parse_args()


def load_persona(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    args = parse_args()
    persona_path = Path(args.persona_json).resolve()
    data = load_persona(persona_path)

    lines = [
        f"You are simulating the persona of {data['display_name']}.",
        data["simulation_contract"]["identity_frame"],
        "Stay fully in character unless an explicit exit command or an out-of-character request is given.",
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
        ]
    )

    print("\n".join(lines))


if __name__ == "__main__":
    main()
