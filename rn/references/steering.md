# steering.md

The one file a session keeps: its plan and its running record. Every `/rn:*` command reads it;
`/rn:on` writes it, the task loop checks it off, `/rn:dn` and `/rn:up` write and reset `State`.

## Template

Copy verbatim when starting a session. Keep every heading and field name exactly — a session
written under an older `rn` must stay readable without conversion.

```markdown
Rn version: <installed rn version — stamped once at creation, never user-edited>
Design: <path to where the session's design lives — omit this line entirely when there is none>

# Goal

<what the user wants and why, in full — no added scope>

# Acceptance criteria

- <a state of the world the goal is judged by — never an artifact or a step; write the whole set>

# Assumptions

- <what is taken as true; mark each as a fact (how it was checked) or an assumption>

# Rules

- commit and push every change; one completion marker per task
- <session-specific conventions>

# Tasks

### #1: <task name>

**Purpose**: what this task achieves, one or two sentences

**Prerequisites**: tasks that must complete first, or "none"

**Steps**:

- [ ] <specific step>

**Completion criteria**:

- <a state a third party can check with evidence — never "the file exists" or "review passed">

# State

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: forward pointer only — branch/PR, the gate awaiting a verdict, blockers; history lives
  in git and the PR
```

## Why each section exists

- **Goal** — what the user wants; every criterion and task must trace back to it.
- **Acceptance criteria** — the bar the session is judged by at the evaluation gate. States, so
  they survive a change of means.
- **Assumptions** — what the plan rests on; when one turns out false, the plan changes, not the
  goal.
- **Rules** — conventions that bind every task. The first line is always the commit convention.
- **Tasks** — the work, worked back from the Acceptance criteria. A "Design sign-off" task goes
  where the approach must be decided before build; its deliverable is the approach, written where
  it belongs in the project and put on the PR — `rn` gives it no template. "Evaluation sign-off"
  is always the last task.
- **State** — where the session stands between conversations. The only section `/rn:dn` and
  `/rn:up` write.

## What makes a task

- Its Purpose fits one sentence; split it otherwise.
- Its Steps name concrete actions, not "implement the feature".
- Its Completion criteria are states a third party can check with evidence.
- Its Prerequisites are named.
- Tasks are flat and numbered `#1`, `#2`, … — no phases, no per-task user gate.

## Session-status block

Opens every message that stops for the user while a session is active, so they can answer without
opening `steering.md`.

```
── {slug}: {goal one-liner} ──
✅ {ids}   {short labels}
👉 #{id}   {task name} ── asking now: {what this stop needs from the user}
⬜ {ids}   {short labels}
({outlook — what follows this stop})
```

Derive it from `steering.md` at the moment of writing — never reuse an earlier block. A stop not
tied to a task (the plan gate) names the gate instead of an id. Omit the ⬜ line when nothing
remains. Write it in the user's conversation language.

## Migration — a session written under an older rn

Run when a command finds `Rn version:` different from the installed version. The point is that an
older session resumes with nothing done by hand.

1. **Keep every task, every check-off, and every `State` fact, so no recorded progress is lost.**
   Change none of them.
2. **Drop unchecked steps that only served 0.8.0's review machinery, since this `rn` evaluates on
   the PR instead.** Those are unchecked steps naming `self-check`, `checks/`, `QA expert review`,
   `Craft expert review`, `Verification expert review`, or `Design expert review`. A checked one
   stays — it records what happened. Existing `checks/` files are left alone.
3. **Stamp `Rn version:` with the installed version, so later commands see a current session.**
4. **Commit `chore: migrate session to rn <version>` and push, so the migration is on record.**
   Then continue the command that triggered it.
