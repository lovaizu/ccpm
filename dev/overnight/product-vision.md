# Product vision of overnight

## Roles

- user\
  An AI, such as a Claude Code session, that stacks tasks for an AI and takes in their results.

## Objectives and key results

- O1: the user gets each task they stack done and takes in its result without watching the tasks
  run.
  - KR1.1: the share of stacked tasks whose result the user takes in without stepping in while
    the tasks run. Higher is better.

The first key result of each objective comes first. Keep a change that improves a key result
only if none before it gets worse.
Key results have no targets, as a measure made a target stops being a good measure, by Goodhart's
law. They show whether a change brought its objective closer.

## Concept

overnight carries each stacked task to its end without the user, so the user lets go after stacking.

- Resuming each task where the usage limit stopped it, for O1\
  The user restarts no task once the limit lifts.
- Ending each task as finished, or as given up with its reason, for O1\
  The user takes in the finished tasks and knows why the others ended.
