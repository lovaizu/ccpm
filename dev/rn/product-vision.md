# Product vision of rn

## Roles

- **user**: one who asks rn for a deliverable, such as a document, code or a plugin, for the people
  it's for.

## Objectives and key results

- O1: the user has each deliverable they mean made, with which the people it's for achieve what
  they're after, and answers only the points that are theirs.
  - KR1.1: the share of the deliverables rn hands over that the people they're for couldn't use
    for what they're after. Lower is better.
  - KR1.2: the share of the points rn asks the user whose answer the purpose or a best practice
    settles. Lower is better.
  - KR1.3: the time from the user's request to the deliverable, the user's own time answering rn
    included. Shorter is better.

KR1.1 comes first and KR1.2 next: keep a change that improves a key result only if none before it
gets worse.
Key results have no targets, as a measure made a target stops being a good measure, by Goodhart's
law. They show whether a change brought its objective closer.

## Concept

rn instead of asking an AI in one prompt, reading its draft and fixing it:

- **Planned back from the goal, for O1**: rn lays out every deliverable the goal needs, and the
  order it needs them in, before it makes any, so none goes missing or comes out of order.
- **Made from a best practice, for O1**: rn builds each deliverable by the best practice of its
  kind toward what its people are after, where an AI starting from scratch maps it from similar
  text.
- **Checked as it's used, for O1**: rn tries each deliverable as its people would use it, and
  checks whether they get what they're after, not whether it follows rules, so the user gets no
  findings off the purpose to sort.
- **Asked only what's theirs, for O1**: rn asks the user one point at a time, and only what the
  purpose and the best practices leave to them. It decides the rest and explains it at the end.
- **Every step on every run, picked up where it stopped, for O1**: rn keeps each step of the
  best practice on every run, and goes on where the work stopped, so no deliverable misses a step
  an AI skipped once, and the user never answers a point twice.
