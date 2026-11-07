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

- **One design tree back from the goal, for O1**: rn plans every deliverable the goal needs back
  from it in one tree, so no deliverable goes missing or comes out of order.
- **Made from a best practice, for O1**: rn builds each deliverable by the best practice of its
  kind toward what its people are after, where an AI starting from scratch maps it from similar
  text.
- **Checked by purpose, not by rules, for O1**: rn checks whether the people a deliverable is for
  get what they're after, so the user gets no findings off the purpose to sort.
- **Asked only what's theirs, for O1**: rn asks the user one point at a time in the main
  conversation, and only what the purpose and the best practices leave to them. It decides the
  rest and explains it at the end. A point that a turn finds open goes back to the main
  conversation, the user and rn settle it there, and the turn starts again.
- **Tried as it's used, for O1**: rn tries each deliverable as its people would use it, so it
  serves them in use, not only on reading.
- **The steps held on every run, for O1**: on every run, [Lane](../lane/product-vision.md) holds
  the steps of each practice, so no deliverable misses a step that an AI skipped on one run.
- **Picked up where it stopped, for O1**: rn goes on from the tree where the work stopped, so it
  doesn't ask the user again what they already answered.
