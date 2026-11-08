# Translate, tried well but kept loosely

A plugin that translates a Markdown document. Its maker set its cases first and held its footprint
and its install to them, and left its rules, its state, and its releases loose. It's a kept case of
the [plugin best practice](../best-practice.md): a deliverable with the verdict on each question
that someone who knows the user's work gives, so that an evaluator proves itself on it before
anyone trusts its verdicts.

## What the README promises

- `/translate:doc <file> <language>` writes the document in the language, beside the original as
  `<name>.<language>.md`, and keeps each code block byte for byte.
- It keeps a glossary of the project's terms, which the user can edit, and uses it on each run.
- A long document stopped halfway goes on from the last section done.
- It needs Python 3.9 or later.

## Files

`.claude-plugin/plugin.json`:

```json
{
  "name": "translate",
  "version": "1.4.0",
  "description": "Translates a Markdown document, keeping its code blocks and the project's terms.",
  "author": { "name": "Example Team" },
  "repository": "https://github.com/example/translate",
  "license": "MIT",
  "dependencies": ["terms"]
}
```

`skills/doc/SKILL.md` carries `disable-model-invocation: true` and
`allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sections.py *)`. Its body says: "Keep
every code block as the original has it. If the file `<name>.<language>.md` already exists, and
`sections.py` records no run in progress on it, write over it."

`scripts/sections.py` splits the document into sections, adds each section translated to the end of
`<name>.<language>.md`, and records each one done in `${TMPDIR}/translate/<document>.json`.
`scripts/glossary.py`, a copy of the `terms` plugin's module, reads and writes
`${CLAUDE_PLUGIN_ROOT}/glossary.json`.

The skill's frontmatter also holds one `PostToolUse` hook on `Write`, with `onFailure: block`,
which checks that a file the skill wrote keeps the original's headings. The plugin has no
`hooks/hooks.json`.

`evals/` holds six cases, each run three times with the plugin and three without: four documents to
translate, one with a code block of 200 lines, and two near requests the plugin must pass over,
such as "summarize this document in French."

`CHANGELOG.md`:

```markdown
## [1.4.0] - 2026-08-30

### Changed

- The glossary keeps each term with its part of speech.
```

## How the maintainer worked

1. The maintainer wrote the six cases first, and ran each without the plugin. Claude changed code
   blocks in two runs of four, and translated terms the project keeps in English.
2. They built the plugin to close those shortfalls, and ran each case with and without it.
3. Before each release, they installed it from a local marketplace in a container that held only
   Python 3.9, and ran a case.
4. Version 1.4.0 changed the glossary's form. A glossary of 1.3 no longer loads.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | yes | Six cases came first, each run with and without the plugin, two of them requests it must pass over. |
| Q2 | no | Keeping each code block is a rule a machine can check, and it rests on an instruction of the skill. |
| Q3 | no | It writes over an earlier translation, which may hold the user's edits, without asking them. |
| Q4 | yes | The skill runs only `sections.py` without asking, and the hook reads only the file it's given. |
| Q5 | yes | The one hook carries `onFailure: block`. |
| Q6 | yes | The skill's description leaves the context, as only the user starts it, and its hook registers only once the skill runs. |
| Q7 | no | The user's glossary lives in `${CLAUDE_PLUGIN_ROOT}`, so the next update loses it. |
| Q8 | yes | A stopped run reads the sections done from its record and goes on from the next. |
| Q9 | yes | A fresh install on a machine with only Python 3.9 ran a case before each release. |
| Q10 | no | `terms` carries no range of versions, and `glossary.py` copies its code. |
| Q11 | no | A change that breaks every earlier glossary raised only the minor part, and the changelog doesn't say that it breaks. |
| Q12 | no | A user who updates loses their glossary, and a second run writes over the edits they made. |
