# steering.md

The one file a session keeps: its plan and its running record. Every `/rn:*` command reads it;
`/rn:on` writes it, the task loop checks it off and keeps it true, `/rn:dn` and `/rn:up` write and
reset `State`. The operations every command shares — entering a session, judging the plan,
checking a task off, the session-status block, migration — are defined here once.

## Template

Copy verbatim when starting a session. Keep every heading and field name exactly — every command
finds its way by them.

```markdown
Rn version: <installed rn version — stamped at creation and by migration, never user-edited>
Design: <path to where the session's design lives — omit this line entirely when there is none>

# Goal

<one sentence saying what the user wants — it is quoted as the session's name wherever the session
is shown. Then why, in full — no added scope>

# Success criteria

- <a state of the world; the Goal is achieved when every line holds — never an artifact or a step>

# Assumptions

- <what the plan rests on, each marked fact (with how it was checked) or assumption — never work
  still to do or a decision not yet made>

# Rules

- commit and push every change, staging paths by name; one completion marker per task; never
  rewrite pushed history
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

- **Status**: active
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Pending**: the gate awaiting a verdict, open questions, items the user deferred, blockers — or
  "none"
- **Notes**: branch, PR, and whatever else the next conversation needs; history lives in git and
  on the PR
```

## Why each section exists

- **Goal** — what the user wants; everything below traces back to it. Its first sentence is the
  session's name: the status block and every report quote it as written, so the user meets the
  same words in every conversation.
- **Success criteria** — how the Goal is judged at the end. States, so they survive a change of
  means. The same name at task level, judged the same way against the task's Objective.
- **Assumptions** — what the plan rests on; when one turns out false, the plan changes, not the
  Goal. A decision about scope lives here or in a criterion — nowhere else, so the evaluator and
  the user judge against the same record.
- **Rules** — conventions that bind every task and everyone who commits. The first line is always
  the commit convention.
- **Tasks** — the work, worked back from the Success criteria; each Objective serves one. A
  "Design sign-off" task goes where the approach must be decided before build; its deliverable is
  the approach, written where it belongs in the project and named on the `Design:` line.
  "Evaluation sign-off" is always the last task.
- **State** — where the session stands between conversations. `Status` is `active` while a
  conversation holds the session, `paused` from `/rn:dn` to `/rn:up`, and `closed` once
  "Evaluation sign-off" is approved — a closed session is never resumed. `Pending` is carried until
  each item it names is closed, never wiped.

## What makes a task

- Its Objective fits one sentence; split it otherwise.
- Its Steps name concrete actions, not "implement the feature".
- Its Success criteria are states a third party can check with evidence.
- Its Prerequisites are named.
- Tasks are flat and numbered `#1`, `#2`, … — no phases, no per-task user gate.

## Checking a task off

A task is complete when its heading ends in ` ✅` — `### #1: <task name> ✅` — and every step under
it is `[x]`. The check-off is one commit, `<type>: complete task #N — <name>`, the only commit whose
message carries `complete task #`; `/rn:up` reconciles from it. Nothing else marks a task done, and
a check-off is never undone by rewriting history — a task found incomplete gets a new task.

## Entering a session

Every command but `/rn:on` starts here, so it acts on the right session in its current shape.

1. **Find `steering.md`.** The path known in this conversation; otherwise run
   `git log --format= --name-only --diff-filter=AM -- '*/steering.md' | awk 'NF && !seen[$0]++'`
   (each session once, most recently touched first) and keep the paths that exist on disk and
   whose `Status` is not `closed`. One → use it. Several → prefer `Status: paused`, then the most
   recent; `/rn:up` proposes it with a recommendation and waits, the other commands say which one
   they took. None → say "No open session. Run /rn:on to start." and stop.

2. **Bring an older session current.** Compare `Rn version:` with `version` in
   `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; on a mismatch run Migration below before the
   command goes on, so the rest of it reads one shape.

## Judging the plan

Run wherever `steering.md`'s Goal, Success criteria, Assumptions or tasks have just been written
or changed — by `/rn:on`, by Migration, by `/rn:gm` — so no plan reaches the user or the task
loop unjudged. First read it as the conductor: every criterion a state, every Assumption a checked
fact or a named assumption and never work to do, every term one the user can take, no history — a
plan with a defect you can see does not go to the evaluator. Then run
`${CLAUDE_PLUGIN_ROOT}/references/evaluate.md` with kind Plan. NG → fix, commit
`docs: revise plan — {what changed}`, push, judge again; after three NG rounds stop and ask the
user one thing, with a recommendation, opening with the session-status block. The plan the user
sees is the plan that was judged: a change after the verdict is judged again.

## Session-status block

Opens every message that stops for the user while a session is active, so they can answer without
opening `steering.md`.

```
── {slug}: {Goal's first sentence} ──
✅ {ids}   {task names}
👉 #{id}   {task name} ── {the one thing this stop needs from the user}
⬜ {ids}   {task names}
({outlook — what follows this stop})
```

The slug is the session directory's name without its date prefix (`.rn/20260921-wc-tool/` →
`wc-tool`). Names are quoted as `steering.md` writes them — the Goal's first sentence and the task names,
verbatim, `/`-separated, ids grouped into ranges (`#1–#3`) — so the user meets the same words in
every conversation; everything else in the block is in the user's conversation language. The 👉 line
carries the ask; on a report that asks nothing (a suspend, a close) it carries where the session
stands and the user's next move. A stop not tied to a task (the plan gate) names the gate instead
of an id. Omit the ⬜ line when nothing remains. Derive it from `steering.md` at the moment of
writing. A stop asks one thing, never what the record already answers, and carries the conductor's
recommendation.

## Migration — a session written under an older rn

Run when a command finds `Rn version:` different from the installed version. The point is that the
session goes on under the current `rn`, at the current bar, with nothing done by hand and nothing
it recorded lost.

1. **Take the old session as input, so nothing it holds is lost.** Read its `steering.md` and
   everything else in its directory. The old text stays in git history; nothing here edits it in
   place.

2. **Write `steering.md` fresh from the template above, so the session is in the shape `/rn:on`
   would give it today.** Carry the Goal as recorded, opening it with one sentence if it has none.
   Rewrite each criterion that names an artifact or a step as the state it stands for. Carry every
   task with its id, name, check-offs and every step that records substance, moved into the
   template's fields; a task the old file records complete gets the ` ✅` mark. Drop an unchecked
   step that existed only to run the old `rn`'s own review — a self-check, an expert review, a
   record into a process file such as `checks/`; a step that records substance stays and points
   where this `rn` puts it, the PR. A checked step keeps its check and its substance; its wording
   changes only where the record shows it false. The new file holds current intent only — no
   history of the old `rn` or of the migration; git keeps that.

3. **Sync `State` to where the session actually stands, so the next command continues rather than
   restarts.** Carry every fact from the old `State`, including anything pending or deferred, map
   an older `Status` value onto `active` / `paused` / `closed`, and reconcile check-offs with the
   commit log (`complete task #N`).

4. **Remove what the old `rn` wrote for its own process, so the session leaves what this `rn`
   leaves.** That is the `checks/` directory and nothing else — evidence and deliverables stay. Git
   history keeps what is removed.

5. **Stamp `Rn version:` with the installed version, commit `chore: migrate session to rn
   <version>`, and push, so the migration is on record before it is judged.**

6. **Have the migrated plan judged, so the session continues at the current bar.** Read it as the
   conductor against the old file first: every task, check-off and pending item present. Then run
   Judging the plan above, with the Migration question added to the Plan kind. Then continue the
   command that triggered it.
