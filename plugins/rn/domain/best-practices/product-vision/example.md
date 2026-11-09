# Product vision of rn

## Roles

- **user**: one who asks rn for a deliverable, such as a document, code or a plugin, for the people
  it's for.

## Objectives and key results

- O1: the user has each deliverable they mean made, with which the people it's for achieve what
  they're after.
  - KR1.1: the share of the deliverables rn hands over that the people they're for couldn't use
    for what they're after. Lower is better.
  - KR1.2: the time from the user's request to the deliverable, the user's own time answering rn
    included. Shorter is better.

KR1.1 comes first: keep a change that improves a key result only if none before it
gets worse.
Key results have no targets, as a measure made a target stops being a good measure, by Goodhart's
law. They show whether a change brought its objective closer.

## Concept

rn instead of letting an AI agent plan the work once, carry it out task by task, and have reviewers
look for faults:

- **Replanned toward the goal, for O1**: rn plans back from the goal and plans again after each
  finished deliverable and each answer, so what it learns on the way changes the rest of the work,
  and a misread in the first plan doesn't last to the end.
- **One plan with every decision, for O1**: rn keeps the goal, the deliverables it needs, and each
  decision with who made it in one plan, so each deliverable serves the goal and the user decides
  each point once.
- **Made by the established way, for O1**: rn makes each deliverable by the way its field has
  established for its kind, so its quality doesn't rest on what an AI thinks of at the moment, and
  rn asks the user only what that way leaves open.
- **Judged by its people, for O1**: rn judges each deliverable by what lets its people do what
  they're after, not by the faults a reviewer finds, so small findings off the purpose don't pile
  up on it.
