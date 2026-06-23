# Goal

Rename `rn`'s three command/skill names from `gm` / `bb` / `hi` to `yo` / `pc` / `rw`, carrying new
mnemonic derivations, and update every reference and explanation across the plugin so the commands
and docs stay consistent. The intended mapping and meaning:

| Role | Old | New | Origin | Meaning |
|---|---|---|---|---|
| Start | `gm` | `yo` | "Yo!" | A call to action — "let's get going" |
| Pause | `bb` | `pc` | peace | "see ya / catch you later" — a break point |
| Resume | `hi` | `rw` | rewind | Rewind and run again — return to where you stopped and continue |

The session flow stays the same shape, now named: **yo (start) → pc (pause) → rw (come back)**.

# Acceptance criteria

- The three skill directories are renamed: `skills/gm` → `skills/yo`, `skills/bb` → `skills/pc`,
  `skills/hi` → `skills/rw`, and each `SKILL.md` `name:` frontmatter equals its directory name.
- No occurrence of the old command names (`gm` / `bb` / `hi` as rn commands, or `rn:gm` / `rn:bb` /
  `rn:hi`) remains in any file, **except** inside `CHANGELOG.md` entries that document this rename.
- Every cross-reference is repointed to the new pairing: `pc` tells the user to resume with `rw`,
  `rw` notes the session was started by `yo`, and all flow text reads `yo → pc → rw`.
- `README.md`'s mnemonic section explains the **new** derivations (`yo` = "Yo!" call, `pc` = peace,
  `rw` = rewind) in place of the old greeting story; the install line and all three example sections
  use the new names.
- `references/steering-template.md` and `references/task-workflow.md` use `yo` / `pc` / `rw`.
- `CHANGELOG.md` `[Unreleased]` has an entry describing the rename in user-facing terms.
- `claude plugin validate rn --strict` and `claude plugin validate <marketplace root> --strict` both
  pass.
- The new skill namespaces resolve headlessly (e.g. `/rn:yo`, `/rn:pc`, `/rn:rw`); the old namespaces
  no longer resolve.

# Assumptions

- This rename **supersedes** the earlier-agreed-but-unimplemented naming `gm/bb/hi → rdy/brb/back`;
  that prior proposal is dropped. (Assumption — confirm in PR review.)
- Claude Code requires a skill's `name:` frontmatter to equal its directory name, so renaming a
  directory requires editing its `name:` too. (Fact — Claude Code skills reference.)
- This is a pre-1.0 plugin (`0.4.0`); a command rename is breaking, but on `0.x` the repo's semver
  policy treats it as a minor change. No version bump now — the entry waits under `[Unreleased]` until
  a release instruction. (Fact — `.claude/rules/plugin.md`.)
- No code or docs outside the `rn` plugin reference these command names; the root `README.md` mentions
  the `rn` plugin only generally. (Assumption — verified during task #2.)

# Rules

- commit and push every change; one completion marker per task
- use `git mv` for the directory renames to preserve file history
- when editing `pc` (old `bb`), preserve its marker-detection logic and do **not** write the literal
  phrase "complete task #N" as prose — it falsely triggers `rw`'s resume scan
- old command names persist only where `CHANGELOG.md` documents this rename

# Tasks

### #1: Rename the three skills (directories + SKILL.md content)

**Purpose**: Rename the `gm` / `bb` / `hi` skill directories to `yo` / `pc` / `rw` and update their
`SKILL.md` frontmatter, descriptions, and internal cross-references so the commands work under the new
names.

**Prerequisites**: none

**Steps**:

- [ ] `git mv skills/gm skills/yo`, `git mv skills/bb skills/pc`, `git mv skills/hi skills/rw`
- [ ] set each `SKILL.md` `name:` to match its new directory (`yo` / `pc` / `rw`)
- [ ] update each `SKILL.md` body heading, `typically via /rn:…` text, and descriptions to the new names
- [ ] repoint internal cross-references: `pc` → resume with `rw`; `rw` → started by `yo`
- [ ] self-check (OK/NG per completion criterion, record in checks/{task-id}.md)
- [ ] QA expert review (subagent)
- [ ] user review

**Completion criteria**:

- `skills/yo`, `skills/pc`, `skills/rw` exist; `skills/gm`, `skills/bb`, `skills/hi` do not.
- Each `SKILL.md` `name:` frontmatter equals its directory name.
- No `rn:gm` / `rn:bb` / `rn:hi` (or bare `gm` / `bb` / `hi` as command references) remain anywhere
  under `skills/`.
- `claude plugin validate rn --strict` passes.
- `/rn:yo`, `/rn:pc`, `/rn:rw` resolve as the plugin's skills when run headlessly.

### #2: Update docs and references

**Purpose**: Repoint every supporting document to `yo` / `pc` / `rw` and rewrite the mnemonic
explanation to the new derivations.

**Prerequisites**: #1

**Steps**:

- [ ] `README.md`: install line, the three example sections, the flow line, and the "Why gm/bb/hi?"
      mnemonic section rewritten to `yo` = "Yo!" / `pc` = peace / `rw` = rewind
- [ ] `references/steering-template.md`: the State note (`bb` / `hi` → `pc` / `rw`)
- [ ] `references/task-workflow.md`: opening line and resume reference (`gm` / `hi` → `yo` / `rw`)
- [ ] check the root `README.md` for any old command references and update if present
- [ ] `CHANGELOG.md`: add the rename entry under `[Unreleased]`
- [ ] self-check (OK/NG per completion criterion, record in checks/{task-id}.md)
- [ ] QA expert review (subagent)
- [ ] user review

**Completion criteria**:

- No `gm` / `bb` / `hi` command references remain in any file outside `CHANGELOG.md`'s description of
  this rename.
- `README.md`'s mnemonic section explains `yo` = "Yo!" call, `pc` = peace, `rw` = rewind, and its flow
  text reads `yo → pc → rw`.
- `references/steering-template.md` and `references/task-workflow.md` use the new names.
- `CHANGELOG.md` `[Unreleased]` contains a user-facing entry for the rename.
- `claude plugin validate <marketplace root> --strict` passes.

# Decisions

(none yet)

# State

(written by /rn:pc, read and reset to this placeholder by /rn:rw. `Status` is `paused` while a
session is suspended — the signal /rn:rw and /rn:pc search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
