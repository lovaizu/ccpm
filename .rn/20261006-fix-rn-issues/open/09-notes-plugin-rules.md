# Plugin rules, rewritten from zero

Agreed with the user one point at a time; the rules are written from these points, not patched.

## Purpose of the rules

A plugin that achieves its purpose comes out simple, never heavy, and is made and checked with little
effort.

- How a plugin is made and how it is checked are decided together, since a way of making cannot be
  judged better without a check that shows it.
- The way of making is not assumed (one shared flow with domain parts is only one candidate, beside a
  short self-contained prompt per plugin and the official plugins' shape). It is chosen after the
  form of the check is decided, by comparing the candidates with that check.

## What the check shows

- What the user got: whether the user actually gets each gain the plugin's README promises.
- What the user spent for it: how long they waited, how much they read to decide, and how many times
  they were called. Every part can work while the whole keeps the user waiting for hours, as rn 0.9.0
  did; looking only at what was got misses it.

## How the check is run

- Day to day, a change is judged by scenes: each starts from the state just before the moment the user
  gets a gain and ends at the first result that shows it, so it runs in minutes.
- At each milestone, the README's whole story is run once, the only run that shows what the user
  spent; rn 0.9.0, checked by scenes alone, kept the user waiting 2 h 43 min unseen.
- The story, its starting state and the version compared against (the one in use) are fixed first
  and not changed on the way: the rebuild's comparison never finished because its subject changed
  four times.

## Who plays the user

- An AI stand-in plays the user, handed only what the README tells a user and what they want.
- Scenes run with `claude -p`; the whole story at a milestone runs in a real interactive session, since
  `-p` behaves otherwise (in an interactive session an agent started with the Agent tool runs in the
  background, #44), and what only shows there would be missed.
- Whether an interactive session can be driven this way is not yet checked; a small try settles it
  before anything rests on it.

## How a run turns into fixes

- The cause is found from the records, not the outcome: the JSONL of every conversation and subagent
  the run started is traced, what each role was handed, did and returned, before a fix is chosen. In
  the rebuild, 41 of 44 commits were made before any trial's JSONL was read.
- A run's findings are gathered whole and grouped by cause before anything is fixed, and only the
  cause's place is fixed; a sentence is not added per symptom. An AI's behavior varies from run to
  run, so one sighting does not show a cause (e923168 added two sentences from one stopped run).
- A fix holds when the scene where it tripped runs again without it; at a milestone, the plugin is
  compared, without saying which is which, with the version in use.

## Staying simple

- A plugin starts minimal: its purpose and its domain parts. Anthropic's own guidance is the same:
  "start by testing a minimal prompt ... then add clear instructions ... based on failure modes"
  (Effective context engineering for AI agents), and "Write minimal instructions: Create just enough
  content to address the gaps" (Skill authoring best practices).
- Something is added only for a failure reproduced in a scene.
- At each milestone report and each request to merge, each plugin's size (what a call reads, in words)
  is shown beside the version in use, and any growth comes with the failure it prevents. No CI and no
  budget file: the user, who merges, judges it there.
- Size is the measure of simple, not of good: rn 0.9.0 was smaller than 0.8.0 and did harm. Whether
  the plugin achieves its purpose is the check's to show.

## Open

- How the way of making is chosen.
