# `product-vision`

## Goal

The developers build a product with which its users achieve their goals.

## Template

[template.md](template.md)

## Example

[example.md](example.md), a copy of [../../../../../dev/rn/product-vision.md](../../../../../dev/rn/product-vision.md)

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The developers know whom the product serves and what each of them is trying to achieve. |
| C2 | The developers can tell whether a change brings the users closer to their goals. |
| C3 | The developers know the one way by which the product brings its users to their goals, so that every choice leans toward it. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | Does Roles list every kind of person who comes to the product with a goal of their own? | Roles |
| N2 | C1 | Does each objective state, in one sentence, what one role is trying to achieve in their own work? | Objectives and key results |
| N3 | C1 | Does the vision describe only what the users do and get, not how the product works inside? | the whole |
| N4 | C2 | Does each objective have key results that measure how well and how fast its role achieves it, each with the direction that's better? | Objectives and key results |
| N5 | C2 | Are the objectives distinct, so that each piece of work serves one of them? | Objectives and key results |
| N6 | C3 | Does the concept state first the one way, as its maker means it, by which the product brings the users to their objectives, and then the few ideas that this way needs? | Concept |

## Practices

### N1

Does Roles list every kind of person who comes to the product with a goal of their own?

**Thinking**

The developers build for the people Roles lists, so a missing role goes unserved, and two roles merged into one get a product that fits neither. Define each role by the job it hires the product to do, as in Clayton Christensen's theory of the jobs that customers hire a product for, not by a job title. Start from the job that the product exists to do, and name who hires it for that job. Then ask whether that job gets done only if the product also does a job for someone else, such as setting it up on a shared server. Each such person is a role as well. Split a role whose members hire the product for different jobs. Name the role `user` where there's only one. Check that each role has a job that no other role has.

**Steps**

1. Ask the user about each person whose job you can't tell from what the product does.

### N2

Does each objective state, in one sentence, what one role is trying to achieve in their own work?

**Thinking**

The developers build toward the objectives, so each must name the end that a role reaches. A feature or a measure of that end isn't an objective. An objective in John Doerr's Measure What Matters is a qualitative goal that a key result then measures. For each role, write its job as the end they reach in their own work, in one sentence with the role as the subject. Ask why that end matters to them until the answer is their own goal and no longer the product's. Write one objective for each distinct end. Check that the objective still makes sense with the product's name taken out.

### N3

Does the vision describe only what the users do and get, not how the product works inside?

**Thinking**

The vision must stay true while the inside of the product changes, so it describes only the problem space: what users do and get. How the product does it belongs to the solution space, in the architecture. For each sentence, ask whether it would change if the product's internals changed while users saw the same. If it would, move it to the architecture.

### N4

Does each objective have key results that measure how well and how fast its role achieves it, each with the direction that's better?

**Thinking**

The developers keep a change only if it brings the users closer to their goals, so each objective needs measures that show that after a change. The International Organization for Standardization (ISO) standard 9241-11 defines usability by effectiveness and efficiency, among other measures, and these give the two key results. The first measures how well: the share of attempts in which the role reaches the objective, or its complement, such as the share of deliverables the users can't use. The second measures how fast: the time or effort the role spends to reach it. Give each the direction that's better. Rank them: keep a change that improves one only if none ranked before it gets worse, with how well before how fast. Give no targets, since a measure made a target stops being a good measure, as Goodhart's law says. Check that a developer can measure both after a change and decide from them whether to keep it.

### N5

Are the objectives distinct, so that each piece of work serves one of them?

**Thinking**

The developers decide what to build by asking which objective a piece of work serves, which works only if the objectives don't overlap. For each pair of objectives, ask whether a piece of work could serve one without the other. If not, merge them. Then take the work the product plans, and name the objective each piece serves. A piece that serves none is either not needed or shows a missing objective. Ask the user which.

### N6

Does the concept state first the one way, as its maker means it, by which the product brings the users to their objectives, and then the few ideas that this way needs?

**Thinking**

The developers make many choices that no line of the vision names, and the concept lets each of them lean the same way. Fred Brooks, in The Mythical Man-Month, calls this conceptual integrity: one set of design ideas that every part follows. The one way comes from whoever conceived the product, because an analysis of what goes wrong today yields only a list of fixes with no center. Decide in order. First, get from the user how the product brings its users to their objectives. Write it in one sentence as what the users see the product do. Second, for each thing that this way needs to work, write an idea, and what it gives the role toward the objective. An idea that the way doesn't need goes. Check by taking a design choice that no line names, and deciding it by the one way.

**Steps**

1. Ask the user how the product brings its users to their objectives, before you write the concept.
