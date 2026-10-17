---
name: ux
version: 0.1.0
---

# UX

A UX is read by whoever builds the product. From it they know the experience the product must give
its users and how close each version must come to it, and build the product to it.

The UX is a user's experience of using the product until they achieve their goal. Working out the
UX is making that experience clear, in this order:

1. Decide the users and the goal each wants to achieve.
2. Decide, for each goal, its key results: what is measured to show how close the product brings
   the user to it, each with a target set high.
3. Draw, as scenes, what the user does and gets back until they achieve the goal.
4. Decide what the user gains when they achieve the goal with this product: the benefits, which are
   why the user chooses it.

Each item of `readability.md` applies to a UX with the users' experience as its subject; its B-16 is
answered by the scenes.

## Format

### F-1: Shape

Does the UX follow this template, headings and IDs included?

```markdown
# <Product name> UX

<The main point>

## Users and goals

- G1: <A user, and the goal they want to achieve>

## Key results

- KR1.1: <What is measured for G1, and its target>

  <Why reaching it shows G1 achieved>

## Scenes

- <A scene: what the user does, and what they get back>

## Benefits

- <What the user gains when they achieve the goal>
```

Why: the builder reads who the users are and what they want, how close the product must bring
them, how they get there, then what they gain, each the ground of the next; the design names each
goal and key result by its ID.

## Benefit

### B-1: The users and their goals

Can the reader tell the users and the goal each wants to achieve?

Why: everything else in the UX is the experience of these users reaching these goals; without them,
the builder cannot tell whom the product is for or when it has done its work.

### B-2: Results measured

Can the reader tell, for each goal, what is measured to show how close the product brings the user
to it?

Look for: work done or a thing made in place of a result the user sees.

Why: what a document or a non-functional part gives is a matter of degree, so each version is judged
by how close it came; a count of work done grows while the user gains nothing.

### B-3: Targets set high

Is each key result's target one the product is not sure to reach?

Why: a target within easy reach is met and leaves nothing to aim at, so the versions after it stop
coming closer.

### B-4: Why each key result

Can the reader tell, for each key result, why reaching it shows its goal achieved?

Why: a result without its why can be reached while the goal is not, and no one can tell whether it
is the right one to measure.

### B-5: The scenes to the goal

Can the reader tell, as scenes, what the user does and gets back until they achieve the goal?

Why: the builder builds what the scenes show the user doing and getting; a step no scene shows is
built by guess, or not at all.

### B-6: The benefits

Can the reader tell what the user gains when they achieve the goal with this product?

Why: the benefits are why the user chooses the product; a builder who does not know them can build
every scene and still give the user nothing worth choosing.
