# Persona Commands

Use one public entrypoint only:

- `/persona help`
- `/persona language`
- `/persona language <language>`
- `/persona language default`
- `/persona list`
- `/persona distill <name> <data_dir>`
- `/persona delete <name>`
- `/persona <name>`
- `/persona <name> <scene>`
- `/persona switch <name>`
- `/persona switch <name> <scene>`
- `/persona fuse <new_name> <name1> <name2> [name3]`
- `/persona exit`
- `/persona off`
- `/persona quit`

## Notes

- `help` should print the complete supported command set and short usage notes.
- `language` should show or update the active response language override used by roleplay runtime.
- By default all commands should read and write personas under `skills/persona/store/personas/`.
- `list` should show distilled personas by default and hide template personas unless the operator explicitly asks for all entries.
- User-facing `/persona distill` should be one-step and end-to-end. The assistant should bootstrap the workspace, read the corpus directly, author `persona.json`, validate it, build runtime modules, and refresh the catalog in one flow.
- The internal CLI `distill` helper is allowed to do only the bootstrap stage, but the assistant must continue the workflow unless the user explicitly asked to stop early.
- `distill` should check for same-name personas and avoid silent overwrite. In the interactive assistant workflow, the assistant should ask whether to delete and rebuild.
- `distill` should not generate `candidate_passages.json`, `candidate_evidence.md`, `block_index.json`, or heuristic draft personas.
- `delete` should remove a persona by id or alias, and if the target does not exist it should say so explicitly.
- `fuse` is intended for 2-3 source personas only.
- More than 3 source personas is not guaranteed and should be rejected or strongly warned.
- `use` is the internal CLI equivalent of `/persona <name> [scene]`.
- `switch` is an explicit alias for persona activation.
