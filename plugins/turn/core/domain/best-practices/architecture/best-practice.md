# architecture

## Goal

The developer builds and changes each part of the product so that the parts together give its product vision.

## Template

[template.md](template.md)

## Example

[example.md](example.md), a copy of [../../../../../../dev/turn/architecture.md](../../../../../../dev/turn/architecture.md)

## Intents

- **Q1** (the opening): Starting on any part, does the developer see the one idea by which the product gives its product vision, and the piece of it the part carries out, so that every part they build serves that idea?
- **Q2** (User stories): Following a step of an objective's main use, as the README's walkthrough shows it, does the developer find the one user story that carries it, so that each part traces back to what a role does?
- **Q3** (Principles): Meeting a case no line of the document names, do two developers of different parts reach the same decision from a principle's why, so that the parts still fit where the document is silent?
- **Q4** (User stories, Components): Facing a decision the stories need, does the developer find the one component that alone decides it, so that no decision is made twice and drifts?
- **Q5** (Components): Starting on a component, does the developer know what kind of thing it is and what it is made with, so that the components fit without anyone choosing alone?
- **Q6** (Data model): Making one component that writes a data and another that reads it, do two developers join it to the other data the same way, so that the data fits while its fields change freely?
- **Q7** (User stories, Components, Data model, Sequences): Following a user story from its role's first request to its end, does the developer see at each step which component acts, along which arrow, and what data it hands on, so that they build each step knowing who acts and on what?
- **Q8** (User stories, Components, Data model, Sequences): Of any story, component or data, does the developer see which objective of the product vision needs it, so that what none needs can go?
- **Q9** (Components, Data model, Deployment): Setting the product up from nothing, does the developer put each component where it runs and each data where it is kept, and start the product, so that they need ask no one?
- **Q10** (Components, Data model, Directory structure): Making or changing a component or a data, does the developer find the one place its files belong, so that each change lands in one place?
- **Q11** (Deployment, Tests): Asked whether anything in the product goes untested, does the developer see for each deployment unit which levels cover it, how heavily, and why a level is missing, so that no gap is left unseen?
- **Q12** (Tests): Writing a test at one level, does the developer know what to run real, what doubles stand in for, what to cover and when it passes, so that a failing test names the rule, path or use it breaks?
- **Q13** (Tests): When the unit and architecture tests pass, does the developer know the product does what this document says, so that the ux level is left only the product vision to confirm?
- **Q14** (Components, Sequences, Deployment, Directory structure, Tests): Doubting a choice the document makes, such as a tool or a test's weight, does the developer see what would be lost by the other way, so that they keep or change it knowing what it was for?
- **Q15** (the whole): Following a principle while building a part, does the developer find every figure and list asking the same of that part, so that they never choose between the document and itself?
- **Q16** (the whole): Changing how a component works inside while the product vision and the principles stay, does the developer find every line of the document still true, so that the document needs no change for it?

## Practices

### Q1: Starting on any part, does the developer see the one idea by which the product gives its product vision, and the piece of it the part carries out, so that every part they build serves that idea?

**Thinking**: The opening says, as one idea seen from above, how the product turns what its roles bring into what the product vision promises. It points to the product vision and does not repeat it. Every part then reads as a piece of that idea.

**Steps**

1. Once the rest is written, check that each component carries out a piece of the idea, and change the idea or the component where one does not.

### Q2: Following a step of an objective's main use, as the README's walkthrough shows it, does the developer find the one user story that carries it, so that each part traces back to what a role does?

**Thinking**: There is one story for each way a role meets the product at its edge, drawn from the objectives and the README's walkthrough, each naming what it carries, such as a step of the walkthrough or resuming a run that stopped. Each part then traces to what the role does, and a convenience added is a story added, while the product vision and the README stay as they are.

**Steps**

1. Go through each exchange of the README's walkthrough, and the main use of each objective it does not run, and name the one way at the product's edge that carries each step; add a story where none does.

### Q3: Meeting a case no line of the document names, do two developers of different parts reach the same decision from a principle's why, so that the parts still fit where the document is silent?

**Thinking**: Each principle is one rule that every part meeting the same decision follows, with its why: what goes wrong without it. A developer carries the why to a case the rule does not name.

**Steps**

1. Point to the principles of the architecture this one builds on, and write only what this product adds or changes.
2. Take a case no rule names, decide it from each why as two developers of different parts would, and sharpen the why where they differ.

### Q4: Facing a decision the stories need, does the developer find the one component that alone decides it, so that no decision is made twice and drifts?

**Thinking**: One component alone makes each decision the stories need, above all one hard to make or likely to change, and a list under the figure says so by the component's name. A decision two components share is made twice and drifts. A box holds only the component's name and type, as a box that holds sentences no longer shows the parts and their joins at a glance.

**Steps**

1. List each decision the stories need by asking at each step of each sequence what must be decided there, and move the decision or split the component where two components or none make it.
2. Label each arrow with what one does to another and the data it hands on, never a word such as "uses".

### Q5: Starting on a component, does the developer know what kind of thing it is and what it is made with, so that the components fit without anyone choosing alone?

**Thinking**: Each box has its type and technology, and the figure a legend for every symbol. A developer otherwise chooses them alone, and the components stop fitting.

**Steps**

1. Read the figure without the text around it, and add to the legend whatever symbol a reader would still have to ask about; what a part does goes to the list under the figure, not into its box.

### Q6: Making one component that writes a data and another that reads it, do two developers join it to the other data the same way, so that the data fits while its fields change freely?

**Thinking**: The data are drawn as a concept model in a UML class diagram, which most developers read: each data once, as a class by its name alone, each relation named with how many of each it joins at both ends, and a filled diamond at the whole where one data holds the other's parts, never a hollow one, which readers take in different ways. A list under the figure says what each data is in a few words. The fields are left to where the data is built. Two developers then join a data the same way while its fields change freely.

### Q7: Following a user story from its role's first request to its end, does the developer see at each step which component acts, along which arrow, and what data it hands on, so that they build each step knowing who acts and on what?

**Thinking**: Each story is drawn as its steps in order, from the role's first request to what the story gives them, each step taken by a component along an arrow of Components and handing on a named data. Each branch, each step that sends work back and each question put to the role is drawn, as each path of the story, and its test, rests on them.

**Steps**

1. Check that each step runs along an arrow of Components, and add the arrow or give the step to another component where none does.

### Q8: Of any story, component or data, does the developer see which objective of the product vision needs it, so that what none needs can go?

**Thinking**: The document keeps only the stories, components and data that an objective needs. Each can then go once no objective needs it.

**Steps**

1. Trace each component and each data to the stories whose sequences reach it, and each story to the objective whose use or intent it carries, and remove what reaches none.

### Q9: Setting the product up from nothing, does the developer put each component where it runs and each data where it is kept, and start the product, so that they need ask no one?

**Thinking**: Each component and each data sits in one deployment unit, within the environment where it runs or is kept, with each thing outside the product it depends on, and no infrastructure the components do not need. The developer then knows what each can reach and how the product starts.

### Q10: Making or changing a component or a data, does the developer find the one place its files belong, so that each change lands in one place?

**Thinking**: The folders and files that hold each component and each data are drawn as they lie on disk, one line each, leaving out what lies inside a component. The developer then finds the one place to change it.

### Q11: Asked whether anything in the product goes untested, does the developer see for each deployment unit which levels cover it, how heavily, and why a level is missing, so that no gap is left unseen?

**Thinking**: Each deployment unit has a cell at each level whose ground, a part's contract, this document or the product vision, says what the unit must do, and an empty cell says why. A level is named by what it checks against, not by its means. Unit and architecture carry most of the checking and run on every change; ux tests are few.

**Steps**

1. Leave out a unit whose every cell would be empty, and say why under the table.
2. Check that each story's sequence runs from start to end at the architecture level in some row.

### Q12: Writing a test at one level, does the developer know what to run real, what doubles stand in for, what to cover and when it passes, so that a failing test names the rule, path or use it breaks?

**Thinking**: Each test is drawn from the one thing its level checks against: the ways a part's contract divides at unit, the paths the sequences draw at architecture, and an objective's main use at real size at ux. It runs only that real and stands doubles in for the rest. A failing test then names the rule, path or use it breaks.

**Steps**

1. Point to the project's shared test rules, and write only where this product differs from them.
2. At unit, divide each input and each result the contract names into classes the part treats alike, the refused ones among them, and write one test for each class.
3. Where a class ends on an ordered scale, such as a length or a count, write one test at each end and one at the nearest value of the next class.
4. Where the contract's result turns on a combination of conditions, write one test for each combination that can occur, with the result it gives.
5. At unit, run a part an AI does on the real model, with one input for each class, both where the contract says the part acts and where it says it does not, and doubles for the parts it works with.
6. At architecture, run real what joins the components, such as hooks and scripts, and stand a double in for each component an AI runs and each thing outside the product, so the level calls no model and gives the same result each run.
7. At architecture, write one test for each path through each story's sequence, the main flow, each branch, each step that sends work back and each question put to the role, until every move from one step to the next lies on some path.
8. At ux, once unit and architecture pass, run the real product on each objective's main use, as the README's walkthrough shows it, at the size of a real request, with an AI standing in for the role that holds an intent the product never sees.
9. At ux, measure each key result as the product vision words it, and set each measure against the last one by the direction the product vision gives it, as the product vision gives no target.
10. For a test whose result varies from run to run, write how many runs of how many must meet the expectation.

### Q13: When the unit and architecture tests pass, does the developer know the product does what this document says, so that the ux level is left only the product vision to confirm?

**Thinking**: Each double gives only results in the form the part's contract gives them, the refusals among them, and is checked as the part's unit tests check the part. Unit and architecture together then show that every path holds for the real parts.

**Steps**

1. For a fault a higher level finds, name the case or path the lower level missed, add its test at the level that must catch it, see it fail, then fix it there.

### Q14: Doubting a choice the document makes, such as a tool or a test's weight, does the developer see what would be lost by the other way, so that they keep or change it knowing what it was for?

**Thinking**: Beside each choice a developer would question, such as a technology, a tool or a unit's weight, stands why it beat the other way and what it costs. The developer then keeps or changes it knowing what it was for.

**Steps**

1. Read each figure as a developer new to the product, and give a why and a cost to each choice they would question.

### Q15: Following a principle while building a part, does the developer find every figure and list asking the same of that part, so that they never choose between the document and itself?

**Thinking**: Each principle and every part it rules say the same. A developer who meets a figure breaking a principle must choose which to follow.

### Q16: Changing how a component works inside while the product vision and the principles stay, does the developer find every line of the document still true, so that the document needs no change for it?

**Thinking**: The document holds only what stays while the product vision and the principles stay. How a component works inside is left to where it is built, as a line about the inside goes untrue at the next change.

**Steps**

1. Imagine a change to how a component works inside, such as its steps, a value it uses or a data's fields, mark each line it would make untrue, and repeat with a change of another kind until no line is marked.
