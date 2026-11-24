# Product vision of overnight

## Roles

- user\
  An AI that a person instructs, such as Claude Code, which asks overnight to run its work.

## Objectives and key results

- O1: the user has the work it asks for run as much as it can.
  - KR1.1: the share of pieces stopped by the usage limit, a wait for an answer, or the session
    closing. Lower is better.

The first key result of each objective comes first. Keep a change that improves a key result
only if none before it gets worse.
Key results have no targets, as a measure made a target stops being a good measure, by Goodhart's
law. They show whether a change brought its objective closer.

## Concept

overnight keeps each piece from stopping by the usage limit, a wait for an answer, or the session
closing.

- Waiting out the usage limit, for O1\
  A piece that the limit stops goes on after each reset, however often the limit comes back.
- Nothing to answer, for O1\
  Each piece gets its tools and a folder of its own up front, so no prompt waits for an answer.
- Running past the session, for O1\
  Each piece goes on after the session that asked for it closes.
