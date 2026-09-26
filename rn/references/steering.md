# steering.md

The one file a session keeps. A fresh conversation resumes from it and git alone, and every command
finds its way by its field names and headings, so they stay exactly as written.

## Template

```markdown
---
rn: <installed rn version>
pr: <the session's pull request URL>
design: <the document that sets out a Design sign-off's choices: among the repository's design documents, or design.md beside this file>
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

### [ ] #1: Plan sign-off

**Purpose**: <the user agrees this plan before any work starts>

**Purpose reached when**:

- <the user approved the plan>

### [ ] #2: <task name>

**Purpose**: <what this task reaches, and the line of Goal reached when it serves>

**Purpose reached when**:

- <a state that shows the Purpose reached>

# State

- **Feedback**: none
- **Notes**: none
```

- Tasks are taken in the order written and end at a sign-off: "Design sign-off" for a choice that is
the user's, "Finished work sign-off" for the finished work. A task is marked `[x]` when the conductor
decides its Purpose is reached, a sign-off when the user approves it. A task added later takes the
next unused id.
- `status` is `finished` from the approval of the Finished work sign-off.
- `Feedback` is the user's words asking for a revision, kept until the conductor decides it is
  answered. `Notes` is what the next conversation needs that nothing else records.
- `evaluations/`, beside `steering.md`, holds every evaluation until the Finished work sign-off.

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
it up to date; any other command asks the user to run `/rn:up` first, and stops.

## Bringing an older session up to date

The old `steering.md` is the user's request and the record of the work so far. The session is brought
up to date by taking `/rn:on`'s steps on it, rather than by converting a format that changed from
version to version.

1. `git mv` it to `steering.old.md` beside it.
2. Take the steps of `/rn:on` (`${CLAUDE_PLUGIN_ROOT}/skills/on/SKILL.md`), the session's branch,
   pull request, and directory in place of new ones, with `steering.old.md` as the request, removed
   once `steering.md` is written: ask only what it leaves unclear, and plan from the work already done.
