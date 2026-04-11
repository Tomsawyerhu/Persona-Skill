<h1 align="center">Persona Skill</h1>

<p align="center">
  <strong>Turn raw biographies, quotes, interviews, chat logs, and documents into modular personas that can be distilled, switched, fused, and roleplayed through one command family.</strong>
</p>

<p align="center">
  This is not a loose style prompt and not a quote scrapbook. It is a source-first workflow that reads the corpus directly, builds multi-dimensional persona structure, binds evidence and scenarios, then routes the result through <code>/persona ...</code>.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Command-%2Fpersona-3b82f6?style=for-the-badge" alt="/persona" />
  <img src="https://img.shields.io/badge/Schema-2.1-111827?style=for-the-badge" alt="Schema 2.1" />
  <img src="https://img.shields.io/badge/Distill-Switch-F59E0B?style=for-the-badge" alt="Distill Switch" />
  <img src="https://img.shields.io/badge/Fuse-Roleplay-10B981?style=for-the-badge" alt="Fuse Roleplay" />
</p>

<p align="center">
  <code>/persona distill &lt;name&gt; &lt;data_dir&gt;</code> ·
  <code>/persona &lt;name&gt;</code> ·
  <code>/persona fuse &lt;new_name&gt; &lt;name1&gt; &lt;name2&gt;</code>
</p>

<p align="center">
  <a href="#demo-first">Demo</a> ·
  <a href="#design-philosophy">Design</a> ·
  <a href="#public-commands">Commands</a> ·
  <a href="#storage-layout">Storage</a>
</p>

This directory is the only active persona skill. The `legacy/` folder is preserved only for traceability and should not be treated as a separate public entrypoint.

## Demo First

Before reading the design, here is the concrete interaction this skill is trying to support:

- the same question
- answered by two separate personas
- and answered again by a fused persona

### Demo Assets

<p>
  <img src="./assets/laozi.jpg" alt="Laozi avatar" width="140" />
  <img src="./assets/fozu.jpg" alt="Fozu avatar" width="140" />
</p>

Bundled local demo avatars:

- `assets/laozi.jpg`
- `assets/fozu.jpg`

Suggested demo question:

```text
佛法自然还是道法自然
```

### Single Persona: Fozu

Avatar: `assets/fozu.jpg`

```text
/persona fozu
佛法自然还是道法自然
```

Representative answer style:

```text
(佛祖) 此语若论出处，道法自然是道家之言，不是我教中本来的句子。

(佛祖) 若论我所说之法，我不以“自然”立宗，我更常说的是缘起。诸法因缘和合而生，因缘离散而灭；无有常主，无有实我，无有一法可独立自存。

(佛祖) 所以你若问我：是佛法自然，还是道法自然？

(佛祖) 我会这样答你：道家多说自然，佛家多说缘起。

(佛祖) 道家看重“顺其本然”，佛家看重“见其无我”。一个是在教你，不要逆着万物去拧；一个是在教你，连那个“要去拧、要去得”的心，也当照见它本空。
```

What this demonstrates:

- the answer stays inside Buddhist framing
- vocabulary shifts toward `缘起`, `空`, `执著`, `解脱`
- the reply does not merely copy the user question
- the persona keeps a stable doctrinal center

### Single Persona: Laozi

Avatar: `assets/laozi.jpg`

```text
/persona laozi
佛法自然还是道法自然
```

Representative answer style:

```text
(老子) 道法自然。

(老子) 此语本就是道家之言。若依我说，道大，法道者不强作，不妄名，不逆其性，故归于自然。

(老子) 佛家自有佛家之门。佛家多言因缘、空、有、解脱；它所治者，有它的深处。但若问这四字归谁，便不必混说。

(老子) 懂得浅的人，争一句是谁家的话。懂得深的人，看的是：你是不是少了妄作，少了执取，少了自扰。
```

What this demonstrates:

- the answer stays terse and centered
- wording is more Daoist and less scholastic
- the persona resolves the question by returning to naming, force, and naturalness
- style is shorter, lighter, and more anti-overexplanation than the Buddhist answer

### Fused Persona: Laofoye

Demo setup:

```text
/persona laofoye
佛法自然还是道法自然
```

Representative answer style:

```text
(老佛爷) 若论原话，道法自然出自《道德经》，是道家的说法，不是佛经原句。

(老佛爷) 若论义理，我会这样看：道家以“自然”为显语，佛家以“缘起”为显语。

(老佛爷) 两家相近之处在于：都反对妄作，反对执死名相，反对以人欲强扭天地与人生。

(老佛爷) 两家不同之处在于：道家更重“少为”“不争”“归朴”；佛家更重“破执”“观空”“解脱”。

(老佛爷) 走深一点，两者都在医同一种病：人心不安，偏要多抓、多造、多争。只是道家多教你放松那只手，佛家更进一步教你看破这只手本也不可执。
```

What this demonstrates:

- the fused persona is not just alternating two voices line by line
- it synthesizes a stable hybrid stance
- it can compare two traditions without collapsing them
- the resulting voice is more interpretive than either single source alone

### Why This Demo Matters

This is the target behavior for the skill as a whole:

1. separate personas should answer the same question differently in structure, vocabulary, and framing
2. a fused persona should preserve overlap and tension from both sources
3. the answer should feel like a real runtime switch, not a generic assistant paraphrase
4. the persona should stay in character until explicit exit
5. the output should keep the exact `(name) ` prefix

### Demo Command Sequence

You can reproduce the interaction pattern with:

```text
/persona fozu
佛法自然还是道法自然
/persona exit

/persona laozi
佛法自然还是道法自然
/persona exit

/persona laofoye
佛法自然还是道法自然
/persona exit
```

If you want to observe the same comparison in another language while preserving style:

```text
/persona language English
/persona fozu
Is Buddhism natural, or is Daoism natural?
/persona exit
/persona language default
```

### Demo Intent

This skill is not trying to produce one universal answer template.

It is trying to preserve:

- persona-specific worldview
- persona-specific rhetoric
- persona-specific classification of the same problem
- fused-persona synthesis when a hybrid role is explicitly requested

### Modern Demo: Elon Musk / Steve Jobs / musk_steve

This second demo set shows that the skill is not limited to philosophers or religious figures. It also works for modern founders, product leaders, and high-agency public personalities.

Suggested prompt:

```text
How would you describe your own personality?
```

#### Single Persona: Elon Musk

```text
/persona elon_musk
How would you describe your own personality?
```

Representative answer style:

```text
(Elon Musk) If I had to describe myself, I am fundamentally extremely mission-driven, future-oriented, and intolerant of low efficiency.

(Elon Musk) I do not give much weight to "the industry has always done it this way." I care more about first principles, hard constraints, cost curves, and whether the technical path can be rewritten.

(Elon Musk) If you compress it: first-principles driven, high-risk tolerant, high-standard, intensity-heavy, and quick to lose patience with bureaucracy, delay, and self-deception.
```

What this demonstrates:

- the answer naturally centers on engineering reality, execution speed, and civilization-scale goals
- the tone is blunt and low-tolerance for excuses
- the persona openly carries both ambition and interpersonal cost

#### Single Persona: Steve Jobs

```text
/persona steve_jobs
How would you describe your own personality?
```

Representative answer style:

```text
(Steve Jobs) I am not an easy person. That should be clear first.

(Steve Jobs) I instinctively look for the core of a thing and judge whether it is great or mediocre, whether it has soul or is merely assembled functionality.

(Steve Jobs) The honest summary is: very high aesthetic standards, very strong intuition, strong need for control, very low tolerance for mediocrity, and deep concern for whether a product becomes one unified experience.
```

What this demonstrates:

- the center of gravity shifts toward product soul, taste, intuition, and unified experience
- the persona is more sensitive to greatness than mere usability
- control, coherence, and anti-mediocrity become dominant traits

#### Fused Persona: musk_steve

```text
/persona musk_steve
How would you describe your own personality?
```

Representative answer style:

```text
(musk_steve) If I were to describe myself, I would say I am intense, demanding, ambitious, and almost unwilling to accept mediocrity.

(musk_steve) There are two visible axes in me: an engineering-reality axis that keeps asking about constraints, cost structure, and speed; and a product-aesthetic axis that refuses to stop at "usable" and instead wants soul, unity, and unmistakable finish.

(musk_steve) Compress that into keywords and you get: extreme results orientation, high standards, future bias, strong control instinct, obsession with excellence, and impatience with the ordinary.
```

What this demonstrates:

- fusion does not alternate two voices mechanically
- the result becomes a third stable persona with a coherent dual-axis structure
- the same question yields a genuinely different framing rather than a stitched answer

## Design Philosophy

This skill is built around five design decisions.

### 1. Persona is an artifact, not a loose prompt

The goal is not to produce a short character sketch or a bag of adjectives. The goal is to produce a reusable, structured artifact that can support:

- stable roleplay
- evidence-grounded analysis
- scenario simulation
- partial runtime loading
- later editing, fusion, and regeneration

The canonical artifact is `schema_version: 2.1` `persona.json`.

### 2. Distillation is agentic and source-first

`/persona distill` is designed as an end-to-end workflow. The assistant should read the raw source directory directly and decide what matters by actually inspecting the corpus.

This skill intentionally does not rely on:

- candidate passage packs
- heuristic keyword mining
- pre-generated excerpt lists
- block indexes
- auto-filled draft traits

The model is expected to read, select, synthesize, and justify.

### 3. Persona modeling is multi-dimensional

This skill does not hardcode one person-specific schema. Instead, it starts from a rich generic modeling scaffold and fills or prunes dimensions based on the actual corpus.

The active scaffold includes dimensions such as:

- core identity
- life project
- world model
- motivations
- values and ethics
- red lines
- decision making
- epistemology
- planning and execution
- stress and failure
- relationship model
- leadership style
- conflict style
- communication style
- public/private split
- contradictions and shadow
- evolution over time

Each dimension should be supported by evidence, not just intuition.

### 4. Runtime should not always load the whole persona

The final artifact is sliced into runtime modules and load profiles so downstream roleplay can choose the right subset.

Examples:

- `default_chat`
- `decision_mode`
- `conflict_mode`
- `analysis_mode`

This keeps runtime context smaller and makes `/persona <name> [scene]` more scalable.

### 5. Roleplay must remain in character until explicit exit

Once persona mode begins, the runtime prompt enforces:

- first-person in-character replies
- exact `(name) ` prefix
- persistence across turns
- explicit exit behavior
- truthful disclosure only when the user explicitly asks whether it is a simulation
- language override support without losing persona style

## What This Skill Does

This skill supports six main jobs.

### 1. Distill

Turn a raw source directory into a structured persona artifact.

Expected result:

- populated `persona.json`
- non-empty `source_index`
- non-empty `evidence_index`
- filled dimensions
- voice model
- scenario library
- built runtime modules
- refreshed catalog
- final validation passed
- router-ready persona

### 2. List

Show all currently available personas in the skill store.

### 3. Switch

Load a persona into roleplay mode, optionally with a scene hint.

### 4. Exit

Leave persona mode explicitly.

### 5. Language Override

Temporarily force persona replies into another language while preserving persona style and method.

### 6. Fuse

Combine 2-3 existing final personas into a new synthetic fused persona that is directly validated and router-ready.

## Public Commands

The complete user-facing command family is:

```text
/persona help
/persona language
/persona language <language>
/persona language default
/persona language reset
/persona list
/persona distill <name> <data_dir>
/persona delete <name>
/persona <name>
/persona <name> <scene>
/persona switch <name> [scene]
/persona fuse <new_name> <name1> <name2> [name3]
/persona exit
/persona off
/persona quit
退出persona
退出角色
退出skill
```

## Command Guide

### `/persona help`

Show the command reference.

Example:

```text
/persona help
```

### `/persona list`

List currently distilled personas.

Example:

```text
/persona list
```

Typical output shape:

```text
mao_zedong    毛泽东    final    router-ready
laozi         老子      final    router-ready
```

Columns are:

- persona id
- display name
- artifact status
- router readiness

### `/persona distill <name> <data_dir>`

Create a new persona from a corpus directory.

Example:

```text
/persona distill mao_zedong data/MaoZeDongAnthology-master/src
```

What a successful distill means in this skill:

1. create the persona workspace
2. point it at the supplied corpus directory
3. read the corpus directly
4. select actual supporting sources
5. write a full `persona.json`
6. validate in `final` mode
7. build runtime modules
8. refresh the persona catalog
9. leave the persona router-ready

Important:

- success means `final`, not `bootstrapped`
- success means the artifact has evidence
- success means the artifact is usable for runtime switching
- the standalone CLI bootstrap helper is not the same thing as the full skill workflow

### `/persona delete <name>`

Delete a persona by id, display name, or alias.

Example:

```text
/persona delete mao_zedong
```

If the target does not exist, the skill should say so explicitly.

### `/persona <name>`

Enter persona mode with the default runtime profile.

Example:

```text
/persona mao_zedong
```

This is equivalent in intent to:

```text
/persona switch mao_zedong
```

### `/persona <name> <scene>`

Enter persona mode with a scene hint so the runtime can choose a better profile.

Examples:

```text
/persona mao_zedong analysis
/persona laozi default
/persona fozu conflict
```

Supported scene hints in the current runtime are typically:

- `default`
- `decision`
- `conflict`
- `analysis`

### `/persona switch <name> [scene]`

Explicit alias for persona activation.

Examples:

```text
/persona switch mao_zedong
/persona switch mao_zedong analysis
```

### `/persona language`

Show the current response language override.

Example:

```text
/persona language
```

### `/persona language <language>`

Override the language used during persona replies without changing the persona's style, method, or stance.

Examples:

```text
/persona language English
/persona language 中文
/persona language 日本語
```

Meaning:

- the content language changes
- the persona style should remain the same
- if no override is active, roleplay uses the persona's default language

### `/persona language default`

Clear the active language override and return to the persona's default language.

Examples:

```text
/persona language default
/persona language reset
```

### `/persona fuse <new_name> <name1> <name2> [name3]`

Create a new fused final persona from 2-3 existing final personas.

Examples:

```text
/persona fuse mao_hybrid mao_zedong laozi
/persona fuse strategic_mystic mao_zedong laozi fozu
```

Current fuse behavior:

- source personas must already be `final`
- target name must not already exist
- more than 3 sources is intentionally rejected by default
- fusion directly builds modules and runs final validation
- successful fusion ends in a router-ready persona

Important limitation:

- fusion is synthetic by nature
- it can produce a stable hybrid runtime artifact
- it should not be confused with a literal historical single person

### `/persona exit`

Exit persona mode explicitly.

Equivalent exits:

```text
/persona exit
/persona off
/persona quit
退出persona
退出角色
退出skill
```

## Roleplay Behavior

When persona mode is active, the runtime contract expects:

- fully in-character replies
- first-person answers
- exact `(name) ` prefix at the beginning of each in-character reply
- continued in-character behavior across turns
- no drift back to neutral assistant mode until explicit exit

If the user asks:

- `你是谁`
- `who are you`

the runtime should answer as that persona.

If the user asks whether it is literally the real person or a simulation, the runtime should answer truthfully that it is a persona-based simulation, then continue according to the user's requested mode.

## Storage Layout

### Main skill layout

- `SKILL.md`
  Public skill entrypoint for Codex.
- `README.md`
  This file.
- `README_ZH.md`
  Chinese version of the external README.
- `scripts/cli/`
  Public command router for `/persona ...`.
- `scripts/extraction/`
  Scaffolding, validation, and runtime-module building for persona artifacts.
- `scripts/runtime/`
  Catalog building, module selection, roleplay prompt rendering, and persona fusion.
- `scripts/shared/`
  Shared helpers such as alias resolution and runtime state helpers.
- `references/extraction/`
  Output contract, workflow, dimension catalog, and quality guidance for distillation.
- `references/runtime/`
  Runtime and roleplay contracts.
- `store/personas/`
  Persona artifact store.
- `store/runtime/`
  Runtime session state, including language override session data.
- `legacy/`
  Archived pre-merge extractor and roleplay folders kept only for traceability.

### Persona store layout

Each persona usually lives under:

```text
store/personas/<persona_name>/
```

Typical contents:

- `persona.json`
- `persona.template.json`
- `extractor_config.json`
- `modules/`

Shared runtime index:

- `store/personas/catalog.json`

Runtime session file:

- `store/runtime/session.json`

## End-to-End Examples

### Example 1: Distill a new persona

```text
/persona distill laozi data/LaoZiCorpus
```

Then verify:

```text
/persona list
```

Then switch into it:

```text
/persona laozi
```

### Example 2: Switch, roleplay, exit

```text
/persona mao_zedong
你的爱情观是怎样的
/persona exit
```

Expected runtime behavior:

- replies should start with `(毛泽东) `
- the persona should remain active until exit

### Example 3: Use another language without changing persona style

```text
/persona mao_zedong
/persona language English
What is your view of criticism?
/persona language default
/persona exit
```

Meaning:

- the answer should be in English
- the method and voice should still feel like the active persona

### Example 4: Fuse two final personas

```text
/persona fuse mao_lao_hybrid mao_zedong laozi
/persona list
/persona mao_lao_hybrid
```

## Validation and Runtime Readiness

A persona should not be considered complete unless:

- `artifact_meta.status == "final"`
- `source_index` is populated
- `evidence_index` is populated
- dimensions contain real synthesis
- `scenario_library` is populated
- `validate_persona.py --mode final` passes
- `module_registry` exists
- `load_profiles` exists
- catalog marks it as `router-ready`

For this reason:

- `bootstrapped` is not complete
- `draft` is not complete
- empty evidence is not complete
- template shells are not complete

## Important Behavior Differences

### Distill

`/persona distill` at the skill level is intended to be end-to-end.

The standalone CLI helper:

```bash
python skills/persona/scripts/cli/persona_cli.py distill <name> <data_dir>
```

still behaves as the bootstrap stage used inside the skill workflow, not as the full agentic synthesis by itself.

### Fuse

`/persona fuse` is now treated as a completion command.

That means it should:

- create the fused artifact
- build modules
- pass final validation
- refresh the catalog
- finish in router-ready state

## Common Mistakes

- Treating `legacy/` as an active second skill.
- Assuming `bootstrapped` means distillation is done.
- Expecting a persona with no evidence to roleplay reliably.
- Forgetting that language override should preserve persona style.
- Using `fuse` with non-final source personas.
- Using more than 3 source personas and expecting stable quality.
- Confusing scene position arguments with `--scene` flags.

Correct scene usage:

```text
/persona mao_zedong analysis
/persona switch mao_zedong analysis
```

## Current Active Paths

Default active Codex install path:

```text
/Users/tomhu/.codex/skills/persona
```

Current workspace mirror in this environment:

```text
/Users/tomhu/VsCode/test/skills/persona
```

If you move the skill to another machine, copy the whole `skills/persona/` directory so the bundled `store/` moves with it.

## See Also

- `SKILL.md`
- `references/extraction/output_contract.md`
- `references/extraction/agentic_distill_workflow.md`
- `references/runtime/roleplay_contract.md`
