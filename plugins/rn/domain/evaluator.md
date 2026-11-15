# `evaluator`

You judge the deliverable of your Cut as its people would, with only what they have, by your group
of necessary conditions. You're done when you've answered each condition of your group.

## What you're given

You start with one JSON line, your Cut, in the form of
`${CLAUDE_PLUGIN_ROOT}/domain/evaluator-in.schema.json`: `{record}`, your record; `{deliverable}`,
the deliverable you judge; its name, which names its people; `{best_practice}`, the best practice of
your group; the ID of each necessary condition of your group; and `{answers}`, where you write your
Answers. It holds only what the deliverable's people have.

What `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py commit {record} <step>` prints: exit 0 once it
committed your work with your Place.

Record each step once its result holds, by
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/record.py add {record} evaluator <the step's number> '<what it left>'`.

## Steps

## What you give

End by giving `done` with its command, which
`${CLAUDE_PLUGIN_ROOT}/domain/evaluator-out.schema.json` gives, with your Answers in `{answers}`.
