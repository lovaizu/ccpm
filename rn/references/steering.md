# The session's record

A session is its directory `.rn/{yyyymmdd}-{slug}/`, the README, design document, and verification
document it names, and git. A fresh conversation, and every later version of `rn`, goes on from
these alone, so the layout, field names, headings, and markers stay exactly as written here.

## steering.md

```markdown
---
rn: <installed rn version>
pr: <the session's pull request URL>
status: running
artifact-language: <the language the user chose for everything written to the repository>
conversation-language: <the language the user chose for what is said to them>
readme: <path of the README; README.md unless agreed otherwise>
design: <path of the design document; docs/design.md unless agreed otherwise>
verification: <path of the verification document; docs/verification.md unless agreed otherwise>
---

# Goal

<what the user wants and why, as agreed with them>

# Acceptance criteria

## Attractive quality

- A1: <what would make the user choose the result>

## Must-be quality

- M1: <what the user takes for granted>

# Assumptions

- Fact, <how it was checked, or "decided by the user">: <what the plan rests on>
- Assumption: <what the plan rests on without having checked it>

# Rules

- <what a generator cannot tell from the goal, such as this repository's conventions>

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off
### [ ] #3: <task name>

Purpose: <what this task does for the goal>

Serves: <criterion IDs>

Completion criteria:

- Attractive quality: <a state checked on the real thing>
- Must-be quality: <a state checked on the real thing>

### [ ] #4: Deliverable sign-off

# Not yet specified

- <what cannot yet be stated as a task>
```

- Criterion IDs are `A1`, `A2`… and `M1`, `M2`…, never reused once given.
- Tasks are taken in the order written. A task is marked `[x]` when the conductor decides its purpose
  is fulfilled, a sign-off only when the user approves it with `/rn:ty`. A task added later takes the
  next unused id and goes before the sign-off it leads to.
- Until the Design sign-off is approved, the only tasks are the Plan and Design sign-offs; what the
  deliverable needs is under Not yet specified. The tasks planned then take the next ids, and the
  Deliverable sign-off comes last.
- The pull request body links `steering.md`, with `Closes #N` for each issue the work completes,
  `Refs #N` for each it only serves, and the pull requests it replaces, as agreed in the plan.
- `status` becomes `finished` when the Deliverable sign-off is approved.

## open/

What is not yet settled, one file per item, named `{NN}-{kind}-{about}.md`: `{NN}` is one more than
the highest number in `open/`, or `01` when it is empty; `{kind}` is one of

- `report`: written by a first user, or by `writ` on how the documents read, one file per use the
  conductor asks for, such as `04-report-task-3.md`, and `05-report-task-3-a1.md` for one viewpoint
  after a fix;
- `feedback`: the user's words from `/rn:gm`, whole, in their own language;
- `notes`: design points agreed and waiting for `writ`, or where a task stands when `/rn:dn` pauses.

`{about}` names what it is about, such as `plan`, `design`, `task-3`, or `deliverable`.

The conductor writes its Good and More under a report in the report's file before any fix is made,
so whoever fixes reads the Goods to keep. An item leaves `open/` in the commit that settles it,
copied whole into that commit's message under its file name, with what was decided on each More:

```
04-report-task-3.md:
    <the report, whole, each line indented>

- Good A1: <what the user gains, at path:line>
- More A1: <what the user will struggle with, at path:line>
  → fixed: <how> | → let go: <why fixing it would not bring the work closer> | → to the user: <the question, or back to the plan or the design>
```

Asking for the same use again writes the same file anew; settle the earlier report first, so it
stays in the record and the first user never reads it.

## The decision line

Every commit the conductor makes has a subject line saying what it records, such as
`rn: settle the reports on #3 move src/cart`, and ends with one line saying what was decided and what
comes next; the first, from `/rn:on`, is `● plan ── started → working out the plan`:

```
● {#id task name | plan | design | deliverable} ── {what was decided} → {next move}
```

`●`, `──`, `→`, `waiting for`, and `paused at` stay as written whatever the artifact language, since
the commands find their way by them. The last decision line on the branch is where the session
stands. The commits where `rn` stops for the user end as follows, and leave in `open/` only what is
listed:

| Stop | Ends with | `open/` holds |
|---|---|---|
| At a sign-off, with the proposal as the message body | `→ waiting for #{id} {sign-off name}` | only `notes` of design points waiting for `writ` |
| After `/rn:ty` | `── approved → {the next task, or finished}` | the same |
| After `/rn:gm` | `── feedback in {file} → {working out the plan or the design again, or the tasks for it}` | that, and the `feedback` item |
| A pause, on `/rn:dn` | `→ paused at {#id task name, plan, or design}` | whatever is unsettled, and a `notes` item on where the task stands, its edits committed beside it |

## Finding the session

1. The `steering.md` this conversation has been working on.
2. Otherwise the one the current branch changed whose `status` is not `finished`, a session from an
   older `rn` having none:
   `git diff --name-only $(git merge-base HEAD origin/HEAD) HEAD -- '.rn/*/steering.md'`
   (`git remote set-head origin --auto` first when `origin/HEAD` is not set).

None → say there is no session on this branch: check out the session's branch, or run `/rn:on`.
Only one whose `status` is `finished` → say it is finished. Either way, stop.

A session with no `rn` field, or one whose first two numbers are lower than `version` in
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, was started under an earlier `rn`. `/rn:up`
brings it to the current form; any other command asks the user to run `/rn:up` first, and stops.

## Bringing an older session to the current form

The old record is the user's request and what was done so far. The goal is worked out again from it,
since an older record may not hold why the user wants the goal, and every later decision is judged
by it.

1. Read the old `steering.md` and whatever else the old version left in the session's directory.
2. Work out the plan as `/rn:on` does, with the session's branch, pull request, and directory in
   place of new ones and the old record as the request: ask only what it leaves unclear.
3. The first write of the new `steering.md` replaces the old one. What an old design the user
   approved settled goes to a `notes` item as agreed points of the design; what was done becomes
   Facts in Assumptions, each saying where; the other old files are removed, and stay readable in
   git.
4. Stop at a new Plan sign-off.
