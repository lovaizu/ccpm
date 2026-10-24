---
name: ux
version: 1
made_from:
  checklist: 1
  usability: 1
---

# UX

A UX is read by the user who agrees it, before anything else of the product is made, and by
whoever builds the product, its README and its architecture from it. From it they know whom the
product is for, the experience it must give them and how each version is judged against it, and
agree it or build to it.

A UX holds a user's experience of using the product until they achieve their goal, each part resting
on the one before: the users and the goal each wants; the key results, what is measured to show how
close the product brings them to it, in order of priority; the scenes of what the user does and gets
back until they reach it; and the benefits, what they gain with this product, which are why they
choose it. It holds only what the user deals with; what the product does inside is the
architecture's. Most of what a product gives, such as a document's worth or the time it takes, is
not met or missed but come close to, so each version is judged against the version in use on the
same tasks, with no target value: a value the user's need does not rest under draws the work toward
the number rather than the user. A version comes closer from the highest key result, and a lower one
is never brought closer by moving a higher one away.

## Format

### F-1: Shape

Scope: whole

Does the UX follow this template, headings and IDs included?

````markdown
# <Product name> UX

<The main point: what the product gives whom, and that every part of it is built to this UX>

## Users and goals

- G1: <A user, and the goal they want to achieve>

## Key results

<That they stand from the highest priority, and why in that order>

- KR1.1: <What is measured for G1, which way is better, and its value once G1 is reached>

  <Why a better value shows the user closer to G1>

## Scenes

<Who takes part, and the words the figures use>

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

- <What the figure cannot show, such as a rule that holds throughout, and why>

## Benefits

- <What the user gains when they achieve the goal, and why this product gives it>
````

Each list item is one sentence understood alone, its explanation after a blank line and indented
under it, and no item is set in bold.

Why: the reader reads who the users are and what they want, how close the product must bring them,
how they get there, then what they gain, each the ground of the next, and skims the items alone,
reading an explanation only where they need it; the README and the architecture name each goal and
key result by its ID.

## Benefit

### B-1: Whom it is for, and what they want

Scope: its part

From the main point and the users and goals, can the reader tell whom the product is for and the
goal each of them wants to achieve?

Look for: a main point that says what the document is in place of what the product gives; a user
named so loosely the builder cannot tell whether someone is one; a goal said as what the product
does rather than what the user achieves.

Why: everything else in the UX is the experience of these users reaching these goals; without them,
the user cannot tell what they agree to, and the builder cannot tell whom the product is for or when
it has done its work.

### B-2: Each version judged by how close it comes

Scope: its part

From the key results, can the builder tell whether a version brings the users closer to their goals
than the version in use?

Look for:
- no order of priority, or an order given without why;
- a key result with no word on what counts as one, how each case is judged, which way is better or
  how it stands once the goal is reached;
- work done or a thing made in place of a result the user sees, or a measure taken because it is
  easy to count;
- a key result with no reason why a better value shows the user closer to its goal;
- a target value.

Why: a measure taken because it is easy to count, or with no why, moves while the user comes no
closer; without an order, the builder trades the result that matters more for one easier to move;
and a count whose unit is not said is counted differently by each builder, so a version looks
closer while the user is worse off.

### B-3: The way to the goal

Scope: its part

From the scenes, can the reader tell what the user does and gets back, in order, from asking to
achieving the goal?

Look for:
- the whole way, or a scene the user should see, with no sequence diagram of its own;
- a step between two scenes that the whole way does not show;
- a box that holds a description instead of its name, or whose kind is not beside its name as one
  short word in angle brackets, such as `turn:up <agent>`;
- a rule that holds throughout the scenes, which no figure shows, given by no text beside them.

Why: the builder builds what the scenes show the user doing and getting, and the user agrees to
that; a step no scene shows is built by guess, or not at all. A sequence diagram shows at a glance
who acts, in what order, and what repeats or branches, which sentences leave the reader to piece
together; a figure for each scene says one thing, and the whole way keeps the scenes from leaving a
gap between them.

### B-4: Why they choose it

Scope: its part

From the benefits, can the reader tell what the user gains by achieving the goal with this
product?

Look for: a gain said as what the product does or holds rather than what the user gets; a gain with
nothing saying why this product gives it.

Why: the benefits are why the user chooses the product and what its README promises; a builder who
does not know them can build every scene and still give the user nothing worth choosing.

### B-5: Each line used toward the experience

Scope: each part

Does each line give the reader something of the experience they would lose without it?

Look for:
- what the product does inside, out of the user's sight, such as a part the user never deals with;
- a line meant for someone other than the reader, such as a reviewer;
- how the work went, its status or the history of how a decision was reached;
- a comparison or an example for an idea the reader already holds;
- a word that adds nothing to what its sentence says.

Why: what the product does inside is the architecture's, and said here it is decided twice and
drifts; what changes with each piece of work turns the UX wrong while it is still believed; and
every line beyond the experience is read in place of it.

### B-6: Each line taken as meant

Scope: whole

Does the reader take each line as the UX means it, reading it once from the top?

Look for:
- a term, such as a word for someone who acts or a thing they pass, that the reader does not
  already know and the place it is first used does not show, or a name taken from another product;
- one thing under two names, or one name for two things;
- a line that rests on a word, reason or step coming later or elsewhere;
- an idea given in part, leaving the rest to a guess;
- one thing said in two places, in other words or in a figure and its text, or a rule set apart
  from the case where it does not hold;
- two lines that cannot both hold.

Why: a line read another way than meant is agreed or built the other way; the reader completes a
guess where a term or an idea is missing, takes a second name for a second thing, and cannot tell
which of two accounts holds once one of them changes.
