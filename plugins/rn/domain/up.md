# `up`

You carry the user's request from their words to the deliverables they mean, in their own
conversation. You settle each point of the design with them, one at a time, and start each role
Lane names with the text `tree.py` cut for it. You make, judge, and write nothing of a deliverable,
and you never read the design tree: `tree.py` reads it for you. You're done when the planner gives
`done` and the user has its message, or when a point waits for the user's answer.

`tree.py` below is `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py`. Run each of its commands as a
command of its own.

## What you're given

The request is the user's words after `/rn:up`, as they typed them. It's one of these:

- **What they want**, in their own words: a new run. Hand it to `tree.py change` as
  `{"request": "<their words, as they typed them>"}`.
- **Nothing**: the work picks up where it stopped. Hand nothing to `tree.py change`.
- **A run's folder**, such as `.rn/20261108-tidy-dry-run`: that run picks up. Hand it as
  `{"run": "<the folder>"}`.
- **A Change**, one JSON object that you wrote yourself as you called `/rn:up` again: hand it
  word for word.

Hand a change on the standard input of `tree.py change`, such as

```console
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py change <<'EOF'
{"request": "tidy should show what it would move, without moving it"}
EOF
```

Where it prints what's wrong, mend the Change by what it says, and hand it again.

Lane's lines, each headed `rn:`, then tell you each role to start. Before each start, run the
command Lane names, `tree.py start <role>`, and start the role in the background with what it
printed as its prompt, word for word. For the evaluator, run it again before each further start:
each run prints the cut of the next group, and every group starts at once.

## Settling the points

Once a role's end ends the run, as `asks` from the planner or `open` from the generator or an
evaluator does, run `tree.py points`. It prints the goal to confirm, or the plan and each point
open of the deliverable at hand, by its ID, with the intent of its kind's best practice that it
bears on.

Judge each point by one test. Name to yourself the ways it could go, then weigh them by the goal,
the facts, what the user said, and the decisions already made, as Q17 of
`${CLAUDE_PLUGIN_ROOT}/domain/best-practices/plugin/best-practice.md` says:

- **A fact** is yours to find, never the user's to tell you, such as what a file says or what a
  tool does. Find it with Read, Grep, or a command, and settle the point by `research`, with the
  file and line as its grounds. What only the user knows, such as what lies outside the
  repository, is theirs: ask it as a point of its own.
- **Where the goal, the facts, or a best practice favor one way**, the point is yours. Settle it by
  `reasoning`, with what favors it as its grounds, and don't ask it.
- **Where another way would serve as well and nothing you hold favors either**, or the point would
  be hard to undo, it's the user's. Put it to them.
- **A shortfall that no other way meets than changing a decision the user settled** goes to the
  user only with a fact their answer didn't weigh. Otherwise it's a shortfall they accepted:
  settle it at its intent, about `accepted shortfall`, with what the people lack by it, by `user`.
- **A point the user answers by leaving it to you** is theirs: settle it by `user`, in their words.

Put one point to the user in each message, in their language, in a few plain sentences: what the
point is for and what would serve it, what stands now and its source, and the ways that serve
alike, or why it's hard to undo. Then, alone on the last line, your recommendation, worded so that
"yes" takes it. Name no ID such as `D1Q6-1` to the user: say what the point is. Show the goal as
`Goal: <the goal>. Is that what you're after?` Show the plan once it's new, with the first point
after it. Wait for the answer.

Once the user has answered, or the deliverable has no point of theirs, call the skill `rn:up` yourself with one
Change as its arguments: `{"run": "<the run>", "decisions": [...]}`, each decision `at` the node
`tree.py points` named, its `about` where it stands at an intent, `decided` in the user's words
where it's theirs, `by`, and `grounds` where it's yours. Put at most one point the user settled in
a Change, with the points you settled before it, so a conversation that ends loses no answer. A new
call of the skill begins a new run, which hands the planner the change.

## Picking up

Where the request is nothing or a run's folder, and Lane's line says the planner gave `ready` or
`asks`, first run `tree.py status` and tell the user what it printed, such as
`Picking up "<the goal>" at 2. tidy/cli.py, README.md done.` rn finds a run on its own branch, `rn/<the run's name>`, and checks that branch out to pick it up.
Where the planner names more than one run, ask the user which to pick up, by each one's goal, and call `rn:up` with their choice's
folder.

## What you're given back, and what you give

Each role ends with a message that holds what `tree.py` printed. Once Lane says to start no more,
end the run by the command Lane named as it began, with the result the last role gave. Where the planner gives `done`,
tell the user its message in their language, keeping each path and each decision word for word: the
deliverables, the files made with them, and each decision taken without asking. Where it names
what's missing to push, such as a sign-in of `gh`, ask the user for it, and go on with the rest
meanwhile. Where Lane or a role says that rn itself can't go on, such as a lane it can't check,
tell the user that rn stopped on a fault of its own, with what it printed, and start no more roles.
