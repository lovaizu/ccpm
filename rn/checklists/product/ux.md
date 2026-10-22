---
name: ux
version: 0.2.0
---

# UX

A UX is read by whoever builds the product. From it they know the experience the product must give
its users and how each version is judged against it, and build the product to it.

The UX is a user's experience of using the product until they achieve their goal. A goal says what
the user wants to achieve, and its key results say what is measured to show how close the product
brings them to it. Most of what a product gives, such as a document's worth or the time it takes,
is not met or missed but come close to, so each version is judged against the version in use on the
same tasks, with no target value: a value the user's need does not rest under draws the work toward
the number rather than the user. The key results stand in order of priority: a version comes closer
from the highest, and a lower one is never brought closer by moving a higher one away. Working out
the UX is making that experience clear, in this order:

1. Decide the users and the goal each wants to achieve.
2. Decide, for each goal, its key results, each drawn from the goal: what is counted, how each case
   is judged to count, and how the value stands once the user has reached the goal; then put them in
   order of priority.
3. Draw, as scenes, what the user does and gets back until they achieve the goal: a sequence
   diagram of who acts in turn, with what it cannot show beside it.
4. Decide what the user gains when they achieve the goal with this product: the benefits, which are
   why the user chooses it.

Each item of `usability.md` applies to a UX with the users' experience as its subject; its B-16 is
answered by the scenes.

## Format

### F-1: Shape

Scope: whole

Does the UX follow this template, headings and IDs included?

```markdown
# <Product name> UX

<The main point>

## Users and goals

- G1: <A user, and the goal they want to achieve>

## Key results

<That they stand from the highest priority, and why in that order>

- KR1.1: <What is measured for G1, and which way is better>

  <Why a better value shows the user closer to G1>

## Scenes

<What the figure shows, and the words it uses>

```mermaid
sequenceDiagram
  <Who acts, in the order they act, from asking to the goal>
```

- <What the figure cannot show, such as a rule that holds throughout, and why>

## Benefits

- <What the user gains when they achieve the goal>
```

Why: the builder reads who the users are and what they want, how close the product must bring
them, how they get there, then what they gain, each the ground of the next; the design names each
goal and key result by its ID.

## Benefit

### B-1: The users and their goals

Scope: its part

Can the reader tell the users and the goal each wants to achieve?

Why: everything else in the UX is the experience of these users reaching these goals; without them,
the builder cannot tell whom the product is for or when it has done its work.

### B-2: Results drawn from the goal

Scope: its part

Can the reader tell, for each key result, what is counted, how each case is judged, and how the
value stands once the user has reached the goal, each drawn from the goal?

Look for: work done or a thing made in place of a result the user sees.

Why: a measure taken because it is easy to count, or counted by rule rather than by the goal, moves
while the user comes no closer.

### B-4: Why each key result

Scope: its part

Can the reader tell, for each key result, why a better value shows the user closer to its goal?

Why: a result without its why can grow better while the goal comes no closer, and no one can tell whether it
is the right one to measure.

### B-7: The order of priority

Scope: its part

Can the reader tell which key result comes first, and why in that order?

Why: bringing one key result closer often moves another away; without an order, the builder trades
the one that matters more for one easier to move, and a version looks closer while the user is
worse off.

### B-5: The scenes to the goal

Scope: its part

Can the reader tell, from a sequence diagram of who acts in turn, what the user does and gets back
until they achieve the goal, with what the figure cannot show written beside it, and with no part of
the product shown that the user does not deal with?

Why: the builder builds what the scenes show the user doing and getting; a step no scene shows is
built by guess, or not at all. A sequence diagram shows at a glance who acts, in what order, and
what repeats or branches, which a list of scenes leaves the reader to put together. What the
product does inside, out of the user's sight, is the design's; shown in the scenes, it is decided
twice and drifts.

### B-6: The benefits

Scope: its part

Can the reader tell what the user gains when they achieve the goal with this product?

Why: the benefits are why the user chooses the product; a builder who does not know them can build
every scene and still give the user nothing worth choosing.
