# Run the session to the user's next decision

The session goes on without the user until a decision is theirs. In each turn one agent does a task,
an evaluator evaluates the task result against its Purpose, and you, the main conversation running
the session, decide the next move by the Goal. A later conversation knows only `steering.md` and git,
so each decision goes into `steering.md`, not only into this conversation.

## A turn

Take the first task in `steering.md` not yet complete.

A sign-off task is the user's: stop for the user, below. Before an Evaluation sign-off, have the
finished work evaluated first, and decide on its evaluation as for a task.

Otherwise, start a fresh agent with `Agent` to do the task. Give it the path of `steering.md`, the
task's id, and `${CLAUDE_PLUGIN_ROOT}/references/viewpoints.md`, whose Task result section is what it
must reach and check its work against; on a retry, the Mores it must answer too. It commits and
pushes its work, and returns the commits. You do not do the task yourself: your context has to last
until the user's decision.

Have the task result evaluated, below. Then decide by the Goal, reading its Mores:

- the Purpose is reached → mark the task's steps `[x]`;
- it falls short, and another try the same way can close the gap → send it back with the Mores;
- the way itself falls short → rewrite the tasks from where the session stands, and have the plan
  evaluated before going on;
- what decides it is the user's to weigh: taste, scope, or cost against benefit → add a Design
  sign-off task for it as the next task.

Set `Next` in `State`, commit `steering.md`, and push. Show the decision as one line, then take the
next turn:

```
● #{id} {task name} ── evaluated: {passes | fails ({the More that decides it})} → {what you do next}
```

## Having it evaluated

Start a fresh general-purpose agent with `Agent`. Give it `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md`
to follow, the kind — Plan, Task result, or Finished work — the path of `steering.md`, and the file for
its evaluation: `evaluations/{NN}-{plan | task-{id} | finished-work}.md` next to `steering.md`, `{NN}`
counting up from `01` across the session's evaluations. For a task result, give it the task's id and
its commits too. Give it nothing else. Your reasons and how the work came about would pull it toward
your view. Commit the evaluation and push, so the user can tie it to what it evaluated.

## Stopping for the user

The user decides from what is in front of them, so prepare it first:

- Design sign-off → set out the choices with what each costs and gives, and your recommendation, in a
  document that stays with the work: where the repository keeps its designs, or next to `steering.md`
  when it keeps none. Set the `design` field to its path. Write the tasks that follow from the
  recommended choice, as far as the next decision, and have the plan evaluated: the user approves the
  choice and the tasks together.
- Evaluation sign-off → the finished work has been evaluated, as in a turn.

Commit and push. Open your message with the session's map, in the user's language:

```
── {slug}: {the Goal in one line} ──
✅ #{first}–#{last}   {done task names, separated by /}
👉 #{id}      {sign-off name} ── {what you need from the user}
⬜ #{first}–#{last}   {task names ahead, separated by /}
({what happens after this stop})

Draft PR: {url}
```

Ask them to read what the decision is about on the pull request, with your recommendation. They
answer with `/rn:ty` to approve, or `/rn:gm <feedback>` to ask for changes.
