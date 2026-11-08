# `architecture`

## Goal

The developer builds and changes each part of the product so that the parts together give its product vision.

## Template

[template.md](template.md)

## Example

[example.md](example.md), a copy of [../../../../../dev/rn/architecture.md](../../../../../dev/rn/architecture.md)

## Inputs

- [product-vision](../product-vision/best-practice.md)
- [readme](../readme/best-practice.md)

## Intents

| ID | About | Question |
| --- | --- | --- |
| Q1 | the opening | Starting on any part, does the developer see the one idea by which the product gives its product vision, and the piece of it the part carries out, so that every part they build serves that idea? |
| Q2 | User stories | Following a step of an objective's main use, as the README's walkthrough shows it, does the developer find the one user story that carries it, so that each part traces back to what a role does? |
| Q3 | Principles | Meeting a case no line of the document names, do two developers of different parts reach the same decision from a principle's why, so that the parts still fit where the document is silent? |
| Q4 | User stories, Components | Facing a decision the stories need, does the developer find the one component that alone decides it, so that no two components make the same decision and drift apart? |
| Q5 | Components | Starting on a component, does the developer know what kind of thing the component is and what they build it with, so that the components fit without anyone choosing alone? |
| Q6 | Data model | Making one component that writes a data and another that reads it, do two developers join it to the other data the same way, so that the data fits while its fields change freely? |
| Q7 | User stories, Components, Data model, Sequences | Following a user story from its role's first request to its end, does the developer see at each step which component acts, along which arrow, and what data it hands on, so that they build each step knowing who acts and on what? |
| Q8 | User stories, Components, Data model, Sequences | Of any story, component or data, does the developer see which objective of the product vision needs it, so that what none needs can go? |
| Q9 | Components, Data model, Deployment | Setting the product up from nothing, does the developer put each component where it runs and each data where the product keeps it, and start the product, so that they need ask no one? |
| Q10 | Components, Data model, Directory structure | Making or changing a component or a data, does the developer find the one place its files belong, so that each change lands in one place? |
| Q11 | Deployment, Tests | Asked whether anything in the product goes untested, does the developer see for each deployment unit which levels cover it, how far each tries it, and why a level is missing, so that no gap goes unseen? |
| Q12 | Tests | Writing a test at one level, does the developer know what to run real, what doubles stand in for, what to cover and when it passes, so that a failing test names the rule, path, or use it breaks? |
| Q13 | Tests | When the unit and architecture tests pass, does the developer know the product does what this document says, so that the product vision level only confirms the product in real use? |
| Q14 | Components, Sequences, Deployment, Directory structure, Tests | Doubting a choice the document makes, such as a tool or how far a level tries a unit, does the developer see what the other way would lose, so that they keep or change it knowing what it was for? |
| Q15 | the whole | Following a principle while building a part, does the developer find every figure and list asking the same of that part, so that they never choose between the document and itself? |
| Q16 | the whole | Changing how a component works inside while the product vision and the principles stay, does the developer find every line of the document still true, so that the document needs no change for it? |

## Practices

### Q1

Starting on any part, does the developer see the one idea by which the product gives its product vision, and the piece of it the part carries out, so that every part they build serves that idea?

**Thinking**

The opening says, as one idea seen as a whole, how the product turns what its roles bring into what the product vision promises. It points to the product vision and doesn't repeat it. Every part then reads as a piece of that idea.

**Steps**

1. After writing the rest, check that each component carries out a piece of the idea, and change the idea or the component where one doesn't.

### Q2

Following a step of an objective's main use, as the README's walkthrough shows it, does the developer find the one user story that carries it, so that each part traces back to what a role does?

**Thinking**

There is one [user story](https://www.mountaingoatsoftware.com/agile/user-stories) for each way a role meets the product at its edge, drawn from the objectives and the README's walkthrough, each naming what it carries, such as a step of the walkthrough or resuming a run that stopped. Each part then traces to what the role does, and a convenience added is a story added, while the product vision and the README stay unchanged.

**Steps**

1. Go through each exchange of the README's walkthrough, and the main use of each objective it doesn't run, and name the one way at the product's edge that carries each step. Add a story where none does. The trace: `{inputs}` read to its end.

### Q3

Meeting a case no line of the document names, do two developers of different parts reach the same decision from a principle's why, so that the parts still fit where the document is silent?

**Thinking**

Each principle is one rule that every part meeting the same decision follows, with its why: what goes wrong without it. A developer carries the why to a case the rule doesn't name.

**Steps**

1. Point to the principles of the architecture this one builds on, and write only what this product adds or changes.
2. Take a case no rule names, decide it from each why as two developers of different parts would, and sharpen the why where they differ.

### Q4

Facing a decision the stories need, does the developer find the one component that alone decides it, so that no two components make the same decision and drift apart?

**Thinking**

One component alone makes each decision the stories need, most of all one hard to make or likely to change, and a list under the figure says so by the component's name. Two components that share a decision make it twice, and it drifts, as [information hiding](https://doi.org/10.1145/361598.361623) has each module hide one decision likely to change. A box holds only the component's name and type, as a box that holds sentences no longer shows the parts and their joins at a glance.

**Steps**

1. List each decision the stories need by asking at each step of each sequence what a component must decide there, and move the decision or split the component where two components or none make it.
2. Label each arrow with what one does to another and the data it hands on, never a word such as "uses."

### Q5

Starting on a component, does the developer know what kind of thing the component is and what they build it with, so that the components fit without anyone choosing alone?

**Thinking**

Each box has its type and technology, and the figure a legend for every symbol, as the [C4 model](https://c4model.com/diagrams/container) draws a container. A store of data is a box like a component's, as its type, such as a folder of JSON files, sets it apart. A developer otherwise chooses them alone, and the components stop fitting.

**Steps**

1. Read the figure without the text around it, and add to the legend whatever symbol a reader would still have to ask about. What a part does goes to the list under the figure, not into its box.

### Q6

Making one component that writes a data and another that reads it, do two developers join it to the other data the same way, so that the data fits while its fields change freely?

**Thinking**

A concept model in a Unified Modeling Language (UML) class diagram, which most developers read, shows the data. It draws each data once, as a class by its name alone. It names each relation, with how many of each it joins at both ends. Where one data holds the other's parts, it puts a filled diamond at the whole, never a hollow one, which readers take in different ways. Frames group the data, one for each component or part of the product that keeps them, in the order the stories meet them. The data that most others join stands in the middle. The reader then grasps how the data hang together before reading a relation. A list under the figure says what a data is in a few words only where a reader could take its name for another's, such as two data that both start a role. A name the reader already reads right gets no line, as such a line only gives them the figure to read again. The document leaves the fields to where the developer builds the data. Two developers then join a data the same way while its fields change freely.

### Q7

Following a user story from its role's first request to its end, does the developer see at each step which component acts, along which arrow, and what data it hands on, so that they build each step knowing who acts and on what?

**Thinking**

A sequence, such as a [UML](https://www.omg.org/spec/UML) sequence diagram, draws each story as its steps in order, from the role's first request to what the story gives them, each step taken by a component along an arrow of Components and handing on a named data. The sequence draws each branch, each step that sends work back, and each question put to the role, as each path of the story, and its test, rests on them.

**Steps**

1. Check that each step runs along an arrow of Components, and add the arrow or give the step to another component where none does.

### Q8

Of any story, component or data, does the developer see which objective of the product vision needs it, so that what none needs can go?

**Thinking**

The document keeps only the stories, components, and data that an objective needs. Each can then go once no objective needs it.

**Steps**

1. Trace each component and each data to the stories whose sequences reach it, and each story to the objective whose use or intent it carries, and remove what reaches none.

### Q9

Setting the product up from nothing, does the developer put each component where it runs and each data where the product keeps it, and start the product, so that they need ask no one?

**Thinking**

Each component and each data sits in one deployment unit, within the environment where it runs or where the product keeps it, with each thing outside the product it depends on, and no infrastructure the components don't need. The developer then knows what each can reach and how the product starts, as a [C4 deployment diagram](https://c4model.com/diagrams/deployment) shows.

### Q10

Making or changing a component or a data, does the developer find the one place its files belong, so that each change lands in one place?

**Thinking**

The directory structure shows the folders and files that hold each component and each data as they lie on disk, one line each, leaving out what lies inside a component. The developer then finds the one place to change it.

### Q11

Asked whether anything in the product goes untested, does the developer see for each deployment unit which levels cover it, how far each tries it, and why a level is missing, so that no gap goes unseen?

**Thinking**

Each deployment unit has a cell at each level whose ground, a part's contract, this document or the product vision, says what the unit must do, and an empty cell says why. Each level takes its name from what it checks against, not from its means. Unit and architecture carry most of the checking and run on every change. Product vision tests are few, as the [test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) has it.

**Steps**

1. Leave out a unit whose every cell would be empty, and say why under the table.
2. Check that each story's sequence runs from start to end at the architecture level in some row.

### Q12

Writing a test at one level, does the developer know what to run real, what doubles stand in for, what to cover and when it passes, so that a failing test names the rule, path, or use it breaks?

**Thinking**

The developer draws each test from the one thing its level checks against: the ways a part's contract divides at unit, the paths the sequences draw at architecture, and an objective's main use at real size at product vision. It runs only that real and stands [test doubles](https://martinfowler.com/bliki/TestDouble.html) in for the rest. A failing test then names the rule, path, or use it breaks.

**Steps**

1. Point to the project's shared test rules, and write only where this product differs from them.
2. At unit, divide each input and each result the contract names into classes the part treats alike, the refused ones among them, and write one test for each class, by equivalence partitioning as the [glossary](https://glossary.istqb.org) of the International Software Testing Qualifications Board defines it.
3. Where a class ends on an ordered scale, such as a length or a count, write one test at each end and one at the nearest value of the next class, by boundary value analysis.
4. Where the contract's result turns on a combination of conditions, write one test for each combination that can occur, with the result it gives, by decision table testing.
5. At unit, pass when every test passes, every line and branch runs, and the tests catch every mutant. Add a unit test for each gap that coverage, mutation testing, or a property-based test finds, as these tools confirm the tests drawn from the contract and draw none themselves.
6. At unit, where no guard holds each rule of a part an AI does on every run, run the part on the real model, with one input for each class, both where the contract says the part acts and where it says it doesn't, and doubles for the parts it works with.
7. At architecture, run real what joins the components, such as hooks and scripts, and stand a double in for each component an AI runs and each thing outside the product, so the level calls no model and gives the same result each run.
8. At architecture, write one test for each path through each story's sequence, the main flow, each branch, each step that sends work back and each question put to the role, until every move from one step to the next lies on some path.
9. Run the unit and architecture tests that a change reaches before each push, and every test in CI, as running every test before each push makes each change wait, and a selection misses a test that reads a file the change edits.
10. At product vision, once unit and architecture pass, run the real product on each objective's main use, as the README's walkthrough shows it, at the size of a real request, with an AI standing in for the role that holds an intent the product never gets.
11. At product vision, measure each key result as the product vision words it, and set each measure against the last one by the direction the product vision gives it, as the product vision gives no target.
12. At product vision, run each role on the model its users run and judge each run from its records, and try no case a lower level can test, as another model makes other slips than the users meet, and each run is slow and costly.
13. For a test whose result varies from run to run, write how many runs of how many must meet the expectation.

### Q13

When the unit and architecture tests pass, does the developer know the product does what this document says, so that the product vision level only confirms the product in real use?

**Thinking**

Each double gives only results in the form the part's contract gives them, the refusals among them, and its own tests check it as the part's unit tests check the part. Unit and architecture together then show that every path holds for the real parts.

**Steps**

1. Draw a double of something outside the product from its documentation or from a recorded run of the real thing, as a double that gives what the real thing never would passes a test that the real one fails.
2. For a fault a higher level finds, name the case or path the lower level missed, add its test at the level that must catch it, see it fail, then fix it there.
3. Trust a check, such as a test, a hook or the judge of a trial, only once you have seen it fail on a case that breaks what it checks. Trust a judge once it's right on kept records whose answer you know. A check that can't fail lets everything through unseen.

### Q14

Doubting a choice the document makes, such as a tool or how far a level tries a unit, does the developer see what the other way would lose, so that they keep or change it knowing what it was for?

**Thinking**

Beside each choice a developer would question, such as a technology, a tool or how far a level tries a unit, stands why it beat the other way and what it costs, as an [architecture decision record](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) keeps its context and consequences. The developer then keeps or changes it knowing what it was for.

**Steps**

1. Read each figure as a developer new to the product, and give a why and a cost to each choice they would question.

### Q15

Following a principle while building a part, does the developer find every figure and list asking the same of that part, so that they never choose between the document and itself?

**Thinking**

Each principle and every part it rules say the same. A developer who meets a figure breaking a principle must choose which to follow.

### Q16

Changing how a component works inside while the product vision and the principles stay, does the developer find every line of the document still true, so that the document needs no change for it?

**Thinking**

The document holds only what stays while the product vision and the principles stay. The document leaves how a component works inside to where the developer builds it, as a line about the inside goes untrue at the next change, which [information hiding](https://doi.org/10.1145/361598.361623) keeps inside the module.

**Steps**

1. Imagine a change to how a component works inside, such as its steps, a value it uses or a data's fields, mark each line it would make untrue, and repeat with a change of another kind until you mark no line.
