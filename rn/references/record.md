# The session's record

A session is its directory `.rn/{yyyymmdd}-{slug}/`, the README, design document and verification
document its plan names, and git. A fresh conversation, and every later version of rn, goes on from
these alone, so the layout, names and markers stay exactly as written here; the plan's own form is
`${CLAUDE_PLUGIN_ROOT}/checklists/plan.md`.

## The directory

```
.rn/{yyyymmdd}-{slug}/
├── steering.md       the plan, in the form plan.md gives
├── open/             what is not yet settled, one file per item
├── content/          what each work was asked to say, item by item, one file per work
└── tasks/            each task handed to turn, and the CCS turn wrote back
```

`content/` and `tasks/` are written by `up.py content` and `up.py task`, and committed with the
decision that made them; a later conversation settles points from them as from any file. turn's
evidence under `.turn/` at the top of the repository is left uncommitted.

## open/

One file per item, named `{NN}-{kind}-{about}.md`: `{NN}` is one more than the highest number in
`open/`, or `01` when it is empty; `{kind}` is one of

- `report`: the report `up.py report` printed for one work, such as `04-report-task-3.md`;
- `feedback`: the user's words from `/rn:gm`, whole, in their own language;
- `notes`: a question being put to the user, a proposal being made, or where a task stands when
  `/rn:dn` pauses. A question's first line is `Serves:` with the criterion IDs it rests on, or
  `goal`.

`{about}` names what it is about, such as `plan`, `design`, `task-3` or `deliverable`; a question
being put to the user is `question`, and a proposal at a sign-off `proposal`, since the checks find
them by these names.

An item leaves `open/` in the commit that settles it, copied whole into that commit's message under
its file name, with what was decided on each shortfall:

```
04-report-task-3.md:
    <the report, whole, each line indented>

- Good A1: <what the user gains, at path:line>
- More A1: <what the user will struggle with, at path:line>
  → fixed: <how> | → let go: <why fixing it would not bring the work closer> | → to the user: <the question, or back to the plan or the design>
```

## The decision line

Every commit the conductor makes has a subject line saying what it records, such as
`rn: settle the report on #3 move src/cart`, and ends with one line saying what was decided and
what comes next; the first, from `/rn:up`, is `● plan ── started → working out the plan`:

```
● {#id task name | plan | design | deliverable} ── {what was decided} → {next move}
```

`●`, `──`, `→`, `waiting for`, `paused at`, `approved` and `feedback in`, and `Good` and `More` with
their criterion ID at the start of a line, stay as written whatever the artifact language, since the
commands and checks find their way by them. The last decision line on the branch is where the
session stands. The commits where rn stops for the user end as follows, and leave in `open/` only
what is listed:

| Stop | Ends with | `open/` holds |
|---|---|---|
| At a sign-off, with the proposal as the message body | `→ waiting for #{id} {sign-off name}` | nothing |
| After `/rn:ty` | `── approved → {the next task, or finished}` | nothing |
| After `/rn:gm` | `── feedback in {file} → {working out the plan or the design again, or the tasks for it}` | the `feedback` item |
| A pause, on `/rn:dn` | `→ paused at {#id task name, plan, or design}` | whatever is unsettled, and a `notes` item on where the task stands |

## Finding the session

1. The `steering.md` this conversation has been working on.
2. Otherwise the one the current branch changed whose `status` is not `finished`:
   `git diff --name-only $(git merge-base HEAD origin/HEAD) HEAD -- '.rn/*/steering.md'`
   (`git remote set-head origin --auto` first when `origin/HEAD` is not set).

None, and `/rn:up` was given words → start a session from them. None, and no words → say there is
no session on this branch: check out the session's branch, or give `/rn:up` what to do. Only one
whose `status` is `finished` → say it is finished. Either way, stop.

A session whose `rn` field's first two numbers are `0.9` is taken up as it stands, since its record
has this form. One with no `rn` field, or lower, was started under an earlier rn: `/rn:up` brings
it to the current form; any other command asks the user to run `/rn:up` first, and stops.

## Bringing an older session to the current form

The old record is the user's request and what was done so far. The goal is worked out again from
it, since an older record may not hold why the user wants the goal, and every later decision is
judged by it.

1. Read the old `steering.md` and whatever else the old version left in the session's directory.
2. Work out the plan as `/rn:up` does on a start, with the session's branch, pull request and
   directory in place of new ones and the old record as the request: ask only what it leaves
   unclear.
3. The first write of the new `steering.md` replaces the old one. What an old design the user
   approved settled goes into the design's content as agreed points; what was done becomes Facts in
   Assumptions, each saying where; the other old files are removed, and stay readable in git.
4. Stop at a new Plan sign-off.
