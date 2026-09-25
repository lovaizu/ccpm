# Run the session to the user's next decision

The session goes on without the user until a decision is theirs. You, the main conversation running
the session, own `steering.md` and decide every next move by the Goal; the work is done by one agent
and evaluated by another. A later conversation knows only `steering.md` and git, so each decision
goes into `steering.md`, not only into this conversation.

## A turn

Take the task at `Next`.

A sign-off task is the user's decision: stop for the user, below.

When `Next` says the task has been evaluated but not yet decided on, decide on that evaluation. When it
says the work is done but not yet evaluated, have those commits evaluated. Otherwise start a fresh agent
with `Agent` to do the task. Give it the path of `steering.md`, the task's id, and
`${CLAUDE_PLUGIN_ROOT}/references/viewpoints.md`, whose Task result section is what it must reach and
check its work against; on a retry, the evaluation whose Mores it must answer too. It does the task,
commits and pushes its work, leaves `steering.md` to you, and returns the commits. You do not do the
task yourself: your context has to last until the user's decision.

Have the task result evaluated, decide on it, and take the next turn.

## Having it evaluated

Start a fresh general-purpose agent with `Agent`. Give it `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md`
to follow, the kind — Plan, Design choice, Task result, or Finished work — the path of `steering.md`,
and the file for its evaluation: `evaluations/{NN}-{plan | design-{id} | task-{id} | finished-work}.md`
next to `steering.md`, `{NN}` counting up from `01` across the session's evaluations. For a task
result, give it the task's id and its commits too. Give it nothing else. Your reasons and how the work
came about would pull it toward your view. Commit the evaluation and push, so the user can tie it to
what it evaluated.

## Deciding on an evaluation

Read its Mores, and decide by the Goal:

- **Reached** → go on. A task result: mark the task's steps `[x]`. A plan: take the next turn. A design
  choice or the finished work: stop for the user at its sign-off.
- **Short, and another try the same way can close the gap** → a task result: send it back with the
  Mores. A plan or a design choice: revise it, commit, push, and have it evaluated again. The finished
  work: add a task before the Evaluation sign-off that closes the gap.
- **Short, and the way itself does not reach the Goal** — the same gap comes back, or the Mores show
  the approach cannot close it → choosing another way is the user's: add a Design sign-off.
- **What decides it is the user's to weigh** — taste, scope, or cost against benefit, or a change to
  the Goal or Goal reached when they approved → add a Design sign-off for it.

A Design sign-off goes in as the next task. The tasks not yet complete — a task whose way fell short
among them — move into `Notes`, as tasks planned before the choice, so the plan written after it is
the only way on.

Set `Next` in `State`, commit `steering.md`, and push. Show the decision as one line:

```
● {#id task name | plan | design choice | finished work} ── evaluated: {passes | fails ({the More that decides it})} → {what you do next}
```

## Stopping for the user

The user decides from what is in front of them, so have it ready and evaluated first:

- **Plan sign-off** → the plan, evaluated as Plan.
- **Design sign-off** → set out the choices, what each costs and gives, and your recommendation, where
  the repository keeps its designs, and set the `design` field to that document; when the repository
  keeps none, set them out in the sign-off task itself. When the way fell short, name the attempt and
  its commits, so the choice is made knowing them. Have it evaluated as Design choice.
- **Evaluation sign-off** → the finished work, evaluated as Finished work.

An evaluation already passed, with nothing it evaluated changed since, is still good.

Commit and push. Open your message with the session's map, in the user's language, tasks in the order
they run:

```
── {slug}: {the Goal in one line} ──
✅ {#id done task name / …}
👉 {#id sign-off name} ── {what you need from the user}
⬜ {#id task name ahead / …}
({what happens after this stop})

Draft PR: {url}
```

Ask them to read what the decision is about on the pull request, with your recommendation. They
answer with `/rn:ty` to approve, or `/rn:gm <feedback>` to ask for changes; at a Design sign-off,
`/rn:ty` takes your recommendation and `/rn:ty <choice>` another choice.

## After the user decides

`/rn:up` goes on from here. What `Next` says is under way comes first: a task result or revision to
evaluate, or an evaluation to decide on.

At a Design sign-off the user approved, the choice is in `Assumptions`: write the tasks that follow
from it, as far as the next decision, from what `Notes` kept of the earlier plan, and have the plan
evaluated.

When `Feedback` holds the user's words asking for a revision and `Next` shows nothing under way for
it, it is about what the session stopped for; answer every point of it, and say in `Next` what is
under way:

- the plan or a design choice → revise it yourself, have it evaluated, and stop at the same sign-off;
- the finished work → add the tasks before the Evaluation sign-off that answer it, and run turns.

`Feedback` stays until the revision passes its evaluation, so the evaluator can check it against the
user's words. Then, for a point from a pull request review thread, reply on the thread with what
changed and the commit, in the language of the comment, leaving resolving it to the user; and set
`Feedback` to none.
