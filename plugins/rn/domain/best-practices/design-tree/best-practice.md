# `design-tree`

## Goal

The maker builds every deliverable that the user's goal needs, each after what it needs and from settled decisions, and the user knows where the work stands.

## Template

[design-tree.schema.json](design-tree.schema.json)

## Example

[example.json](example.json), a copy of [../../../../../.rn/20261107-rn/design-tree.json](../../../../../.rn/20261107-rn/design-tree.json)

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The design tree holds every deliverable that the goal needs, each after the deliverables it needs. |
| C2 | The maker builds each deliverable from settled decisions, and asks the user only what's theirs to decide. |
| C3 | The maker and the user see where the work stands, and pick it up from there. |
| C4 | The design tree stays true as the work changes it. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | Does the goal state, in one sentence, what the user is trying to achieve? | goal |
| N2 | C1 | Does the tree hold every deliverable that the goal needs? | deliverables |
| N3 | C1 | Does each deliverable name its kind, with a best practice for that kind or a deliverable before it that makes one? | deliverables |
| N4 | C1 | Does each deliverable name the deliverables it takes content from and those that must pass before it starts, and come after all of them? | deliverables |
| N5 | C2 | Does each deliverable hold the decisions and the open points for each necessary condition of its best practice? | deliverables |
| N6 | C2 | Does each decision say who settled it? | deliverables |
| N7 | C3 | Does each deliverable's name say what it brings toward the goal? | deliverables |
| N8 | C3 | Does each deliverable show its status and which necessary conditions it meets? | deliverables |
| N9 | C4 | After a change to a node, does every node that the change touches agree with it? | goal, deliverables |
| N10 | C4 | Does the tree hold only what holds now? | goal, deliverables |

## Practices

### N1

Does the goal state, in one sentence, what the user is trying to achieve?

Every deliverable in the design tree is there to serve the goal, so the goal decides what goes in and what stays out.

1. *While deciding.* Write what the user is trying to achieve as one sentence with the user as its subject.
2. *While deciding.* Ask why until the answer is the user's own purpose and no longer a deliverable.
3. *While deciding.* Name in `by` who settled it.
4. *While making.* Check that each deliverable of the design tree serves the goal, and drop one that serves nothing.

### N2

Does the tree hold every deliverable that the goal needs?

A deliverable left out shows up only when the work reaches it, and the work stops there. A [work breakdown structure](https://en.wikipedia.org/wiki/Work_breakdown_structure) finds every deliverable up front by working back from the goal.

1. *While deciding.* Ask which deliverables together make the goal true.
2. *While deciding.* For each, ask which deliverables it takes its content from. Repeat until a deliverable takes nothing.
3. *While deciding.* Where a decision needs facts that no one has found yet, put a research deliverable before it.
4. *While making.* Put each research deliverable at the top level, in the order of the work.

### N3

Does each deliverable name its kind, with a best practice for that kind or a deliverable before it that makes one?

A deliverable made without a best practice meets no stated condition, so no one can tell whether it's good.

1. *While deciding.* Give each deliverable the kind whose best practice it meets, by the folder name of that best practice.
2. *While deciding.* Where a kind has no best practice yet, put a deliverable that makes one, of the kind `meta`, at the top level before the first deliverable of that kind.

### N4

Does each deliverable name the deliverables it takes content from and those that must pass before it starts, and come after all of them?

A deliverable started before its inputs rests on a guess.

1. *While deciding.* Give each deliverable, in `inputs`, the path of each deliverable it takes content from, and in `preconditions`, the path of each one that must pass before it starts, each of a kind that its best practice names there. Use paths, not kinds, since deliverables of one kind can serve different products.
2. *While making.* Let a script order the deliverables by these paths, as a [topological sort](https://en.wikipedia.org/wiki/Topological_sorting) gives an order that keeps every dependency, instead of working out the order case by case.
3. *While making.* After each change, have a script, such as rn's `tree.py`, check that each deliverable comes after its inputs and preconditions, that each research deliverable serves a later decision, and that a later deliverable uses each meta deliverable's kind.
4. *While making.* Order the tests by level: unit, then architecture, then product vision, each after the level below passes. A higher level finds a fault later, at a higher cost.
5. *While making.* Put a check, and a test that shows the check failing, before the deliverables that trust its results, as [the architecture best practice](../architecture/best-practice.md#n14) trusts a check only then.

### N5

Does each deliverable hold the decisions and the open points for each necessary condition of its best practice?

The maker builds a deliverable from the decisions that answer its best practice's conditions, and asks about the points still open instead of guessing.

1. *While deciding.* Give each deliverable the necessary conditions of its best practice, in that best practice's order, each with its decisions.
2. *While deciding.* Leave a point's `decided` null while it's open.
3. *While deciding.* Settle each decision once its inputs exist, and no earlier, as the [last responsible moment](https://blog.codinghorror.com/the-last-responsible-moment/) avoids a decision that rests on a guess.
4. *While making.* After each result, revise the design tree forward from it.

### N6

Does each decision say who settled it?

The user should spend their time only on the decisions that are theirs.

1. *While deciding.* Name in `by` who settled each decision: the user, the maker, reasoning from the goal and the best practices, or research.
2. *While making.* Keep the grounds out of the tree, and write them in the commit message that makes the decision, so that the user finds them in git.

### N7

Does each deliverable's name say what it brings toward the goal?

The user reads the design tree to see where the work stands and what comes next, without opening each deliverable.

1. *While making.* For each deliverable, ask what holds toward the goal once it exists, and write that as its name.
2. *While making.* Leave out its path and its kind, which have fields of their own.

### N8

Does each deliverable show its status and which necessary conditions it meets?

Whoever picks up the work must go on from where it stopped, without reading back through what came before. The work then resumes at the first deliverable that isn't done.

1. *While making.* Keep each deliverable's status: `open`, `doing`, or `done`.
2. *While making.* Keep, for each necessary condition, whether the deliverable meets it, in `good`.

### N9

After a change to a node, does every node that the change touches agree with it?

A node that a change touches, left unread, goes on saying what held before.

1. *While making.* After each change to a node, go through the nodes that a script, such as rn's `tree.py`, lists: up to the goal, then the later decisions of the deliverable, then the deliverables before and after it that it takes from or gives to.
2. *While making.* Answer each as holding or as changed, as a checker such as Lane's `every_item` asks.
3. *While making.* Start the list again after each change.

### N10

Does the tree hold only what holds now?

A reader acts on what the design tree says, and reads any history in it as part of the current decision. Git keeps how each point came about.

1. *While making.* Keep only what holds now.
2. *While making.* Keep one line for a deliverable that's done: its name, path, kind, and status.
3. *While making.* Drop a research deliverable once the decisions hold what it found.
