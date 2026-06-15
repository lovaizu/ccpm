# Goal

Keep the Claude Code session on the interactive Max flat-rate path (no `claude -p`, no SDK), and
prove — in the real cmux + Claude Code + rn environment — that an **external watcher** can run the
rn suspend/resume loop unattended. When context crosses a threshold (~70%), the watcher must drive,
with zero human input:

```
ctx-check → ESC → /rn:bb → git gate → /clear → /rn:hi
```

This session's deliverable is a **feasibility verdict backed by a working spike**, not a shipped
product. Packaging (plugin vs plain scripts) and polish are explicitly out of scope and deferred to
a later session — decided only after feasibility is confirmed. **rn itself is not modified.**

# Acceptance criteria

Two axes: does the chain actually work (goal alignment), and does it work safely/repeatably
(quality). All judged by live runs in this environment, never by reasoning alone.

## Goal alignment — the chain works end to end

- **AC1 — Live token source**: the augmented statusline writes a state file containing the current
  context-% that matches the value shown in the status line, refreshed on each render, and readable
  by an external process.
- **AC2 — Threshold detection**: the watcher reads that state file and detects crossing the ~70%
  threshold.
- **AC3 — ESC interrupts**: an ESC sent through cmux to the target surface actually stops an
  in-progress Claude Code response (research task 3 — must be observed live).
- **AC4 — bb fires and completes**: after ESC, `/rn:bb` is sent and runs to completion (commits +
  writes `Status: paused` + pushes).
- **AC5 — git gate holds**: the watcher detects bb completion from git facts only (clean tree **and**
  HEAD `steering.md` State `Status: paused`), and `/clear` is **never** sent before that gate passes.
- **AC6 — clear fires**: `/clear` is sent and the context is cleared (logical session boundary).
- **AC7 — hi resumes**: `/rn:hi` is sent in the fresh conversation, reconstructs state from git, and
  resumes the next task.
- **AC8 — Full unattended run**: a single threshold crossing drives ESC → bb → gate → clear → hi to
  completion with **zero** manual keystrokes, observed at least once.

## Quality — safe and repeatable

- **AC9 — No double-fire**: while one cycle is in flight (threshold still high, bb not yet done), the
  watcher does not re-trigger ESC/bb.
- **AC10 — Re-arm**: after `/rn:hi` resets the State (`Status: not suspended`), the watcher can fire
  again on the next threshold crossing — demonstrated across at least two consecutive cycles.
- **AC11 — Billing path unchanged**: no `claude -p` and no SDK anywhere in the spike; the watcher
  only sends keystrokes to the live interactive pane. Verified by inspecting every script.
- **AC12 — Safe targeting & degradation**: the watcher drives the correct surface and repo (learned
  from the state file), and when the state file is missing or stale it sends nothing (no spurious
  keystrokes).

# Assumptions

Facts (verified this session) and assumptions (to be proven by the tasks).

## Facts — verified

- **F1**: cmux is the terminal (no tmux). It exposes `cmux send --surface <id> <text>`,
  `cmux send-key --surface <id> <key>`, and `cmux read-screen`/`capture-pane --surface <id>`.
  Source: `cmux --help` on this machine.
- **F2**: the current pane's identifiers are in the environment — `CMUX_SURFACE_ID`,
  `CMUX_WORKSPACE_ID`. Source: `env` in this session.
- **F3**: the existing `~/.claude/scripts/statusline.sh` already computes the real context-limit
  percentage (`c_int`) from `.context_window.current_usage` (input + output + cache) ÷
  `context_window_size`. statusLine is the only live token source (hooks do not receive tokens).
  Source: reading the script + the work-instruction research.
- **F4**: `/rn:bb` commits work, writes State `Status: paused`, and pushes; `/rn:hi` reconciles from
  git and resets State to `Status: not suspended`, committing that reset. The `Status` field is a
  committed git fact, not screen prose. Source: rn `bb`/`hi` SKILL.md.
- **F5**: bb has a "clean tree → skip the commit" branch, so HEAD may not advance after ESC when
  there is no diff — therefore "HEAD advanced" must not be a required gate (D-2).

## Assumptions — unverified, proven by tasks

- **A1**: `statusline.sh`, spawned by Claude Code, inherits `CMUX_SURFACE_ID` in its environment, so
  it can stamp the target surface into the state file. → task #1.
- **A2**: `cmux send-key … Escape` (exact key name TBD) interrupts an in-progress CC response. → #2.
- **A3**: `cmux send <text>` types into the prompt; submitting requires a trailing
  `cmux send-key … Enter` (text alone does not auto-submit). → #2.
- **A4**: a slash command delivered via `send` + `Enter` is accepted exactly as if typed by the user
  (`/rn:bb`, `/clear`, `/rn:hi`). → #2, #5.
- **A5**: sending `/rn:hi` in the same pane after `/clear` resumes correctly (a fresh conversation
  shares the same surface). → #5.
- **A6**: for this PoC there is a single active rn session (one `steering.md`) in the target repo.

# Rules

- 1 task = 1 commit.
- Do not modify rn (`rn/**`). The watcher only reads rn's git output and sends keystrokes.
- Interactive billing only — no `claude -p`, no SDK, in any spike artifact.
- Do not clobber the existing `statusline.sh` display output; only append a state-file write.
- Spike artifacts live under `loop/` at the repo root, clearly marked PoC. Packaging is deferred —
  do not adopt a plugin layout this session.
- Verify by running it live in this cmux + CC + rn environment; do not substitute analysis for a run.

# Tasks

### #1: statusline → state-file write

**Purpose**: Make the live context-% (and the target surface/repo) available to an external process
by appending a state-file write to the existing statusline script, without changing its display.

**Prerequisites**: none

**Steps**:

- [ ] Copy the current `~/.claude/scripts/statusline.sh` into `loop/statusline.sh` as the spike copy.
- [ ] Append a block that writes JSON to a per-surface state file (e.g.
      `~/.rn/ctx/${CMUX_SURFACE_ID}.json`) containing at least: context percentage, raw token total,
      `context_window_size`, `CMUX_SURFACE_ID`, `CMUX_WORKSPACE_ID`, repo cwd
      (`.workspace.current_dir`), and an epoch timestamp.
- [ ] Confirm the existing display output (the `printf '%s | %s | %s'` line) is unchanged.
- [ ] Trigger a render (point settings at the spike copy or run it with a captured statusline JSON)
      and confirm the file appears with a percentage matching the displayed `C:xx%` and a populated
      `CMUX_SURFACE_ID` (proves A1).
- [ ] self-check (OK/NG per completion criterion, record in checks/1.md)
- [ ] QA engineer review (subagent)
- [ ] language expert review (subagent)
- [ ] software engineer review (subagent)
- [ ] user review

**Completion criteria**:

- A state file written by the statusline script exists and contains a context percentage equal to
  the value the status line displays for the same input, plus a non-empty surface id and repo cwd.
- The statusline display output is byte-for-byte identical to the original for the same input.

### #2: cmux drive primitives (ESC, type+submit, read)

**Purpose**: Establish the exact cmux incantations to interrupt a response, type-and-submit a slash
command, and read pane output for a chosen surface — the riskiest unknowns, resolved early.

**Prerequisites**: none

**Steps**:

- [ ] Determine the exact ESC key name for `cmux send-key` (e.g. `Escape`) and confirm, live, that
      sending it to a surface running an in-progress CC response stops it (proves A2/AC3). Use a
      second pane or surface to drive a test pane so this session is not the one interrupted.
- [ ] Determine how to type a slash command and submit it: confirm `cmux send <text>` then
      `cmux send-key … Enter` lands and runs the command (proves A3/A4).
- [ ] Confirm `cmux read-screen`/`capture-pane --surface <id>` returns the target pane's text (used
      later for observation/logging, not as the gate).
- [ ] Record the confirmed commands and surface-targeting form in `loop/cmux-notes.md`.
- [ ] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA engineer review (subagent)
- [ ] user review

**Completion criteria**:

- `loop/cmux-notes.md` records, with the observed result, the exact command to: (a) send ESC that
  stops an in-progress CC response, (b) type a slash command and submit it, (c) read a surface's
  screen — each targeting a surface by id.

### #3: git gate predicate

**Purpose**: Implement a function that decides bb-done and re-armable purely from git facts, so the
watcher never sends `/clear` prematurely and can re-fire after `/rn:hi`.

**Prerequisites**: none

**Steps**:

- [ ] In `loop/gate.sh`, implement `bb_done`: true when the repo tree is clean **and** HEAD's
      `steering.md` State shows `Status: paused` (read via `git show HEAD:<path>`), per F4/F5.
- [ ] Implement `rearmed`: true when HEAD's `steering.md` State `Status` is no longer `paused` (reset
      by `/rn:hi`).
- [ ] Implement steering-file resolution for the target repo (single active session, A6): locate
      `.rn/*/steering.md`, preferring the most recent / `Status: paused`.
- [ ] Test the predicates against real commits produced by an actual `/rn:bb` then `/rn:hi` run, and
      record the before/after verdicts.
- [ ] self-check (OK/NG per completion criterion, record in checks/3.md)
- [ ] QA engineer review (subagent)
- [ ] language expert review (subagent)
- [ ] software engineer review (subagent)
- [ ] user review

**Completion criteria**:

- `loop/gate.sh` returns `bb_done` = false before a real bb run and = true after it (clean tree +
  `Status: paused` at HEAD), and `rearmed` = true after a real `/rn:hi` reset — each demonstrated
  against actual commits, with the results recorded.

### #4: watcher loop

**Purpose**: Implement the unattended state machine that ties the pieces together: poll the state
file, and on threshold crossing drive ESC → bb → gate → clear → hi, with an in-flight lock and a
stale-file guard.

**Prerequisites**: #1, #2, #3

**Steps**:

- [ ] In `loop/watch.sh`, poll the per-surface state file from #1; parse percentage, surface id,
      repo cwd, and timestamp.
- [ ] Implement the state machine: `ARMED` → (≥ threshold) send ESC then `/rn:bb`, enter `WAIT_BB`
      → (`gate.sh bb_done`) send `/clear` then `/rn:hi`, enter `WAIT_HI` → (`gate.sh rearmed`) back
      to `ARMED`. Hold phase in-process so a still-high percentage cannot re-fire mid-cycle (AC9).
- [ ] Add a stale/missing-file guard: if the state file is absent or its timestamp is older than a
      bound, send nothing (AC12).
- [ ] Make threshold and poll interval configurable (env or args) so #5 can use a low threshold.
- [ ] Confirm by inspection that the watcher uses only `cmux …` and git — no `claude -p`, no SDK
      (AC11).
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA engineer review (subagent)
- [ ] language expert review (subagent)
- [ ] software engineer review (subagent)
- [ ] user review

**Completion criteria**:

- `loop/watch.sh` run against a state file below threshold sends nothing; raised above threshold it
  sends ESC then `/rn:bb` and then waits — sending `/clear` only after `gate.sh` reports bb_done —
  then sends `/rn:hi`; and a missing or stale state file produces no sends. Each behavior observed
  and recorded. No `claude -p`/SDK reference exists in any `loop/` script.

### #5: end-to-end unattended dry run

**Purpose**: Prove the whole chain runs unattended against a throwaway rn session across two
consecutive cycles — the feasibility moment.

**Prerequisites**: #1, #2, #3, #4

**Steps**:

- [ ] Create a throwaway rn session (a scratch `steering.md` with trivial tasks) in a test repo or
      worktree so a real run can be exercised safely.
- [ ] Start the statusline state-file write and the watcher with a deliberately low threshold; drive
      the test CC session to cross it.
- [ ] Observe one full unattended cycle: ESC → `/rn:bb` → git gate → `/clear` → `/rn:hi`, with no
      manual keystrokes (AC8); confirm `/clear` was not sent before the gate (AC5).
- [ ] Cross the threshold a second time and confirm the watcher re-fires (AC10) and that no
      double-fire occurred during either cycle (AC9).
- [ ] Capture a transcript / log of both cycles into `loop/e2e-run.md`.
- [ ] self-check (OK/NG per completion criterion, record in checks/5.md)
- [ ] QA engineer review (subagent)
- [ ] user review

**Completion criteria**:

- `loop/e2e-run.md` records two consecutive unattended cycles in which, with no manual keystrokes,
  the watcher ran ESC → `/rn:bb` → `/clear` → `/rn:hi` in order, sent `/clear` only after the git
  gate passed, and did not double-fire — each point evidenced by the captured log.

### #6: feasibility verdict

**Purpose**: Record the conclusion the session exists to produce — is this approach feasible, where
is it fragile, and what does that imply for the deferred packaging decision.

**Prerequisites**: #1, #2, #3, #4, #5

**Steps**:

- [ ] In `loop/FEASIBILITY.md`, state the verdict (feasible / not / conditional) against AC1–AC12,
      citing the evidence from #1–#5.
- [ ] List the fragile points and residual risks observed (ESC timing, send/submit races, stale
      state, multi-session, restart resilience).
- [ ] List the implications for packaging (what a plugin vs plain-scripts form would each need),
      as input to the next session's decision — without deciding it here.
- [ ] self-check (OK/NG per completion criterion, record in checks/6.md)
- [ ] QA engineer review (subagent)
- [ ] user review

**Completion criteria**:

- `loop/FEASIBILITY.md` gives an explicit feasible/not/conditional verdict referencing each of
  AC1–AC12 with evidence, plus a list of residual risks and a list of packaging implications left
  open for the next session.

# Decisions

## D-1: Token source is the augmented statusline, not a self-tally
- **Issue**: How does an external watcher learn the current context size, given hooks cannot receive
  token counts?
- **Conclusion**: Append a state-file write to the existing `statusline.sh`; the watcher polls that
  file.
- **Rationale**: statusLine is the only live token source, and the existing script already computes
  the exact real percentage — reusing it avoids a fragile independent transcript tally.
- **Evidence**: F3 — the script's `c_int` computation; the work-instruction research that hooks get
  no tokens.
- **Sources**: `~/.claude/scripts/statusline.sh`; work instruction; `cmux --help`.

## D-2: bb-completion gate is git facts only
- **Issue**: How to know `/rn:bb` finished before sending `/clear`, without scraping the screen?
- **Conclusion**: Gate on a clean tree **and** HEAD `steering.md` State `Status: paused`; do not
  require HEAD to have advanced.
- **Rationale**: `Status: paused` is a committed, structured marker rn itself relies on, so it is a
  git fact rather than prose; and bb may skip the commit on a clean tree, so HEAD advance is unsafe
  as a required condition.
- **Evidence**: F4 (bb writes/ pushes `Status: paused`; hi searches for it), F5 (clean-tree skip).
- **Sources**: rn `bb`/`hi` SKILL.md.

## D-3: Re-fire lock is the State `Status` field plus an in-process phase
- **Issue**: Prevent a still-high context from re-triggering ESC/bb mid-cycle, and allow re-firing
  only after a full cycle.
- **Conclusion**: The watcher holds an in-process phase (ARMED → WAIT_BB → WAIT_HI), and treats
  `Status: not suspended` at HEAD (hi's reset) as the re-arm signal.
- **Rationale**: percentage stays high during bb, so a value-only trigger would double-fire; the
  committed `Status` reset is the unambiguous end-of-cycle marker.
- **Evidence**: F4 (hi resets State and commits it).
- **Sources**: rn `hi` SKILL.md.

# State

(written by /rn:bb, read and reset to this placeholder by /rn:hi)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
