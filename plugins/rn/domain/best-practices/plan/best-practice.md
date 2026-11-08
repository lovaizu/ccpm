# `plan`

## Goal

The user reaches their goal through the deliverables of the plan, none missing, none started before what it needs, and the plan revised after each turn.

## Template

[design-tree.schema.json](design-tree.schema.json)

## Example

[example.json](example.json), a copy of [../../../../../.rn/20261107-rn/design-tree.json](../../../../../.rn/20261107-rn/design-tree.json)

## Intents

| ID | About | Question |
| --- | --- | --- |
| Q1 | goal | Reading the goal, does the maker see the one end the user is after, so that every deliverable of the plan serves that end? |
| Q2 | deliverables | Working back from the goal, does the maker find every deliverable the goal needs, so that none is missing when the work reaches it? |
| Q3 | deliverables | Taking up a deliverable, does the maker find the best practice of its kind, or a meta deliverable that makes one before it, so that each deliverable meets the intents of a best practice? |
| Q4 | deliverables | Reading a deliverable's name in the plan, does the user see what it brings toward the goal, so that they know where the work stands and what comes next without opening it? |
| Q5 | deliverables | Ordering the deliverables, does the maker find what each one takes from its inputs and preconditions, so that none starts before what it needs? |
| Q6 | deliverables | Making a deliverable, does the maker find each intent of its best practice with the decisions that answer it and the points still open, so that it makes the deliverable from the settled decisions and asks about the rest? |
| Q7 | deliverables | Reading a decision, does the user see who settled it, so that they're asked only what's theirs? |
| Q8 | deliverables | Picking up the work, does the maker see where each deliverable stands and which intents it meets, so that it goes on from where the work stopped? |
| Q9 | goal, deliverables | Changing a node of the tree, does the maker find each node the change touches, so that no node goes on saying what held before? |
| Q10 | goal, deliverables | Reading the plan, does the user find only what holds now, so that they act on the current decisions and not on how someone reached them? |
| Q11 | the whole | Following the plan through the work, does the user reach their goal, every deliverable made, none started before what it needs, and the plan revised after each turn? |

## Practices

### Q1

Reading the goal, does the maker see the one end the user is after, so that every deliverable of the plan serves that end?

**Thinking**

Write the end the user is after as one sentence, with the user as its subject, and name in by who settled it. Each deliverable then answers to that end, and one that serves none drops out.

### Q2

Working back from the goal, does the maker find every deliverable the goal needs, so that none is missing when the work reaches it?

**Thinking**

Lay out the deliverables up front, back from the goal, as a [work breakdown structure](https://en.wikipedia.org/wiki/Work_breakdown_structure) does: the deliverables that make the goal, then for each the deliverables it takes, until one takes nothing. A deliverable left out shows only when the work reaches it, and the work stops there. Size each deliverable so that one maker makes it whole and one reader reads it whole, as a work package, the lowest level of a work breakdown structure, is the size one owner delivers. A maker that can't hold the whole drops parts of it, and a reader that can't read it whole can't judge whether it meets its intents.

**Steps**

1. Put in a research deliverable before the decisions it serves, where a decision needs what no one has found yet, at the top level in the order of the work.
2. Where a work is larger than one maker makes whole, split it into a deliverable for each part its architecture names, each after the parts it takes from, and put a deliverable of the whole after them, such as the README of a product after the code of its parts. The architecture already says where the parts meet, so each part stands alone, and the deliverable of the whole holds what only the parts together show.

### Q3

Taking up a deliverable, does the maker find the best practice of its kind, or a meta deliverable that makes one before it, so that each deliverable meets the intents of a best practice?

**Thinking**

Give each deliverable the kind whose best practice it meets, by the name of that best practice's folder. The maker then makes it to that best practice's intents. Where a kind has no best practice yet, put a meta deliverable for it at the top level before the first deliverable of the kind, as a deliverable made with no best practice meets no stated intent.

### Q4

Reading a deliverable's name in the plan, does the user see what it brings toward the goal, so that they know where the work stands and what comes next without opening it?

**Thinking**

Write the one thing that holds toward the goal once the deliverable exists. Leave out its path and kind, which have fields of their own.

### Q5

Ordering the deliverables, does the maker find what each one takes from its inputs and preconditions, so that none starts before what it needs?

**Thinking**

Have a script order the deliverables from each one's inputs and preconditions, never by thinking the order out case by case, as a [topological sort](https://en.wikipedia.org/wiki/Topological_sorting) gives one order that keeps every dependency. Give each deliverable in inputs the path of each deliverable it takes its content from, and in preconditions the path of each that must pass before it starts, each of a kind its best practice names there. One kind's deliverables serve different products, so the paths, not the kinds, say which deliverable comes first.

**Steps**

1. After each change, have a script, such as rn's tree.py, check that the tree holds every deliverable needed, that each comes after its inputs and preconditions, that each research deliverable serves a later decision, and that a later deliverable uses each meta deliverable's kind.
2. Order the tests by level, unit, then architecture, then the product vision, each after the level below passes, as a higher level finds a fault later and at a higher cost.
3. Put a check before the deliverables that trust its results, and trust it only once someone has seen a test of it fail, or, for a judge, once it's right on examples whose answer someone knows.

### Q6

Making a deliverable, does the maker find each intent of its best practice with the decisions that answer it and the points still open, so that it makes the deliverable from the settled decisions and asks about the rest?

**Thinking**

Give each deliverable the intents of its best practice in that best practice's order, each with the decisions that answer it. Leave a point's decided null while it's open, so the maker asks about it instead of guessing. Settle each decision once its inputs exist, and revise the plan forward from each turn's result, as a decision settled before its inputs rests on a guess, which the [last responsible moment](https://blog.codinghorror.com/the-last-responsible-moment/) avoids.

### Q7

Reading a decision, does the user see who settled it, so that they're asked only what's theirs?

**Thinking**

Name in by who settled each decision: the user, the maker, reasoning from the goal and the best practices, or research. Keep no grounds in the tree, as the reason for a decision goes in the commit message that makes it. The user then weighs only the decisions that are theirs, and finds the grounds of the rest in git.

### Q8

Picking up the work, does the maker see where each deliverable stands and which intents it meets, so that it goes on from where the work stopped?

**Thinking**

Keep each deliverable's status, open, doing, or done, and each intent's good, true once the deliverable meets it. Whoever picks up the work goes on from the first deliverable not done, without reading back through what came before.

### Q9

Changing a node of the tree, does the maker find each node the change touches, so that no node goes on saying what held before?

**Thinking**

After each change to a node, go through the nodes that a script, such as rn's tree.py, lists: up to the goal, then the later decisions of the deliverable, then the deliverables before and after it that it takes from or gives to. Answer each as holding or as changed, as a checker such as Lane's every_item asks, and start the list again after each change. A node left unread goes on saying what held before.

### Q10

Reading the plan, does the user find only what holds now, so that they act on the current decisions and not on how someone reached them?

**Thinking**

Keep only what holds now. A deliverable done keeps one line, its name, path, kind, and status, and a research deliverable goes once the decisions hold what it found. Git keeps how each point came about, and a history in the tree reads as part of the current decision.

### Q11

Following the plan through the work, does the user reach their goal, every deliverable made, none started before what it needs, and the plan revised after each turn?

**Thinking**

Read this best practice whole as [Q10 of the meta best practice](../meta/best-practice.md#q10) says. Once the product vision trial shows plans made by it closer to the goal, ship it, and mend each shortfall met in use where it lies: in the goal, the template, a question, or a practice.
