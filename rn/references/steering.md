# steering.md

The one file a session keeps: its plan and its running record. Every `/rn:*` command reads it;
`/rn:on` writes it, the task loop checks it off and keeps it true, `/rn:dn` and `/rn:up` write and
reset `State`.

## Template

Copy verbatim when starting a session. Keep every heading and field name exactly — every command
finds its way by them.

```markdown
Rn version: <installed rn version — stamped at creation and by migration, never user-edited>
Design: <path to where the session's design lives — omit this line entirely when there is none>

# Goal

<what the user wants and why, in full — no added scope>

# Success criteria

- <a state of the world; the Goal is achieved when every line holds — never an artifact or a step>

# Assumptions

- <what the plan rests on, each marked fact (with how it was checked) or assumption — never work
  still to do or a decision not yet made>

# Rules

- commit and push every change; one completion marker per task
- <session-specific conventions>

# Tasks

### #1: <task name>

**Objective**: <the outcome this task achieves, and which Success criterion it serves>

**Prerequisites**: <tasks that must complete first, or "none">

**Steps**:

- [ ] <specific step>

**Success criteria**:

- <a state; the Objective is achieved when every line holds — never "the file exists" or "review
  passed">

# State

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Pending**: the gate awaiting a verdict, open questions, items the user deferred, blockers — or
  "none"
- **Notes**: branch, PR, and whatever else the next conversation needs; history lives in git and
  on the PR
```

## Why each section exists

- **Goal** — what the user wants; everything below traces back to it.
- **Success criteria** — how the Goal is judged at the end. States, so they survive a change of
  means. The same name at task level, judged the same way against the task's Objective.
- **Assumptions** — what the plan rests on; when one turns out false, the plan changes, not the
  Goal.
- **Rules** — conventions that bind every task. The first line is always the commit convention.
- **Tasks** — the work, worked back from the Success criteria; each Objective serves one. A
  "Design sign-off" task goes where the approach must be decided before build; its deliverable is
  the approach, written where it belongs in the project and named on the `Design:` line.
  "Evaluation sign-off" is always the last task.
- **State** — where the session stands between conversations. `/rn:dn` writes it, `/rn:up` reads
  it; `Pending` is carried until each item it names is closed, never wiped.

## What makes a task

- Its Objective fits one sentence; split it otherwise.
- Its Steps name concrete actions, not "implement the feature".
- Its Success criteria are states a third party can check with evidence.
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

Run when a command finds `Rn version:` different from the installed version. The point is that the
session goes on under the current `rn`, at the current bar, with nothing done by hand and nothing
it recorded lost.

1. **Take the old session as input, so nothing it holds is lost.** Read its `steering.md` and
   everything else in its directory. The old text stays in git history; nothing here edits it in
   place.

2. **Write `steering.md` fresh from the template above, so the session is in the shape `/rn:on`
   would give it today.** Carry the Goal as recorded. Rewrite each criterion that names an artifact
   or a step as the state it stands for. Carry every task with its id, name, check-offs and every
   step that records substance, moved into the template's fields. Drop an unchecked step that
   existed only to run the old `rn`'s own review — a self-check, an expert review, a record into a
   process file such as `checks/`; a step that records substance stays and points where this `rn`
   puts it, the PR. A checked step stays as it is: it records what happened.

3. **Sync `State` to where the session actually stands, so the next command continues rather than
   restarts.** Carry every fact from the old `State`, including anything pending or deferred, and
   reconcile check-offs with the commit log (`complete task #N`).

4. **Remove what the old `rn` wrote for its own process, so the session leaves what this `rn`
   leaves.** That is the `checks/` directory and nothing else — evidence and deliverables stay. Git
   history keeps what is removed.

5. **Have the migrated plan judged as a plan, so the session continues at the current bar.** Run
   `evaluate.md` with kind Plan plus its Migration line; fix every NG, three rounds at most, then
   ask the user.

6. **Stamp `Rn version:` with the installed version, commit `chore: migrate session to rn
   <version>`, and push, so later commands see a current session and the migration is on record.**
   Then continue the command that triggered it.
