# UX

A UX is read by the user who agrees it before anything else of the product is made, and by whoever
builds the product, its README and its architecture from it. From it they know whom the product is
for, the experience it must give them and how each version is judged against it, and they agree it
or build to it.

A UX holds a user's experience of the product until they achieve their goal, each part resting on
the one before: the users and the goal each wants; the key results, what is measured to show how
close the product brings them to it, in order of priority; the scenes of what the user does and gets
back on the way; and the benefits, what they gain with this product, which are why they choose it.
It holds only what the user deals with, as what the product does inside is the architecture's. The
scenes are the one place that tells who does what in which order; the README and the architecture
point to them and do not tell it again. Most of what a product gives, such as a document's worth or
the time it takes, is not met or missed but come close to. So each version is judged by how close it
brings the user, with no target value: a number the user's need does not set draws the work toward
the number rather than toward the user.

## Format

````markdown
# <Product name> UX

<The main point: what the product gives whom, and that every part of it is built to this UX>

## Users and goals

- G1: <A user, and the goal they want to achieve>

## Key results

- KR1.1: <What is measured for G1, which way is better, and how it stands once G1 is reached>

  <Why a better value shows the user closer to G1>

<That they stand from the highest priority, and why in that order>

## Scenes

<Who takes part, each with its kind, such as a person or a plugin, and the words the figures use>

### <The whole way>

```mermaid
sequenceDiagram
  <Who acts, in the order they act, from asking to the goal>
```

### <A scene the user should see>

```mermaid
sequenceDiagram
  <Who acts in this scene, in the order they act>
```

- <What the figures cannot show, such as a rule that holds throughout, and why>

## Benefits

- <What the user gains when they achieve the goal, and why this product gives it>
````

The README and the architecture name each goal and key result by its ID.

## Questions

### Q-1: Whom it is for, and what they want

From the main point and the users and goals, can the reader tell whom the product is for and the
goal each of them wants to achieve?

Why: everything else in the UX is the experience of these users reaching these goals. Without them,
the user cannot tell what they agree to, and the builder cannot tell whom the product is for or when
it has done its work. A goal said as what the product does, rather than what the user achieves, is
met while the user is no better off.

### Q-2: How close a version comes

From the key results, can the builder tell how close a version brings the users to their goals?

Why: a measure taken because it is easy to count, such as work done or things made, moves while the
user comes no closer. A key result says what counts as one, which way is better and why a better
value shows the user closer, or each builder counts it their own way.

### Q-3: Which result comes first

From the key results, can the builder tell which to favor when two of them move apart?

Why: without an order, the builder trades the result that matters more for one easier to move. A
version comes closer from the highest key result, and a lower one is never brought closer by moving
a higher one away.

### Q-4: The way to the goal

From the scenes, can the reader tell what the user does and gets back, in order, from asking to
achieving the goal?

Why: the builder builds what the scenes show the user doing and getting, and the user agrees to
that. A step no scene shows is built by guess, or not at all. The whole way keeps the scenes from
leaving a gap between them.

### Q-5: Why they choose it

From the benefits, can the reader tell what the user gains by achieving the goal with this product?

Why: the benefits are why the user chooses the product and what its README promises. A builder who
does not know them can build every scene and still give the user nothing worth choosing.

### Q-6: Only what the user deals with

Does each line tell of what the user deals with, leaving what the product does inside to the
architecture?

Why: what the product does inside, said here, is decided twice and drifts from the architecture, and
it takes the place of the experience the user agrees to.
