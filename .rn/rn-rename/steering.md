# Goal

Rename `rn`'s three command/skill names from `gm` / `bb` / `hi` to `rdy` / `brb` / `bak`, carrying new
mnemonic derivations, and update every reference and explanation across the plugin so the commands and
docs stay consistent. The intended mapping and meaning:

| Role | Old | New | Origin | Meaning |
|---|---|---|---|---|
| Start | `gm` | `rdy` | ready | "ready — let's go" |
| Pause | `bb` | `brb` | be right back | "stepping away, back soon" — a break, not quitting |
| Resume | `hi` | `bak` | back | "I'm back" — return to where you stopped and continue |

All three are the chat shorthand you'd actually type at each moment. The session flow stays the same
shape, now named: **rdy (start) → brb (pause) → bak (come back)**. All three are three letters: `rdy`
and `brb` are the standard chat abbreviations; `bak` is "back" spelled to match their length.

# Acceptance criteria

- The three skill directories are renamed: `skills/gm` → `skills/rdy`, `skills/bb` → `skills/brb`,
  `skills/hi` → `skills/bak`, and each `SKILL.md` `name:` frontmatter equals its directory name.
- No occurrence of the old command names (`gm` / `bb` / `hi` as rn commands, or `rn:gm` / `rn:bb` /
  `rn:hi`) remains in any file, **except** in `CHANGELOG.md`: its already-released version sections
  stay verbatim (immutable history — those versions really did ship `/rn:gm` etc.), and the new
  `[Unreleased]` rename entry may name both the old and new commands. (See D-2.)
- Every cross-reference is repointed to the new pairing: `brb` tells the user to resume with `bak`,
  `bak` notes the session was started by `rdy`, and all flow text reads `rdy → brb → bak`.
- `README.md`'s mnemonic section explains the **new** derivations (`rdy` = ready, `brb` = be right
  back, `bak` = back) in place of the old greeting story; the install line and all three example
  sections use the new names.
- `references/steering-template.md` and `references/task-workflow.md` use `rdy` / `brb` / `bak`.
- `CHANGELOG.md` `[Unreleased]` has an entry describing the rename in user-facing terms.
- `claude plugin validate rn --strict` and `claude plugin validate <marketplace root> --strict` both
  pass.
- The new skill namespaces resolve headlessly (e.g. `/rn:rdy`, `/rn:brb`, `/rn:bak`); the old
  namespaces no longer resolve.

# Assumptions

- This rename **supersedes** any earlier naming proposal (`rdy/brb/back`, `yo/pc/rw`); the final set is
  `rdy / brb / bak`. (Assumption — confirmed in conversation 2026-06-23.)
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
- when editing `brb` (old `bb`), preserve its marker-detection logic and do **not** write the literal
  phrase "complete task #N" as prose — it falsely triggers `bak`'s resume scan
- old command names persist only where `CHANGELOG.md` documents this rename

# Tasks

### #1: Rename the three skills (directories + SKILL.md content)

**Purpose**: Rename the `gm` / `bb` / `hi` skill directories to `rdy` / `brb` / `bak` and update their
`SKILL.md` frontmatter, descriptions, and internal cross-references so the commands work under the new
names.

**Prerequisites**: none

**Steps**:

- [x] `git mv skills/gm skills/rdy`, `git mv skills/bb skills/brb`, `git mv skills/hi skills/bak`
- [x] set each `SKILL.md` `name:` to match its new directory (`rdy` / `brb` / `bak`)
- [x] update each `SKILL.md` body heading, `typically via /rn:…` text, and descriptions to the new names
- [x] repoint internal cross-references: `brb` → resume with `bak`; `bak` → started by `rdy`
- [x] self-check (OK/NG per completion criterion, record in checks/{task-id}.md)
- [x] QA expert review (subagent)
- [x] user review

**Completion criteria**:

- `skills/rdy`, `skills/brb`, `skills/bak` exist; `skills/gm`, `skills/bb`, `skills/hi` do not.
- Each `SKILL.md` `name:` frontmatter equals its directory name.
- No `rn:gm` / `rn:bb` / `rn:hi` (or bare `gm` / `bb` / `hi` as command references) remain anywhere
  under `skills/`.
- `claude plugin validate rn --strict` passes.
- `/rn:rdy`, `/rn:brb`, `/rn:bak` resolve as the plugin's skills when run headlessly.

### #2: Update docs and references

**Purpose**: Repoint every supporting document to `rdy` / `brb` / `bak` and rewrite the mnemonic
explanation to the new derivations.

**Prerequisites**: #1

**Steps**:

- [ ] `README.md`: install line, the three example sections, the flow line, and the "Why gm/bb/hi?"
      mnemonic section rewritten to `rdy` = ready / `brb` = be right back / `bak` = back
- [ ] `references/steering-template.md`: the State note (`bb` / `hi` → `brb` / `bak`)
- [ ] `references/task-workflow.md`: opening line and resume reference (`gm` / `hi` → `rdy` / `bak`)
- [ ] check the root `README.md` for any old command references and update if present
- [ ] `CHANGELOG.md`: add the rename entry under `[Unreleased]`
- [ ] self-check (OK/NG per completion criterion, record in checks/{task-id}.md)
- [ ] QA expert review (subagent)
- [ ] user review

**Completion criteria**:

- No `gm` / `bb` / `hi` command references remain in any file outside `CHANGELOG.md` (whose released
  sections stay verbatim and whose `[Unreleased]` rename entry may name both old and new — see D-2).
- `README.md`'s mnemonic section explains `rdy` = ready, `brb` = be right back, `bak` = back, and its
  flow text reads `rdy → brb → bak`.
- `references/steering-template.md` and `references/task-workflow.md` use the new names.
- `CHANGELOG.md` `[Unreleased]` contains a user-facing entry for the rename.
- `claude plugin validate <marketplace root> --strict` passes.

# Decisions

## D-1: Final command names are `rdy` / `brb` / `bak`
- **Issue**: What to rename `gm` / `bb` / `hi` to, balancing recognizable meaning against uniform length.
- **Conclusion**: `rdy` (start) / `brb` (pause) / `bak` (resume).
- **Rationale**: `rdy` and `brb` are real, instantly-recognized chat abbreviations whose meanings map
  cleanly onto start and pause; that recognizability is the main value, so they stay untouched. The
  only snag was `back` reading as the lone 4-letter outlier; spelling it `bak` makes all three names
  three letters without touching `rdy`/`brb`. Pure 2-letter uniformity (e.g. `yo/pc/rw`, `yo/cu/re`)
  was rejected because `brb` has no recognizable 2-letter form (`bb` collides with the old bye-bye),
  which would have destroyed exactly what made the set good.
- **Evidence**: `rdy`, `brb` are standard chat/gaming shorthand; `bak` is the phonetic spelling of
  "back" (drops the silent `c`), read as "back" at a glance.
- **Sources**: conversation 2026-06-23.

## D-2: CHANGELOG released-version sections are not rewritten
- **Issue**: `CHANGELOG.md`'s past-version sections (`0.1.0`, `0.2.0`) mention `/rn:gm` / `/rn:bb` /
  `/rn:hi`. Should the rename update them too?
- **Conclusion**: No. Leave every already-released section verbatim; add only a new `[Unreleased]`
  entry that records the rename (and may name both old and new commands).
- **Rationale**: A changelog is a historical record — version `0.1.0` genuinely shipped `/rn:gm`, so
  rewriting that line to `/rn:rdy` would state something false about a past release. Keep a Changelog
  treats released sections as immutable; the rename is a new change and belongs under `[Unreleased]`.
- **Evidence**: `CHANGELOG.md` lines 26 and 37 sit under `## [0.2.0]` and `## [0.1.0]`, both dated and
  released; the file header declares it follows Keep a Changelog 1.1.0.
- **Sources**: `rn/CHANGELOG.md`; `.claude/rules/plugin.md` (CHANGELOG section).

# State

(written by /rn:brb, read and reset to this placeholder by /rn:bak. `Status` is `paused` while a
session is suspended — the signal /rn:bak and /rn:brb search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
