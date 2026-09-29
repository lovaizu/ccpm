# The session's record

A session is its directory `.rn/{yyyymmdd}-{slug}/`, the README and design document, and git. A fresh
conversation, and every later version of `rn`, resumes from these alone, so the layout, field names,
and headings stay exactly as written here.

## steering.md

```markdown
---
rn: <installed rn version>
pr: <the session's pull request URL>
status: running
ux: <path of the README that says what the product should be to whoever uses it; README.md when none is settled>
design: <path of the design document that says how it is built; docs/design.md when none is settled>
---

# Goal

<what the user wants and why, as agreed with them>

# Goal achieved when

- <a state of the product that shows the goal achieved>

# Assumptions

- **Fact** (<how it was checked, or "the user decided">): <what the plan rests on>
- **Assumption**: <what the plan rests on without having checked it>

# Rules

- Commit and push every change
- <what a generator cannot tell from the goal, such as this repository's conventions>

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off
### [ ] #3: <task name>

**Purpose**: <what this task does for the goal>

**Purpose achieved when**:

- <a state checked on the real thing>

### [ ] #4: Deliverable sign-off
```

- Tasks are taken in the order written. A task is marked `[x]` when the conductor decides its purpose
  is fulfilled, a sign-off when the user approves it. A task added later takes the next unused id.
- `status` becomes `finished` when the Deliverable sign-off is approved.

## open/

What is not yet settled, beside `steering.md`, one file per item, named `{NN}-{kind}-{about}.md`:
`{NN}` is the next number after the highest in `open/`, from `01`; `{kind}` is `check` (a generator's
self-check), `evaluation` (an evaluator's), `feedback` (the user's words from `/rn:gm`, kept whole), or
`notes` (what `/rn:dn` leaves for the next conversation); `{about}` names what it is about, such as
`task-3` or `plan`. An item leaves `open/` in the commit that settles it, and its text goes into that
commit's message.

## The decision line

Every commit the conductor makes ends with one line saying what was decided and what comes next:

```
● {#id task name | plan | design | deliverable | the sign-off name} ── {what was decided} → {next move}
```

The last decision line on the branch is where the session stands: a later conversation takes up its
next move. When the session stops at a sign-off, the next move is `waiting for the {sign-off name}`.

## Finding the session

1. The `steering.md` this conversation has been working on.
2. Otherwise the one this branch changed:
   `git diff --name-only $(git merge-base HEAD origin/HEAD) HEAD -- '.rn/*/steering.md'`
   (`git remote set-head origin --auto` first when `origin/HEAD` is not set).
3. Otherwise those changed on the branches of open pull requests
   (`gh pr list --state open --json headRefName`): propose one and wait.

None → "No open session. Run `/rn:on` to start." A finished session → say so. Either way, stop.

A session with no `rn` field, or one whose first two numbers differ from `version` in
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, was started under an earlier `rn`. `/rn:up` brings
it to the current form; any other command asks the user to run `/rn:up` first, and stops.

## Bringing an older session to the current form

The old record is the user's request and what was done so far. Its format changed from version to
version, so rather than converting it, the goal is worked out again from it.

1. `git mv` the old `steering.md` to `steering.old.md` beside it.
2. Work out the plan as `/rn:on` does (`${CLAUDE_PLUGIN_ROOT}/skills/on/SKILL.md`), with the
   session's branch, pull request, and directory in place of new ones and `steering.old.md` as the
   request: ask only what it leaves unclear, and carry over what was done.
3. Remove `steering.old.md` and anything else the old version left in the directory in the commit
   that writes the new `steering.md`. The session stops at its new Plan sign-off.
