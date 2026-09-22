# steering.md

The one file a session keeps: its plan and its running record. Every `/rn:*` command reads it;
`/rn:on` writes it, the task loop checks it off and keeps it true, `/rn:dn` and `/rn:up` set and
clear the suspend fields. The operations every command shares — entering a session, judging the
plan, checking a task off, the session-status block, migration — are defined here once.

## Template

Copy verbatim when starting a session. Keep every field name and heading exactly — every command
finds its way by them.

```markdown
---
rn: <installed rn version>
issue: <the issue this session serves — omit the line when there is none>
pr: <the session PR's URL — added when the PR opens>
design: <path to the session's design — omit the line when there is none>
status: running
---

# Goal

<one sentence saying what the user wants, then why, in full>

# Success criteria

- <a state of the world; the Goal is achieved when every line holds>

# Assumptions

- <what the plan rests on, each marked fact (with how it was checked) or assumption>

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

- <a state; the Objective is achieved when every line holds>

# State

- **Last completed**: #N description
- **Next**: #N description
- **Pending**: <the gate awaiting a verdict, with the commit judged and the evaluation file it
  stands on; open questions; items the user deferred; blockers — or "none">
- **Notes**: <whatever else the next conversation needs>
```

## Why each part exists

- **Frontmatter** — the session's fixed facts, kept as YAML so GitHub renders them as a table
  above the plan and every command reads them without parsing prose. `rn` is the version the
  session is written for; `issue` and `pr` are where the work came from and where it is reviewed;
  `design` points at the approach once one is settled. `status` is `running` while the session is
  live and `paused` from `/rn:dn` to `/rn:up` — the suspend signal, and the only state that is a
  field. `/rn:dn` adds `paused_at: <YYYY-MM-DD>` beside it and `/rn:up` removes it. That a session
  is finished is not a field either: its last task, "Evaluation sign-off", carries ` ✅`.
- **Goal** — what the user wants; everything below traces back to it. Its first sentence is the
  session's name: the status block and every report quote it as written, so the user meets the
  same words in every conversation.
- **Success criteria** — how the Goal is judged at the end. States, never artifacts or steps, so
  they survive a change of means. The same name at task level, judged against the task's
  Objective.
- **Assumptions** — what the plan rests on: checked facts and named assumptions, never work still
  to do. A decision about scope lives here or in a criterion, nowhere else, so the evaluator and
  the user judge against the same record.
- **Rules** — conventions that bind every task and everyone who commits. The first line is always
  the commit convention.
- **Tasks** — the work, worked back from the Success criteria; each Objective serves one, fits one
  sentence, and is reached by concrete steps. Flat and numbered, no phases. A "Design sign-off"
  task goes where the approach must be decided before build; its deliverable is the approach,
  written where it belongs in the project and named in the `design` field. "Evaluation sign-off"
  is always the last task.
- **State** — where the session stands between conversations, in prose: what was last completed,
  what is next, what is pending, and what else a cold reader needs. `Pending` is carried until each
  item it names is closed; history lives in git and on the PR.

## Checking a task off

A task is complete when its heading ends in ` ✅` — `### #1: <task name> ✅` — and every step under
it is `[x]`. The check-off is one commit, `<type>: complete task #N — <name>`, the only commit whose
message carries `complete task #`; `/rn:up` reconciles from it. A task found incomplete later gets
a new task.

## Entering a session

Every command but `/rn:on` starts here, so it acts on the right session in its current shape.

1. **Find `steering.md`.** The path known in this conversation; otherwise run
   `git log --format= --name-only --diff-filter=AM -- '*/steering.md' | awk 'NF && !seen[$0]++'`
   (each session once, most recently touched first) and keep the paths that exist on disk and
   whose last task, "Evaluation sign-off", is not yet ` ✅` — a finished session is never resumed.
   One → use it. Several → prefer `status: paused`, then the most recent; `/rn:up` proposes it and
   waits, the other commands say which one they took. None → say "No open session. Run /rn:on to
   start." and stop.

2. **Bring an older session current.** Compare the `rn` field with `version` in
   `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`; on a mismatch run Migration below before the
   command goes on.

## Judging the plan

Run wherever `steering.md`'s Goal, Success criteria, Assumptions or tasks have just been written
or changed — by `/rn:on`, by Migration, by `/rn:gm` — so no plan reaches the user or the task
loop unjudged. First read it yourself against the Plan questions; a defect you can see does not go
to the evaluator. Then run `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md` with kind Plan. NG →
fix, commit, push, judge again; after three NG rounds stop and ask the user, showing the last
verdict; the count starts again from the answer.

## Session-status block

Opens every message that stops for the user while a session is active, so they can answer without
opening `steering.md`. A stop asks one thing, with the conductor's recommendation, and never what
the record already answers.

```
── {slug}: {Goal's first sentence} ──
✅ {ids}   {task names}
👉 #{id}   {task name} ── {the one thing this stop needs from the user}
⬜ {ids}   {task names}
({outlook — what follows this stop})
```

The slug is the session directory's name without its date prefix (`.rn/20260921-wc-tool/` →
`wc-tool`). The Goal's first sentence and the task names are quoted as `steering.md` writes them,
`/`-separated, ids grouped into ranges (`#1–#3`); the rest of the block is in the user's
conversation language. On a report that asks nothing (a suspend, a close) the 👉 line carries where
the session stands and the user's next move. A stop not tied to a task (the plan gate) names the
gate instead of an id. Omit the ⬜ line when nothing remains.

## Migration — a session written under an older rn

Run when a command finds the `rn` field different from the installed version, or finds the version
recorded some other way than in frontmatter. The point is that the session goes on under the
current `rn`, at the current bar, with nothing done by hand and nothing it recorded lost.

1. **Take the old session as input, so nothing it holds is lost.** Read its `steering.md` and
   everything else in its directory. The old text stays in git history; nothing here edits it in
   place.

2. **Write `steering.md` fresh from the template above, so the session is in the shape `/rn:on`
   would give it today.** Carry the Goal as recorded, opening it with one sentence if it has none.
   Lift the old header's facts into the frontmatter fields, and the issue and PR the old `State`
   carried in prose along with them. Rewrite each criterion that names an artifact or a step as the
   state it stands for. Carry every task with its id, name and check-offs into the template's
   fields; a task the old file records complete gets the ` ✅` mark. A checked step is carried
   verbatim, whatever it ran; its wording changes only where the record shows it false. Drop an
   unchecked step that existed only to run the old `rn`'s own review — a self-check, an expert
   review, a record into a process file such as `checks/`; an unchecked step that records substance
   stays and points where this `rn` puts it. The new file holds current intent only — no history of
   the old `rn` or of the migration.

3. **Sync `State` to where the session actually stands, so the next command continues rather than
   restarts.** Carry every fact from the old `State`, including anything pending or deferred, map
   an older status value onto `running` / `paused`, and reconcile check-offs with the commit log
   (`complete task #N`).

4. **Rename the session's directory when its slug names a ticket rather than the work, so the
   session reads as what it produces.** `git mv` the directory to `.rn/{yyyymmdd}-{slug}` with a
   slug taken from the Goal; the issue number lives in the `issue` field.

5. **Remove what the old `rn` wrote for its own process, so the session leaves what this `rn`
   leaves.** Its process files — under 0.8.0, the `checks/` directory — and nothing else; evidence
   and deliverables stay.

6. **Stamp the `rn` field with the installed version, commit `chore: migrate session to rn
   <version>`, and push, so the migration is on record before it is judged.**

7. **Have the migrated plan judged, so the session continues at the current bar.** Run Judging
   the plan above, with the Migration question added to the Plan kind. Then continue the command
   that triggered it.
