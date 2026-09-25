# steering.md

The one file a session keeps. A fresh conversation resumes from it and git alone, and every command
finds its way by its field names and headings, so they stay exactly as written.

## Template

```markdown
---
rn: <installed rn version>
issue: <the issue this session serves — omit when there is none>
pr: <the session's pull request URL>
design: <the document setting out a Design sign-off's choices — omit until there is one>
status: running
---

# Goal

<what the user wants and why, as agreed with them>

# Goal reached when

- <a state the user gains>

# Assumptions

- **Fact** (<how it was checked>): <what the plan rests on, including each choice the user made>
- **Assumption**: <what the plan rests on without having checked it>

# Rules

- commit and push every change
- <what an implementer could not know from the Goal: this repository's conventions>

# Tasks

### #1: Plan sign-off

**Purpose**: The user agrees this plan before any work starts.

**Prerequisites**: none

**Steps**:

- [ ] Approved by the user

**Purpose reached when**:

- The user approved the plan.

### #2: <task name>

**Purpose**: <what this task reaches, and the line of Goal reached when it serves>

**Prerequisites**: <task ids, or none>

**Steps**:

- [ ] <step>

**Purpose reached when**:

- <a state that shows the Purpose reached>

# State

- **Next**: #1 Plan sign-off
- **Feedback**: none
- **Notes**: none
```

- The tasks end at a sign-off: "Design sign-off" for a choice that is the user's, "Evaluation sign-off"
  for the finished work. A sign-off task has the one step `Approved by the user`. A task is complete
  when every step is `[x]`; a task added later takes the next unused id.
- `status` is `paused`, with `paused_at: <YYYY-MM-DD>`, from `/rn:dn` until `/rn:up`.
- `Next` is the task to take and how far it got. `Feedback` is the user's words asking for a revision,
  kept until the revision passes its evaluation. `Notes` is what the next conversation needs that
  nothing else records.
- `evaluations/`, beside `steering.md`, holds every evaluation until the Evaluation sign-off.

## Finding the session

1. The `steering.md` this conversation has been working on.
2. Otherwise the one this branch changed:
   `git diff --name-only $(git merge-base HEAD origin/HEAD) HEAD -- '.rn/*/steering.md'`
   (`git remote set-head origin --auto` first when `origin/HEAD` is not set).
3. Otherwise those changed on the branches of open pull requests
   (`gh pr list --state open --json headRefName`): propose one and wait.

None → "No open session. Run `/rn:on` to start." A finished session → say so. Either way, stop.

A session with no `rn` field, or one that differs from `version` in
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, was started under an earlier `rn`. `/rn:up` brings
it up to date; any other command asks the user to run `/rn:up` first, and stops.

## Bringing an older session up to date

Rewrite it in the template's shape so this `rn` can run it, with none of its plan or progress lost
and the wording the user approved unchanged. Earlier versions wrote the header as `Rn version:` and
`Design:` lines, named the criteria Acceptance criteria and Completion criteria, kept status in
`State`, had no Plan sign-off task (the plan was approved on the pull request), and ran their own
reviews as steps recorded in `checks/`; those reviews are replaced by this `rn`'s evaluations.

Commit `chore: bring session up to rn {version}`, push, and have the plan evaluated as in
`${CLAUDE_PLUGIN_ROOT}/references/turn.md`.
