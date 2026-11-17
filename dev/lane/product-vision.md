# Product vision of Lane

## Roles

- user\
  One who builds a Claude Code plugin whose roles work in steps, either a person or an AI.

## Objectives and key results

- O1: the user has their plugin's roles notice the moment they leave the steps or the order the
  user designed.
  - KR1.1: the share of the roles' moves that Lane judges right. Higher is better.
  - KR1.2: the time from Lane taking in a move to giving back its judgment. Shorter is better.

KR1.1 comes first: keep a change that improves a key result only if none before it gets worse.
Key results have no targets, as a measure made a target stops being a good measure, by Goodhart's
law. They show whether a change brought its objective closer.

## Concept

Lane gives a role that leaves its step the step's own sentence, so that the role notices at once.

- The order as routes, for O1\
  The user names the move after each result, and a role started out of order gets the moves due.
- Checks laid, not written, for O1\
  The user approves their steps and routes as Lane lays them, and writes no check.
