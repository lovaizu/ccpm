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
  one exception: `rn/CHANGELOG.md`, which records release history — the `## [0.5.0]` entry stays
  verbatim, and the new release entry legitimately names the old commands as the source of the rename
  (the same convention as `0.5.0` naming the prior `gm`/`bb`/`hi`).
- Cross-references resolve to the new names: `/rn:dn` tells the user to resume with `/rn:up`;
  `/rn:up`'s "no session found" guidance points to `/rn:on`; `rn/references/task-workflow.md` and
  `rn/references/steering-template.md` name `on`/`dn`/`up` (and `/rn:up` / `/rn:dn`) wherever they
  referred to the old commands.
- `rn/README.md` uses the new names throughout and reads coherently — the start / down / up framing
  is internally consistent, with no leftover sentence that assumes an old name.
- `rn/CHANGELOG.md` records the rename under a `## [0.6.0] - 2026-06-24` section (the former
  `## [Unreleased]`, renamed and dated), with a fresh empty `## [Unreleased]` above it; the
  `## [0.5.0]` entry is unchanged.
- `version` in `rn/.claude-plugin/plugin.json` is `0.6.0`.
- `claude plugin validate rn --strict` and `claude plugin validate . --strict` (marketplace root)
  both pass with no error.
- The prior session record under `.rn/rn-rename/` is left unmodified.
- After the PR merges to `main`, `main` carries an annotated tag `rn-v0.6.0` and a GitHub Release is
  published from the `## [0.6.0]` notes. (Gated on the user's merge — the merge itself is the user's.)

# Assumptions

- Skills are discovered by directory under `rn/skills/`; neither `plugin.json` nor `marketplace.json`
  embeds command names, so renaming directories + `name:` fields is sufficient to rename the
  commands. (Verified by inspection: both files describe `rn` only, with no command tokens.)
- This is a command rename — a breaking change — but `rn` is pre-1.0 (`0.x`), so per the plugin rules
  it lands as a **minor** bump: `0.5.0` → `0.6.0`. The user has requested the release, so this session
  bumps the version and finalizes the changelog after the rename is verified.
- `main` is protected: the assistant does every release step except the merge. The assistant pushes
  the bump + finalized changelog and asks the user to merge; the user merges; then the assistant tags
  `main` (`rn-v0.6.0`) and publishes the GitHub Release.
- The `.rn/rn-rename2/` slug aligns with this worktree; the PR is raised from the current
  `worktree-rn-rename2` branch.

# Rules

- commit and push every change; one completion marker per task
- artifacts (skills, references, docs, commit messages, PR) are written in English
- preserve history: do not edit the shipped `## [0.5.0]` CHANGELOG entry or anything under
  `.rn/rn-rename/`
- the version bump (`0.6.0`) and changelog finalization happen only in the release task (#5), after
  the rename is verified — not before
- the assistant never merges to `main` and never uses `--admin`; it requests the user's merge, and
  tags + publishes the Release only after the user confirms the merge
- in commit bodies, never write the literal phrase that the resume command matches in `git log` (the
  task-completion marker) as prose — it would falsely register a task as done

# Tasks

### #1: Rename the three command skills and fix their internal references

**Purpose**: Rename `rn/skills/{rdy,brb,bak}` to `{on,dn,up}` and update each `SKILL.md` so its
`name:`, heading, self-references, and cross-references to the other two skills use the new names.

**Prerequisites**: none

**Steps**:

- [x] `git mv rn/skills/rdy rn/skills/on`, `rn/skills/brb rn/skills/dn`, `rn/skills/bak rn/skills/up`
- [x] In each `SKILL.md`, update the `name:` field to match its new directory
- [x] Replace every `/rn:rdy` → `/rn:on`, `/rn:brb` → `/rn:dn`, `/rn:bak` → `/rn:up` (descriptions,
      headings, body, and cross-references — e.g. `dn` pointing the user to `/rn:up`, `up`'s
      "no steering.md found" message pointing to `/rn:on`)
- [x] self-check (OK/NG per completion criterion, record in checks/task-1.md)
- [x] QA expert review (subagent)
- [x] language expert review (subagent)
- [x] software-engineering expert review (subagent)
- [x] user review

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

- [x] In `steering-template.md`, update the `State`-section note (`written by /rn:brb`, `read … by
      /rn:bak`, "the signal /rn:bak and /rn:brb search for") to `/rn:dn` / `/rn:up`
- [x] In `task-workflow.md`, update line ~4 (`rdy` and `bak` read this file) to `on` and `up`, and
      the `/rn:bak` mention (~line 214) to `/rn:up`
- [x] self-check (OK/NG per completion criterion, record in checks/task-2.md)
- [x] QA expert review (subagent)
- [x] language expert review (subagent)
- [x] software-engineering expert review (subagent)
- [x] user review

**Completion criteria**:

- No token `rdy`, `brb`, or `bak` remains under `rn/references/`.
- Each updated sentence reads correctly with the new command name in place (no dangling reference to
  a now-nonexistent command).

### #3: Update README and CHANGELOG

**Purpose**: Rename every command mention in `rn/README.md` to the new names and add a `Changed`
entry under `## [Unreleased]` in `rn/CHANGELOG.md` describing the rename in user terms.

**Prerequisites**: none

**Steps**:

- [x] Replace all `rdy`/`brb`/`bak` (and `/rn:…`) mentions in `rn/README.md` with `on`/`dn`/`up`,
      keeping the surrounding prose coherent with the start / down / up framing
- [x] Add a `## [Unreleased]` → `Changed` line in `rn/CHANGELOG.md`: commands renamed
      `rdy`→`on`, `brb`→`dn`, `bak`→`up`, in user-facing terms; leave the `## [0.5.0]` entry untouched
- [x] Confirm `version` in `rn/.claude-plugin/plugin.json` is unchanged
- [x] self-check (OK/NG per completion criterion, record in checks/task-3.md)
- [x] QA expert review (subagent)
- [x] language expert review (subagent)
- [x] software-engineering expert review (subagent)
- [x] user review

**Completion criteria**:

- No token `rdy`, `brb`, or `bak` remains in `rn/README.md`.
- `rn/CHANGELOG.md` has a new `## [Unreleased]` `Changed` line naming the three renames in user
  terms; the `## [0.5.0]` entry is byte-for-byte unchanged.
- `version` in `plugin.json` is the same value as before this task.

### #4: Verify the rename end-to-end

**Purpose**: Confirm the whole rename is complete and structurally valid across the entire plugin.

**Prerequisites**: #1, #2, #3

**Steps**:

- [ ] Grep `rn/` for `\b(rdy|brb|bak)\b`; confirm every remaining hit is in `rn/CHANGELOG.md`
      (release history) and none is in `rn/skills/`, `rn/references/`, or `rn/README.md`
- [ ] Run `claude plugin validate rn --strict` and `claude plugin validate . --strict`
- [ ] self-check (OK/NG per completion criterion, record in checks/task-4.md)
- [ ] QA expert review (subagent)
- [ ] user review

**Completion criteria**:

- A repository-wide search under `rn/` finds no `rdy`/`brb`/`bak` token outside `rn/CHANGELOG.md`
  (where release history — the `0.5.0` entry and the new rename entry — legitimately names them).
- Both `claude plugin validate rn --strict` and `claude plugin validate . --strict` exit with no
  error.
- The three skill directories `on`, `dn`, `up` exist and each `name:` matches its directory.

### #5: Release 0.6.0

**Purpose**: Cut the `0.6.0` release for the rename: bump the version, finalize the changelog, push,
and (after the user merges) tag `main` and publish the GitHub Release.

**Prerequisites**: #4

**Steps**:

- [ ] Bump `version` in `rn/.claude-plugin/plugin.json` to `0.6.0`
- [ ] In `rn/CHANGELOG.md`, rename `## [Unreleased]` to `## [0.6.0] - 2026-06-24` and add a fresh
      empty `## [Unreleased]` above it; leave `## [0.5.0]` unchanged
- [ ] Re-run `claude plugin validate rn --strict` and `claude plugin validate . --strict`
- [ ] self-check (OK/NG per completion criterion, record in checks/task-5.md)
- [ ] QA expert review (subagent)
- [ ] user review
- [ ] Commit and push; ask the user to merge the PR to `main` (assistant does not merge)
- [ ] After the user confirms the merge: tag `main` with annotated `rn-v0.6.0` and publish a GitHub
      Release using the `## [0.6.0]` notes

**Completion criteria**:

- `version` in `rn/.claude-plugin/plugin.json` is `0.6.0`.
- `rn/CHANGELOG.md` has `## [0.6.0] - 2026-06-24` containing the rename entry, a fresh empty
  `## [Unreleased]` above it, and an unchanged `## [0.5.0]`.
- Both `claude plugin validate rn --strict` and `claude plugin validate . --strict` exit with no
  error.
- After the user's merge, `main` carries the annotated tag `rn-v0.6.0` and a published GitHub Release
  named for it. (This step is gated on the user's merge.)

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

## D-3: release as 0.6.0 (minor) this session
- **Issue**: whether to bump the version, and by how much.
- **Conclusion**: bump `0.5.0` → `0.6.0` (minor) and release in this session.
- **Rationale**: a command rename is a breaking change, but `rn` is pre-1.0, where the plugin rules
  route breaking changes to a minor bump; the user explicitly asked to include the version update, so
  the release happens now rather than waiting under `## [Unreleased]`.
- **Evidence**: current `version` is `0.5.0`; user instruction "バージョン更新も入れて" (include the
  version update) on 2026-06-24.
- **Sources**: `rn/.claude-plugin/plugin.json`; this session.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
