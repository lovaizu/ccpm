# Product vision of Lane

## Roles

- user\
  One who builds a Claude Code plugin whose roles work in steps, either a person or an AI.

## Objectives and key results

- O1: the user has each run of their plugin keep the steps and the order they designed.
  - KR1.1: the share of the plugin's runs whose steps or order differ from what the user designed.
    Lower is better.
  - KR1.2: the time from the user's first step or order for a plugin to its first run that keeps
    them. Shorter is better.

KR1.1 comes first: keep a change that improves a key result only if none before it gets worse.
Key results have no targets, as a measure made a target stops being a good measure, by Goodhart's
law. They show whether a change brought its objective closer.

## Concept

Lane holds each role of the user's plugin to the steps and order they wrote, on every run.

- The step said again, for O1\
  A role that Lane stops gets its step's own sentence, and goes back to the step.
- The order as routes, for O1\
  The user names the move after each result, and Lane gives and holds each next move.
- Checks laid, not written, for O1\
  The user approves their steps and routes as Lane lays them, and writes no check.
