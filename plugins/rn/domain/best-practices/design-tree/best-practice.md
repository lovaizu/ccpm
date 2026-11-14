# `design-tree`

## Goal tree

- The maker builds every deliverable that the user's goal needs, each after what it needs and from settled decisions, and the user knows where the work stands.
  - **C1** The design tree holds every deliverable that the goal needs, each after the deliverables it needs.
    - **N1** Does the goal state, in one sentence, what the user is trying to achieve? (goal)
    - **N2** Does the tree hold every deliverable that the goal needs? (deliverables)
    - **N3** Does each deliverable name its kind: the best practice of the field's established way of making it, or `specific` where the deliverable is this product's alone? (deliverables)
    - **N4** Does each deliverable name the deliverables it takes content from and those that must pass before it starts, and come after all of them? (deliverables)
  - **C2** The maker builds each deliverable from settled decisions, and asks the user only what's theirs to decide.
    - **N5** Does each deliverable hold the decisions and the open points for each necessary condition of its best practice? (deliverables)
    - **N6** Does each decision say who settled it? (deliverables)
  - **C3** The maker and the user see where the work stands, and pick it up from there.
    - **N7** Does each deliverable's name say what it brings toward the goal? (deliverables)
    - **N8** Does each deliverable show its status and which necessary conditions it meets? (deliverables)
  - **C4** The design tree stays true as the work changes it.
    - **N9** After a change to a node, does every node that the change touches agree with it? (goal, deliverables)
    - **N10** Does the tree hold only what holds now? (goal, deliverables)

## Template

[design-tree.schema.json](design-tree.schema.json)

## Example

[example.json](example.json), a copy of [.rn/20261107-rn/design-tree.json](https://github.com/lovaizu/ccpm/blob/main/.rn/20261107-rn/design-tree.json)

## Practices

### N1

Does the goal state, in one sentence, what the user is trying to achieve?

Every deliverable in the design tree is there to serve the goal, so the goal decides what goes in and what stays out. The method is the why laddering of goal-oriented requirements engineering, as Axel van Lamsweerde's [guided tour](https://doi.org/10.1109/ISRE.2001.948567) describes it: asking why moves up from a deliverable toward the purpose it serves.

1. *While deciding.* Write what the user is trying to achieve as one sentence with the user as its subject.
2. *While deciding.* Ask why until the answer is the user's own purpose and no longer a deliverable.
3. *While deciding.* Name in `by` who settled it.
4. *While making.* Check that each deliverable of the design tree serves the goal, and drop one that serves nothing.

### N2

Does the tree hold every deliverable that the goal needs?

A deliverable left out shows up only when the work reaches it, and the work stops there. A [work breakdown structure](https://en.wikipedia.org/wiki/Work_breakdown_structure) finds every deliverable up front by working back from the goal.

1. *While deciding.* Ask which deliverables together make the goal true.
2. *While deciding.* For each, ask which deliverables it takes its content from. Repeat until a deliverable takes nothing.
3. *While deciding.* Break each deliverable down until it's a work package: a part that ends at a check showing, on its own, that the people the goal serves get a part of what it promises them. A larger part leaves its maker to settle at once what no one checks between, and a smaller one passes checks that show nothing toward the goal.
4. *While deciding.* Where a decision needs facts that no one has found yet, put a research deliverable before it.
5. *While deciding.* Put each research deliverable at the top level, in the order of the work.

### N3

Does each deliverable name its kind: the best practice of the field's established way of making it, or `specific` where the deliverable is this product's alone?

A deliverable of a kind that every product shares has a way of making it that the field has settled, and its best practice brings that way to the maker. A deliverable of this product alone has no such way, and a best practice made for it would only restate the product's own decisions, which leaves nothing but trivia to meet. The method is the [Definition of Done](https://scrumguides.org/scrum-guide.html) of the Scrum Guide: where the organization's standards hold one, the work follows it, and where they don't, the team states what done means for that work.

1. *While deciding.* Give a deliverable the folder name of a best practice where the field has an established way of making it that holds across products, as it has for a README. Where a deliverable holds parts of several such kinds, its kind is the one whose best practice names the others for those parts.
2. *While deciding.* Give a deliverable of this product alone the kind `specific`, such as a file that keeps a run's state, a file of the product's own specification, an integration test of its architecture, or an end-to-end test. The tree's decisions make it, and the check that its `check` names judges it.
3. *While deciding.* Where a kind that every product shares has no best practice yet, put a deliverable that makes one, of the kind `meta`, at the top level before the first deliverable of that kind.

### N4

Does each deliverable name the deliverables it takes content from and those that must pass before it starts, and come after all of them?

A deliverable started before its inputs rests on a guess. A [topological sort](https://en.wikipedia.org/wiki/Topological_sorting) of the deliverables by what each takes from and waits for gives an order that keeps every dependency.

1. *While deciding.* Give each deliverable, in `inputs`, the path of each deliverable it takes content from, and in `preconditions`, the path of each one that must pass before it starts, each of a kind that its best practice names there. Use paths, not kinds, since deliverables of one kind can serve different products.
2. *While deciding.* Have each level of tests pass only once the level below it passes: unit, then architecture, then product vision. A higher level finds a fault later, at a higher cost.
3. *While deciding.* Put a check, and a test that shows the check failing, before the deliverables that trust its results, as [the architecture best practice](../architecture/best-practice.md) trusts a check only then.
4. *While making.* Let a script order the deliverables by these paths, instead of working out the order case by case.
5. *While making.* After each change, have a script, such as rn's `tree.py`, check that each deliverable comes after its inputs and preconditions, that each research deliverable serves a later decision, and that a later deliverable uses each meta deliverable's kind.

### N5

Does each deliverable hold the decisions and the open points for each necessary condition of its best practice?

The maker builds a deliverable from the decisions that answer its best practice's conditions, and asks about the points still open instead of guessing. The [last responsible moment](https://blog.codinghorror.com/the-last-responsible-moment/) of Mary and Tom Poppendieck's *Lean Software Development* settles a decision once its inputs exist, and no earlier, so that it rests on no guess.

1. *While deciding.* Give each deliverable the necessary conditions of its best practice, in that best practice's order, each with its decisions, and a `specific` one the check that judges it, with its decisions.
2. *While deciding.* Leave a point's `decided` null while it's open.
3. *While deciding.* Settle each decision once its inputs exist, and no earlier.
4. *While making.* After each result, revise the design tree forward from it.

### N6

Does each decision say who settled it?

The user should spend their time only on the decisions that are theirs, and finds the grounds of each in git.

1. *While deciding.* Name in `by` who settled each decision: the user, the maker, reasoning from the goal and the best practices, or research.
2. *While making.* Keep the grounds out of the tree, and write them in the commit message that makes the decision, so that the user finds them in git.

### N7

Does each deliverable's name say what it brings toward the goal?

The user reads the design tree to see where the work stands and what comes next, without opening each deliverable. Each name is a goal, as in the goal models of Knowledge Acquisition in Automated Specification (KAOS) that Axel van Lamsweerde's [guided tour](https://doi.org/10.1109/ISRE.2001.948567) describes: a state that holds once the deliverable exists.

1. *While making.* For each deliverable, ask what holds toward the goal once it exists, and write that as its name.
2. *While making.* Leave out its path and its kind, which have fields of their own.

### N8

Does each deliverable show its status and which necessary conditions it meets?

Whoever picks up the work must go on from where it stopped, without reading back through what came before. David J. Anderson's *Kanban* makes the work visible by showing each item in the state it's in.

1. *While making.* Keep each deliverable's status: `open`, `doing`, or `done`.
2. *While making.* Keep, for each necessary condition, whether the deliverable meets it, in `good`, and for a `specific` deliverable, whether it passes its check.

### N9

After a change to a node, does every node that the change touches agree with it?

A node that a change touches, left unread, goes on saying what held before. Change impact analysis, as Shawn Bohner and Robert Arnold's *Software Change Impact Analysis* describes it, follows the dependencies of a changed item to each item that the change touches.

1. *While making.* After each change to a node, go through the nodes that a script, such as rn's `tree.py`, lists: up to the goal, then the later decisions of the deliverable, then the deliverables before and after it that it takes from or gives to.
2. *While making.* Answer each as holding or as changed.
3. *While making.* Start the list again after each change.

### N10

Does the tree hold only what holds now?

A reader acts on what the design tree says, and reads any history in it as part of the current decision, while git keeps how each point came about. The method is Robert C. Martin's rule against journal comments and commented-out code, in *Clean Code*: the source keeps only what holds now, since version control remembers the rest.

1. *While making.* Keep one line for a deliverable that's done: its name, path, kind, and status.
2. *While making.* Drop a research deliverable once the decisions hold what it found.
