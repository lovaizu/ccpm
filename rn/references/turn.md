# Run the session to the user's next decision

The session goes on without the user until a decision is theirs. In each turn one agent makes a
result, another judges it against what it must reach, and you, the main conversation running the
session, decide the next move by the goal. A later conversation knows only `steering.md` and git, so
each decision goes into `steering.md`, not only into this conversation.

## A turn

Take the first task in `steering.md` not yet complete.

A sign-off task is the user's: stop for the user, below. Before an Evaluation sign-off, have the
finished work judged first as the Session kind, and decide on its verdict as for a task.

Otherwise, start a fresh agent with `Agent` to do the task. Give it the path of `steering.md`, the
task's id, and `${CLAUDE_PLUGIN_ROOT}/references/purpose.md`, whose Result section is what it must
reach and check its work against; on a retry, the Mores it must answer too. It commits and pushes
its work, and returns the commits. You do not do the task yourself: your context has to last until
the user's decision.

Have the result judged, below, as the Result kind. Then decide by the goal, reading its Mores:

- the Purpose is reached → mark the task's steps `[x]`;
- it falls short, and another try the same way can close the gap → send it back with the Mores;
- the way itself falls short → rewrite the tasks from where the session stands, and have the plan
  judged as the Plan kind before going on;
- what decides it is the user's to weigh: taste, scope, or cost against benefit → add a Design
  sign-off task for it as the next task.

Set `Next` in `State`, commit `steering.md`, and push. Show the decision as one line, then take the
next turn:

```
● #{id} {task name} ── judged: {passes | fails ({the More that decides it})} → {what you do next}
```

## Having a result judged

Start a fresh general-purpose agent with `Agent`. Give it `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md`
to follow, the kind, the path of `steering.md`, and the file for its verdict:
`evaluations/{NN}-{kind}.md` next to `steering.md`, `{NN}` counting up from `01` across the
session's verdicts. For a Result, give it the task's id and its commits too. Give it nothing else.
Your reasons and how the result came about would pull it toward your view. Commit the verdict and
push, so the user can tie it to what it judged.

## Stopping for the user

Commit and push. Open your message with the session's map, in the user's language:

```
── {slug}: {the goal in one line} ──
✅ #{first}–#{last}   {done task names, separated by /}
👉 #{id}      {sign-off name} ── {what you need from the user}
⬜ #{first}–#{last}   {task names ahead, separated by /}
({what happens after this stop})

Draft PR: {url}
```

Ask them to read what the decision is about on the pull request, with your recommendation. They
answer with `/rn:ty` to approve, or `/rn:gm <feedback>` to ask for changes.
