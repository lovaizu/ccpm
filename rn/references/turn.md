# Run the session to the user's next decision

The session goes on without the user until a decision is theirs. One agent makes each thing, another
evaluates it against `viewpoints.md`, and you, the main conversation, decide the next move by the
Goal. You keep `steering.md` and keep your own context for deciding: a later conversation knows only
`steering.md` and git, so every decision goes there.

## A turn

Take the task at `Next`. A sign-off is the user's: stop for them. Otherwise start a fresh agent with
`Agent`, giving it the path of `steering.md`, the task's id, and
`${CLAUDE_PLUGIN_ROOT}/references/viewpoints.md` (Task result) — on a retry, the evaluation too. It
commits and pushes its work, leaves `steering.md` to you, and returns its commits. Have them evaluated
and decide.

## Having it evaluated

Start a fresh general-purpose agent with `Agent`. Give it `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md`,
the kind (Plan, Design choice, Task result, or Finished work), the path of `steering.md`, a task
result's id and commits, and the file `evaluations/{NN}-{plan | design-{id} | task-{id} |
finished-work}.md`, `{NN}` counting up from `01`. Nothing else: your reasons would pull it toward your
view. Commit its evaluation and push.

## Deciding

By the Goal: accept, retry with the Mores, revise, or stop for the user. A way that keeps falling
short, or a change to what the user approved, is theirs to choose: add a Design sign-off as the next
task, and move the tasks not yet complete into `Notes`, as planned before the choice. Record the move
in `steering.md`, commit, push, and show it as one line:

```
● {#id task name | plan | design choice | finished work} ── evaluated: {passes | fails ({the deciding More})} → {next move}
```

## Stopping for the user

What the user decides on is evaluated first: the plan, the choices for a Design sign-off — set out
with what each costs and gives and your recommendation, where the repository keeps its designs
(`design` field) or in the sign-off task — or the finished work. Commit, push, and open your message
with the map, in the user's language:

```
── {slug}: {the Goal in one line} ──
✅ {#id task name / …}
👉 {#id sign-off name} ── {what you need from the user}
⬜ {#id task name / …}
({what happens after this stop})

Draft PR: {url}
```

Ask them to read it on the pull request, with your recommendation. They answer with `/rn:ty`
(`/rn:ty <choice>` for a choice other than yours) or `/rn:gm <feedback>`.

## After the user decides

`/rn:up` goes on from `Next`. After a chosen design, write the tasks that follow from it and have the
plan evaluated. With `Feedback`, revise what the user stopped at until its evaluation passes — the
plan or the choices yourself, the finished work through new tasks. Then reply on each pull request
thread it came from, with what changed and the commit, in the comment's language, leaving resolving
it to the user, and set `Feedback` to none.
