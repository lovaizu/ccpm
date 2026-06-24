# Goal

The `rn` plugin's three commands still don't read naturally, so rename them to a short, consistent
set that mirrors how a work session actually moves: start it, take it down, bring it back up.

- `rdy` → `on` — start a session ("power on")
- `brb` → `dn` — suspend a session ("bring it down")
- `bak` → `up` — resume a session ("bring it back up")

The rename must be complete and coherent: every reference inside the plugin uses the new names, the
cross-references between the three skills resolve, the docs read naturally, and structural validation
still passes. History (the prior rename's records and the shipped `0.5.0` changelog entry) is
preserved, not rewritten.

# Acceptance criteria

- The three skills are invocable as `/rn:on` (start), `/rn:dn` (suspend), `/rn:up` (resume): each
  skill directory is renamed (`rn/skills/on`, `rn/skills/dn`, `rn/skills/up`) and its `name:`
  front-matter equals the directory name.
- No occurrence of the old command tokens `rdy`, `brb`, or `bak` remains anywhere under `rn/`, with
  one exception: the historical `## [0.5.0]` entry in `rn/CHANGELOG.md`, which records the previous
  rename and stays verbatim.
- Cross-references resolve to the new names: `/rn:dn` tells the user to resume with `/rn:up`;
  `/rn:up`'s "no session found" guidance points to `/rn:on`; `rn/references/task-workflow.md` and
  `rn/references/steering-template.md` name `on`/`dn`/`up` (and `/rn:up` / `/rn:dn`) wherever they
  referred to the old commands.
- `rn/README.md` uses the new names throughout and reads coherently — the start / down / up framing
  is internally consistent, with no leftover sentence that assumes an old name.
- `rn/CHANGELOG.md` has a `## [Unreleased]` entry under `Changed` describing the rename in
  user-facing terms; `version` in `rn/.claude-plugin/plugin.json` is unchanged (no release was
  requested).
- `claude plugin validate rn --strict` and `claude plugin validate . --strict` (marketplace root)
  both pass with no error.
- The prior session record under `.rn/rn-rename/` is left unmodified.

# Assumptions

- Skills are discovered by directory under `rn/skills/`; neither `plugin.json` nor `marketplace.json`
  embeds command names, so renaming directories + `name:` fields is sufficient to rename the
  commands. (Verified by inspection: both files describe `rn` only, with no command tokens.)
- This is a command rename — a breaking change — but `rn` is pre-1.0 (`0.x`), so it lands as a future
  **minor** bump. No version bump happens now; the change waits under `## [Unreleased]` until a
  release is explicitly requested.
- The `.rn/rn-rename2/` slug aligns with this worktree; the PR is raised from the current
  `worktree-rn-rename2` branch.

# Rules

- commit and push every change; one completion marker per task
- artifacts (skills, references, docs, commit messages, PR) are written in English
- preserve history: do not edit the shipped `## [0.5.0]` CHANGELOG entry or anything under
  `.rn/rn-rename/`
- do not bump `version` in `plugin.json`; the rename goes under `## [Unreleased]` only
- in commit bodies, never write the literal phrase that the resume command matches in `git log` (the
  task-completion marker) as prose — it would falsely register a task as done

# Tasks

### #1: Rename the three command skills and fix their internal references

**Purpose**: Rename `rn/skills/{rdy,brb,bak}` to `{on,dn,up}` and update each `SKILL.md` so its
`name:`, heading, self-references, and cross-references to the other two skills use the new names.

**Prerequisites**: none

**Steps**:

- [ ] `git mv rn/skills/rdy rn/skills/on`, `rn/skills/brb rn/skills/dn`, `rn/skills/bak rn/skills/up`
- [ ] In each `SKILL.md`, update the `name:` field to match its new directory
- [ ] Replace every `/rn:rdy` → `/rn:on`, `/rn:brb` → `/rn:dn`, `/rn:bak` → `/rn:up` (descriptions,
      headings, body, and cross-references — e.g. `dn` pointing the user to `/rn:up`, `up`'s
      "no steering.md found" message pointing to `/rn:on`)
- [ ] self-check (OK/NG per completion criterion, record in checks/task-1.md)
- [ ] QA expert review (subagent)
- [ ] language expert review (subagent)
- [ ] software-engineering expert review (subagent)
- [ ] user review

**Completion criteria**:

- Directories `rn/skills/on`, `rn/skills/dn`, `rn/skills/up` exist; `rn/skills/rdy`, `/brb`, `/bak`
  do not.
- In each renamed `SKILL.md`, the `name:` field equals the directory name.
- No token `rdy`, `brb`, or `bak` remains under `rn/skills/`; every cross-reference between the three
  skills names the correct new command.

### #2: Update the shared reference files

**Purpose**: Update `rn/references/steering-template.md` and `rn/references/task-workflow.md` so every
mention of the old commands uses `on` / `dn` / `up`.

**Prerequisites**: none

**Steps**:

- [ ] In `steering-template.md`, update the `State`-section note (`written by /rn:brb`, `read … by
      /rn:bak`, "the signal /rn:bak and /rn:brb search for") to `/rn:dn` / `/rn:up`
- [ ] In `task-workflow.md`, update line ~4 (`rdy` and `bak` read this file) to `on` and `up`, and
      the `/rn:bak` mention (~line 214) to `/rn:up`
- [ ] self-check (OK/NG per completion criterion, record in checks/task-2.md)
- [ ] QA expert review (subagent)
- [ ] language expert review (subagent)
- [ ] software-engineering expert review (subagent)
- [ ] user review

**Completion criteria**:

- No token `rdy`, `brb`, or `bak` remains under `rn/references/`.
- Each updated sentence reads correctly with the new command name in place (no dangling reference to
  a now-nonexistent command).

### #3: Update README and CHANGELOG

**Purpose**: Rename every command mention in `rn/README.md` to the new names and add a `Changed`
entry under `## [Unreleased]` in `rn/CHANGELOG.md` describing the rename in user terms.

**Prerequisites**: none

**Steps**:

- [ ] Replace all `rdy`/`brb`/`bak` (and `/rn:…`) mentions in `rn/README.md` with `on`/`dn`/`up`,
      keeping the surrounding prose coherent with the start / down / up framing
- [ ] Add a `## [Unreleased]` → `Changed` line in `rn/CHANGELOG.md`: commands renamed
      `rdy`→`on`, `brb`→`dn`, `bak`→`up`, in user-facing terms; leave the `## [0.5.0]` entry untouched
- [ ] Confirm `version` in `rn/.claude-plugin/plugin.json` is unchanged
- [ ] self-check (OK/NG per completion criterion, record in checks/task-3.md)
- [ ] QA expert review (subagent)
- [ ] language expert review (subagent)
- [ ] software-engineering expert review (subagent)
- [ ] user review

**Completion criteria**:

- No token `rdy`, `brb`, or `bak` remains in `rn/README.md`.
- `rn/CHANGELOG.md` has a new `## [Unreleased]` `Changed` line naming the three renames in user
  terms; the `## [0.5.0]` entry is byte-for-byte unchanged.
- `version` in `plugin.json` is the same value as before this task.

### #4: Verify the rename end-to-end

**Purpose**: Confirm the whole rename is complete and structurally valid across the entire plugin.

**Prerequisites**: #1, #2, #3

**Steps**:

- [ ] Grep `rn/` for `\b(rdy|brb|bak)\b`; confirm the only hit is the historical `## [0.5.0]`
      CHANGELOG entry
- [ ] Run `claude plugin validate rn --strict` and `claude plugin validate . --strict`
- [ ] self-check (OK/NG per completion criterion, record in checks/task-4.md)
- [ ] QA expert review (subagent)
- [ ] user review

**Completion criteria**:

- A repository-wide search under `rn/` finds no `rdy`/`brb`/`bak` token except the historical
  `## [0.5.0]` CHANGELOG entry.
- Both `claude plugin validate rn --strict` and `claude plugin validate . --strict` exit with no
  error.
- The three skill directories `on`, `dn`, `up` exist and each `name:` matches its directory.

# Decisions

## D-1: rdy → on (over `go` / `new`)
- **Issue**: `rdy` (start a session) needed a new name alongside `dn` (suspend) and `up` (resume);
  candidates were `on`, `go`, and `new`.
- **Conclusion**: `on`.
- **Rationale**: the user chose `on` — a two-character token matching `dn`/`up`, reading as "power on
  / start up" which fits the start ↔ down ↔ up lifecycle.
- **Evidence**: user selection in the start-session dialog on 2026-06-24.
- **Sources**: this session's opening exchange.

## D-2: dn = suspend, up = resume (initial up/dn assignment corrected)
- **Issue**: which of suspend/resume maps to `up` vs `dn`.
- **Conclusion**: suspend = `dn`, resume = `up`.
- **Rationale**: the user corrected the initial `brb→up` / `bak→dn` to `brb→dn` / `bak→up`, reading it
  as "bring the session down" to suspend and "bring it back up" to resume — the standard
  bring-down / bring-up framing for a service.
- **Evidence**: user correction in this session.
- **Sources**: this session's opening exchange.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
