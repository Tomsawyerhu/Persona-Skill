# Extraction Notes

Use this folder as the working directory for one persona.

Recommended order:

1. Set corpus metadata in extractor_config.json
2. Inspect the raw corpus directory directly
3. Use the dimension template as a scaffold, then prune unsupported dimensions
4. Decide evidence, voice, and scenarios from actual source reading
5. Author persona.json from persona.template.json
6. Validate with validate_persona.py
7. Build runtime modules with build_persona_modules.py

Do not generate keyword candidates or heuristic evidence packs.
Use only source-grounded reading and manual synthesis.
Do not leave the persona as an empty scaffold if the intent is full distillation.

Keep source ids, evidence ids, and scenario ids stable once the artifact is in use.
