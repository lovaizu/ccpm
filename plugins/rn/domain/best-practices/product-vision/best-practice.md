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
| N6 | C3 | Does the concept state first the one way, as its maker means it, by which the product brings the users to their objectives, and then the ideas that keep this way holding at each moment of their use? | Concept |

## Practices

### N1

Does Roles list every kind of person who comes to the product with a goal of their own?

The developers build for the people Roles lists, so a missing role goes unserved, and two roles merged into one get a product that fits neither. The method is Clayton Christensen's theory of the jobs that customers hire a product for.

1. *While deciding.* Define each role by the job it hires the product to do, not by a job title.
2. *While deciding.* Start from the job that the product exists to do, and name who hires it for that job.
3. *While deciding.* Then ask whether that job gets done only if the product also does a job for someone else, such as setting it up on a shared server. Each such person is a role as well.
4. *While deciding.* Ask the user about each person whose job you can't tell from what the product does.
5. *While deciding.* Split a role whose members hire the product for different jobs. Name the role `user` where there's only one.
6. *While making.* Check that each role has a job that no other role has.

### N2

Does each objective state, in one sentence, what one role is trying to achieve in their own work?

The developers build toward the objectives, so each must name the end that a role reaches. A feature or a measure of that end isn't an objective. An objective in John Doerr's Measure What Matters is a qualitative goal that a key result then measures.

1. *While deciding.* For each role, write its job as the end they reach in their own work, in one sentence with the role as the subject.
2. *While deciding.* Ask why that end matters to them until the answer is their own goal and no longer the product's.
3. *While deciding.* Write one objective for each distinct end.
4. *While making.* Check that the objective still makes sense with the product's name taken out.

### N3

Does the vision describe only what the users do and get, not how the product works inside?

The vision must stay true while the inside of the product changes, so it describes only the problem space: what users do and get. How the product does it belongs to the solution space, in the architecture.

1. *While making.* For each sentence, ask whether it would change if the product's internals changed while users saw the same. If it would, move it to the architecture.

### N4

Does each objective have key results that measure how well and how fast its role achieves it, each with the direction that's better?

The developers keep a change only if it brings the users closer to their goals, so each objective needs measures that show that after a change. The International Organization for Standardization (ISO) standard 9241-11 defines usability by effectiveness and efficiency, among other measures, and these give the two key results.

1. *While deciding.* Make the first key result measure how well: the share of attempts in which the role reaches the objective, or its complement, such as the share of deliverables the users can't use.
2. *While deciding.* Make the second measure how fast: the time or effort the role spends to reach it.
3. *While deciding.* Give each the direction that's better.
4. *While deciding.* Rank them: keep a change that improves one only if none ranked before it gets worse, with how well before how fast.
5. *While deciding.* Give no targets, since a measure made a target stops being a good measure, as Goodhart's law says.
6. *While making.* Check that a developer can measure both after a change and decide from them whether to keep it.

### N5

Are the objectives distinct, so that each piece of work serves one of them?

The developers decide what to build by asking which objective a piece of work serves, which works only if the objectives don't overlap.

1. *While deciding.* For each pair of objectives, ask whether a piece of work could serve one without the other. If not, merge them.
2. *While deciding.* Then take the work the product plans, and name the objective each piece serves.
3. *While deciding.* A piece that serves none is either not needed or shows a missing objective. Ask the user which.

### N6

Does the concept state first the one way, as its maker means it, by which the product brings the users to their objectives, and then the ideas that keep this way holding at each moment of their use?

The developers make many choices that no line of the vision names, and the concept lets each of them lean the same way. Fred Brooks, in The Mythical Man-Month, calls this conceptual integrity: one set of design ideas that every part follows. The one way and the ideas that carry it out come from whoever conceived the product, because an analysis of what goes wrong today yields only a list of fixes with no center.

1. *While deciding.* Ask the user how the product brings its users to their objectives, and by which ideas, before you write the concept.
2. *While deciding.* Write the one way in one sentence as what the users see the product do.
3. *While deciding.* Write each idea the user gave, with what it gives the role toward the objective.
4. *While deciding.* Find where the user's ideas leave the one way unheld. Walk through the users' use from the moment they first meet the product to the moment they reach the objective, and list its moments, as a [customer journey map](https://www.nngroup.com/articles/journey-mapping-101/) does.
5. *While deciding.* At each moment, ask what keeps the one way holding there. Where no idea answers, propose one.
6. *While deciding.* Confirm each idea you propose with the user.
7. *While deciding.* An idea that the way doesn't need goes.
8. *While making.* Check by taking a design choice that no line names, at each of those moments, and deciding it by the one way and its ideas.
