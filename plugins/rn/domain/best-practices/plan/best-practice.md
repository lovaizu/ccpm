# `plan`

## Goal

The maker builds every deliverable that the user's goal needs, each after what it needs and from settled decisions, and the user knows where the work stands.

## Template

[design-tree.schema.json](design-tree.schema.json)

## Example

[example.json](example.json), a copy of [../../../../../.rn/20261107-rn/design-tree.json](../../../../../.rn/20261107-rn/design-tree.json)

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The plan holds every deliverable that the goal needs, each after the deliverables it needs. |
| C2 | The maker builds each deliverable from settled decisions, and asks the user only what's theirs to decide. |
| C3 | The maker and the user see where the work stands, and pick it up from there. |
| C4 | The plan stays true as the work changes it. |

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

**Thinking**

Every deliverable in the plan is there to serve the goal, so the goal decides what goes in and what stays out. Write what the user is trying to achieve as one sentence with the user as its subject. Ask why until the answer is the user's own purpose and no longer a deliverable. Name in `by` who settled it. Check that each deliverable of the plan serves the goal, and drop one that serves nothing.

### N2

Does the tree hold every deliverable that the goal needs?

**Thinking**

A deliverable left out shows up only when the work reaches it, and the work stops there. A [work breakdown structure](https://en.wikipedia.org/wiki/Work_breakdown_structure) finds every deliverable up front by working back from the goal. Decide the tree in order. First, ask which deliverables together make the goal true. Second, for each, ask which deliverables it takes its content from. Repeat until a deliverable takes nothing. Third, where a decision needs facts that no one has found yet, put a research deliverable before it.

**Steps**

1. Put each research deliverable at the top level, in the order of the work.

### N3

Does each deliverable name its kind, with a best practice for that kind or a deliverable before it that makes one?

**Thinking**

A deliverable made without a best practice meets no stated condition, so no one can tell whether it's good. Give each deliverable the kind whose best practice it meets, by the folder name of that best practice. Where a kind has no best practice yet, put a deliverable that makes one, of the kind `meta`, at the top level before the first deliverable of that kind.

### N4

Does each deliverable name the deliverables it takes content from and those that must pass before it starts, and come after all of them?

**Thinking**

A deliverable started before its inputs rests on a guess. Give each deliverable, in `inputs`, the path of each deliverable it takes content from, and in `preconditions`, the path of each one that must pass before it starts, each of a kind that its best practice names there. Use paths, not kinds, since deliverables of one kind can serve different products. Then let a script order the deliverables by these paths, as a [topological sort](https://en.wikipedia.org/wiki/Topological_sorting) gives an order that keeps every dependency, instead of working out the order case by case.

**Steps**

1. After each change, have a script, such as rn's `tree.py`, check that each deliverable comes after its inputs and preconditions, that each research deliverable serves a later decision, and that a later deliverable uses each meta deliverable's kind.
2. Order the tests by level: unit, then architecture, then product vision, each after the level below passes. A higher level finds a fault later, at a higher cost.
3. Put a check, and a test that shows the check failing, before the deliverables that trust its results, as [the architecture best practice](../architecture/best-practice.md#n14) trusts a check only then.

### N5

Does each deliverable hold the decisions and the open points for each necessary condition of its best practice?

**Thinking**

The maker builds a deliverable from the decisions that answer its best practice's conditions, and asks about the points still open instead of guessing. Give each deliverable the necessary conditions of its best practice, in that best practice's order, each with its decisions. Leave a point's `decided` null while it's open. Settle each decision once its inputs exist, and no earlier, as the [last responsible moment](https://blog.codinghorror.com/the-last-responsible-moment/) avoids a decision that rests on a guess. After each result, revise the plan forward from it.

### N6

Does each decision say who settled it?

**Thinking**

The user should spend their time only on the decisions that are theirs. Name in `by` who settled each decision: the user, the maker, reasoning from the goal and the best practices, or research. Keep the grounds out of the tree, and write them in the commit message that makes the decision, so that the user finds them in git.

### N7

Does each deliverable's name say what it brings toward the goal?

**Thinking**

The user reads the plan to see where the work stands and what comes next, without opening each deliverable. For each deliverable, ask what holds toward the goal once it exists, and write that as its name. Leave out its path and its kind, which have fields of their own.

### N8

Does each deliverable show its status and which necessary conditions it meets?

**Thinking**

Whoever picks up the work must go on from where it stopped, without reading back through what came before. Keep each deliverable's status: `open`, `doing`, or `done`. Keep, for each necessary condition, whether the deliverable meets it, in `good`. The work then resumes at the first deliverable that isn't done.

### N9

After a change to a node, does every node that the change touches agree with it?

**Thinking**

A node that a change touches, left unread, goes on saying what held before. After each change to a node, go through the nodes that a script, such as rn's `tree.py`, lists: up to the goal, then the later decisions of the deliverable, then the deliverables before and after it that it takes from or gives to. Answer each as holding or as changed, as a checker such as Lane's `every_item` asks. Start the list again after each change.

### N10

Does the tree hold only what holds now?

**Thinking**

A reader acts on what the plan says, and reads any history in it as part of the current decision. Keep only what holds now. A deliverable that's done keeps one line: its name, path, kind, and status. A research deliverable goes once the decisions hold what it found. Git keeps how each point came about.
