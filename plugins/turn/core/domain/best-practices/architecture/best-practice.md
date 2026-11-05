# architecture

## Goal

The developer builds and changes each part of the product so that the parts together give its UX.

## Template

[template.md](template.md)

## Example

[example.md](example.md), a copy of [../../../../../../dev/turn/architecture.md](../../../../../../dev/turn/architecture.md)

## User benefits

- **Q1** (the opening): Starting on any part, does the developer see the one idea by which the product gives its UX, and the piece of it the part carries out?
- **Q2** (User stories): Following a step of the UX's scenarios, does the developer find the one user story that carries it?
- **Q3** (Principles): Meeting a case no line of the document names, do two developers of different parts reach the same decision from a principle's why?
- **Q4** (User stories, Components): Facing a decision the stories need, does the developer find the one component that alone decides it?
- **Q5** (Components): Starting on a component, does the developer know what kind of thing it is and what it is made with, choosing nothing themselves?
- **Q6** (Data model): Making one component that writes a data and another that reads it, do two developers join it to the other data the same way?
- **Q7** (User stories, Components, Data model, Sequences): Following a user story from its role's first request to its end, does the developer see at each step which component acts, along which arrow, and what data it hands on?
- **Q8** (User stories, Components, Data model, Sequences): Of any story, component or data, does the developer see which objective of the UX needs it, so that what none needs can go?
- **Q9** (Components, Data model, Deployment): Setting the product up from nothing, does the developer put each component where it runs and each data where it is kept, and start the product, asking no one?
- **Q10** (Components, Data model, Directory structure): Making or changing a component or a data, does the developer find the one place its files belong?
- **Q11** (Deployment, Tests): Asked whether anything in the product goes untested, does the developer see for each deployment unit which levels cover it, how heavily, and why a level is missing?
- **Q12** (Tests): Writing a test at one level, does the developer know what to run real, what doubles stand in for, what to cover and when it passes, deciding none of it?
- **Q13** (Tests): When the unit and architecture tests pass, does the developer know the product does what this document says, leaving to the ux level only the UX to confirm?
- **Q14** (Components, Sequences, Deployment, Directory structure, Tests): Doubting a choice the document makes, such as a tool or a test's weight, does the developer see what would be lost by the other way?
- **Q15** (the whole): Following a principle while building a part, does the developer find every figure and list asking the same of that part?
- **Q16** (the whole): Changing how a component works inside while the UX and the principles stay, does the developer find every line of the document still true?

## Practices

### Q1: Starting on any part, does the developer see the one idea by which the product gives its UX, and the piece of it the part carries out?

**Thinking**: Write how the product turns what its roles bring into what the UX promises as one idea seen from above, pointing to the UX and not repeating it, as every part then reads as a piece of that idea.

**Steps**

1. Once the rest is written, check that each component carries out a piece of the idea, and change the idea or the component where one does not.

### Q2: Following a step of the UX's scenarios, does the developer find the one user story that carries it?

**Thinking**: Write one story for each way a role of the UX meets the product at its edge, drawn from the UX's scenarios and their intent, and name what it carries, such as a step of a scenario or resuming a run that stopped, as each part is then traced to what the role does, and a convenience added is then a story added, leaving the UX and the README as they are.

**Steps**

1. Go through each message of each scenario of the UX, and name the one way at the product's edge that carries it.
2. Where a step meets the product in a way no story names, add the story.
3. For each convenience the UX's intent asks for around its scenarios, such as resuming a run that stopped, name the story that carries it, or add one.

### Q3: Meeting a case no line of the document names, do two developers of different parts reach the same decision from a principle's why?

**Thinking**: Write each principle as one rule every part meeting the same decision follows, and its why as what goes wrong without it, as a developer then carries the why to a case the rule does not name.

**Steps**

1. Write as a rule also what must be absent, such as a dependency no component may have.
2. Point to the principles of the architecture this one builds on, and write only what this product adds or changes.
3. Take a case no rule names, decide it from each why as two developers of different parts would, and sharpen the why where they differ.

### Q4: Facing a decision the stories need, does the developer find the one component that alone decides it?

**Thinking**: Cut the components so that one alone makes each decision the stories need, above all one hard to make or likely to change, and write it in its box, as a decision two components share is made twice and drifts.

**Steps**

1. List each decision the stories need by going through each step of each sequence and asking what must be decided there.
2. Ask of each decision which component makes it, and move the decision or split the component where two or none answer.
3. Label each arrow with what one does to another and the data it hands on, never a word such as "uses".

### Q5: Starting on a component, does the developer know what kind of thing it is and what it is made with, choosing nothing themselves?

**Thinking**: Give each box its type and technology, and a legend for every symbol, as a developer otherwise chooses them alone and the components stop fitting.

**Steps**

1. Read the figure without the text around it, and add to the boxes or the legend whatever a reader would still have to ask.

### Q6: Making one component that writes a data and another that reads it, do two developers join it to the other data the same way?

**Thinking**: Draw each data once by its name and what it is in a few words, with each relation named and how many of each it joins, leaving the fields to where the data is built, as two developers then join a data the same way while its fields change freely.

**Steps**

1. For each relation, ask whether the component that writes it and the one that reads it would keep it the same way, and name the relation more exactly where they would not.

### Q7: Following a user story from its role's first request to its end, does the developer see at each step which component acts, along which arrow, and what data it hands on?

**Thinking**: Draw each story as its steps in order, from the role's first request to what the story gives them, each step taken by a component along an arrow of Components and handing on a named data, as the developer then builds each step knowing who acts and on what.

**Steps**

1. Check that each step runs along an arrow of Components, and add the arrow or give the step to another component where none does.
2. Draw each branch, each step that sends work back and each question put to the role, as each path of the story, and the test of each path, rests on them.

### Q8: Of any story, component or data, does the developer see which objective of the UX needs it, so that what none needs can go?

**Thinking**: Keep only the stories, components and data that an objective of the UX needs, as each can then go once no objective needs it.

**Steps**

1. Trace each component and each data to the stories whose sequences reach it, and each story to the objective whose scenario or intent it carries, and remove what reaches none.

### Q9: Setting the product up from nothing, does the developer put each component where it runs and each data where it is kept, and start the product, asking no one?

**Thinking**: Place each component and each data in one deployment unit, within the environment where it runs or is kept, with each thing outside the product it depends on, as the developer then knows what each can reach and how the product starts.

**Steps**

1. Leave out any infrastructure the components do not need.
2. Check that each component and each data of Components sits in one unit.

### Q10: Making or changing a component or a data, does the developer find the one place its files belong?

**Thinking**: Draw the folders and files that hold each component and each data as they lie on disk, one line each, leaving out what lies inside a component, as the developer then finds the one place to change it.

**Steps**

1. Check that each component and each data stands on one line, and move the files or the line where it stands on none or on two.

### Q11: Asked whether anything in the product goes untested, does the developer see for each deployment unit which levels cover it, how heavily, and why a level is missing?

**Thinking**: Fill the cell of each deployment unit at each level whose ground, a part's contract, this document or the UX, says what the unit must do, and say why a cell is empty, as a level is named by what it checks against and not by its means.

**Steps**

1. Leave out a unit whose every cell would be empty, and say why under the table.
2. Check that unit and architecture carry most of the checking and run on every change, and that ux tests are few.
3. Check that each story's sequence runs from start to end at the architecture level in some row.

### Q12: Writing a test at one level, does the developer know what to run real, what doubles stand in for, what to cover and when it passes, deciding none of it?

**Thinking**: Draw each test from the one thing its level checks against, the ways a part's contract divides, the paths the sequences draw or an objective's scenario at real size, run only that real and stand doubles in for the rest, as a failing test then names the rule, path or scenario it breaks.

**Steps**

1. Point to the project's shared test rules, and write only where this product differs from them.
2. At unit, divide each input and each result the contract names into classes the part treats alike, the refused ones among them, and write one test for each class.
3. Where a class ends on an ordered scale, such as a length or a count, write one test at each end and one at the nearest value of the next class.
4. Where the contract's result turns on a combination of conditions, write one test for each combination that can occur, with the result it gives.
5. At unit, run a part an AI does on the real model, with one input for each class, both where the contract says the part acts and where it says it does not, and doubles for the parts it works with.
6. At architecture, run real what joins the components, such as hooks and scripts, and stand a double in for each component an AI runs and each thing outside the product, so the level calls no model and gives the same result each run.
7. At architecture, write one test for each path through each story's sequence, the main flow, each branch, each step that sends work back and each question put to the role, until every move from one step to the next lies on some path.
8. At ux, once unit and architecture pass, run the real product on each objective's scenario at the size of a real request, with an AI standing in for the role that holds an intent the product never sees.
9. At ux, measure each key result as the UX words it, and set each measure against the last one by the direction the UX gives it, as the UX gives no target.
10. For a test whose result varies from run to run, write how many runs of how many must meet the expectation.

### Q13: When the unit and architecture tests pass, does the developer know the product does what this document says, leaving to the ux level only the UX to confirm?

**Thinking**: Build each double from the form the part's contract gives its results, and check its results as the part's unit tests check the part's, as unit and architecture together then show every path holds for the real parts.

**Steps**

1. Set each double only to results that form allows, the refusals among them.
2. For a fault a higher level finds, name the case or path the lower level missed, add its test at the level that must catch it, see it fail, then fix it there.

### Q14: Doubting a choice the document makes, such as a tool or a test's weight, does the developer see what would be lost by the other way?

**Thinking**: Write beside each choice a developer would question, such as a technology, a tool or a unit's weight, why it beat the other way and what it costs, as the developer then keeps or changes it knowing what it was for.

**Steps**

1. Read each figure as a developer new to the product, and give a why and a cost to each choice they would question.

### Q15: Following a principle while building a part, does the developer find every figure and list asking the same of that part?

**Thinking**: Read each principle against every part it rules, and change the part or the principle until the two say the same, as a developer who meets a figure breaking a principle must choose which to follow.

### Q16: Changing how a component works inside while the UX and the principles stay, does the developer find every line of the document still true?

**Thinking**: Keep in the document only what stays while the UX and the principles stay, leaving how a component works inside to where it is built, as a line about the inside goes untrue at the next change.

**Steps**

1. Imagine a change to how a component works inside, such as its steps, a value it uses or a data's fields, mark each line it would make untrue, and repeat with a change of another kind until no line is marked.
