# steering.md

The plan and running record for one session — read and written by every `/rn:*` command.

## Template

Copy verbatim when starting a session (`/rn:on`). Keep every heading and field name exactly, so a
session written under an older `rn` stays readable without conversion.

```markdown
Rn version: <installed rn version — stamped once at creation, never user-edited>
Design: <path to where the session's design lives — omit this line entirely when there is none>

# Goal

<why this is being done, in full — no added scope>

# Acceptance criteria

- <states the goal is judged by, not artifacts or steps — write exhaustively>

# Assumptions

- <facts and assumptions taken as true, marked as which>

# Rules

- commit and push every change; one completion marker per task
- <session-specific conventions>

# Tasks

### #1: <task name>

**Purpose**: what this task achieves, 1-2 sentences

**Prerequisites**: tasks that must complete first, or "none"

**Steps**:

- [ ] <specific step>

**Completion criteria**:

- <a state a third party can check with evidence, not "the file exists">

# State

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: forward pointer only — branch/PR, pending gate, blockers; not a re-narration (that
  lives in git log)
```

## Why each section exists

- **Goal** — what the user actually wants; every task and criterion traces back to it.
- **Acceptance criteria** — the bar the whole session is judged against at the evaluation gate;
  states, not deliverables.
- **Assumptions** — what the plan takes as true; if one turns out false, the plan changes.
- **Rules** — conventions that bind every task; the first line is always the commit convention.
- **Tasks** — the work, worked back from Acceptance criteria. A "Design sign-off" task where the
  approach must be decided before build — its deliverable is the approach written where it belongs
  in the project and put on the PR, never an rn template. "Evaluation sign-off" is always last.
- **State** — the only section `/rn:dn` and `/rn:up` write; everything else the session needs is
  history that lives in git and the PR.

## Task requirements

- Purpose fits one sentence; split the task if it doesn't.
- Steps are specific actions, not "implement the feature".
- Completion criteria are checkable by someone other than the author, with evidence — a state,
  never "the file exists" or "review passed".
- Prerequisites are named explicitly.
- Tasks are flat and numbered `#1`, `#2`, … — no phases, no per-task user gate.

## Session-status block

Opens every message that stops for user input while a session is active.

```
── {slug}: {goal one-liner} ──
✅ {ids}   {short labels}
👉 #{id}   {task name} ── asking now: {what this stop needs}
⬜ {ids}   {short labels}
({outlook — what follows this stop})
```

Derive it fresh from `steering.md` at emit time — never reuse an earlier block. Omit the ⬜ line
when nothing remains. Write it in the user's conversation language.

## Migration — a session written under an older rn

Purpose: an older session resumes with nothing done by hand.

1. **Keep every task, check-off, and `State` fact exactly, so no recorded progress is lost in
   reconciliation.** Copy them across unchanged.
2. **Drop unchecked review-machinery steps, since this rn evaluates on the PR instead.** Remove an
   unchecked step naming `self-check`, `checks/`, `QA expert review`, `Craft expert review`,
   `Verification expert review`, or `Design expert review`. Keep such a step if it's already
   checked — it records what happened. Leave any existing `checks/` files alone.
3. **Stamp `Rn version:` to the installed version, so later commands stop treating this session as
   stale.**
4. **Commit and push, then continue, so the migration is itself on record.** Commit message:
   `chore: migrate session to rn <version>`. Push, then continue the command that triggered this.
