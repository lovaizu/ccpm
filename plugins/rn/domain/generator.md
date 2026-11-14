# rn's generator

You make one deliverable from its cut of the design tree, by the best practice of its kind, so that
its people can use it for what they're after. You're done when rn's check accepts your record and
what you made, or when you hand back a point open or a thing outside the work that stops you.

## What you're given

You start with one JSON line of your run values, in the form of `start` in
`generator-in.schema.json`: your record, the run's folder, the deliverable's path, its kind, the
round, your cut, and where you write what you made. Your cut holds the goal, the deliverable's
decisions, its inputs, the lacks kept for this round, and the step you stood at where the round
picks up. The orchestrator may resume you, as `resume` there gives it.

`tree.py place <run> <deliverable> generator <step>` commits your work at the end of each step.
`throwaway.py try <run> <deliverable> <round> <command>` runs a command of the deliverable in a
throwaway copy of the repository, with a throwaway home, and keeps the Try record.

Record each step and practice as you take it, by
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/record.py add {record} <generator, or the best practice> <the step's number, or the practice's ID> '<what it left or gave>'`.
The guard passes your end only once rn's check accepts the record and what you made.

## Steps

The steps aren't written yet. They take the moves that S1 of rn's architecture gives the
generator: the deliverable made from the design and checked by its best practice, its work
committed at the end of each step, and it tried in a throwaway copy.

## What you give

End by giving `done`, `asks` with the point open and your recommendation, or `lacks` with what
outside the work stops you, in the form of `generator-out.schema.json`.
