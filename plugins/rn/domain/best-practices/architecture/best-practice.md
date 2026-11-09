# `architecture`

## Goal

The developers build and change the parts of the product so that together they deliver the product vision.

## Template

[template.md](template.md)

## Example

[example.md](example.md), a copy of [../../../../../dev/rn/architecture.md](../../../../../dev/rn/architecture.md)

## Inputs

- [product-vision](../product-vision/best-practice.md)
- [readme](../readme/best-practice.md)

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The developers know what each part must do, for the users or for the product's development and operation, and why. |
| C2 | Parts that different developers build fit together. |
| C3 | The developers can place, set up, and start every part without asking anyone. |
| C4 | The developers know that the product does what the document says before users try it. |
| C5 | The developers can change the product without making the document wrong. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | Does the opening state the one idea by which the product delivers its vision? | the opening |
| N2 | C1 | Does each step of each objective's main use, as the README's walkthrough shows it, have one user story that carries it? | User stories |
| N3 | C1 | Does each principle, user story, component, and kind of data trace to what the README promises the users, or to a need of the product's development or operation? | Principles, User stories, Components, Data model, Sequences |
| N4 | C2 | Does each principle give a rule and a reason from which two developers decide a case that no line names the same way? | Principles |
| N5 | C2 | Does each decision that the stories need belong to exactly one component? | User stories, Components |
| N6 | C2 | Does each component state its type and its technology? | Components |
| N7 | C2 | Does the data model show how each kind of data relates to the others, without its fields? | Data model |
| N8 | C2 | Does each user story have a sequence that shows, at each step, which component acts, along which arrow, and with which data? | User stories, Components, Data model, Sequences |
| N9 | C2 | Do the figures, lists, and sentences agree with one another, and with the architecture that the product builds on, on what each part does? | the whole |
| N10 | C3 | Does Deployment show where each component runs, where the product keeps each kind of data, and how the product starts? | Components, Data model, Deployment |
| N11 | C3 | Does each component and each kind of data have one place for its files? | Components, Data model, Directory structure |
| N12 | C4 | Does Tests show, for each deployment unit, which test levels cover it, how thoroughly, and why a level is missing? | Deployment, Tests |
| N13 | C4 | Does each test level say what runs real, what test doubles replace, what the tests cover, and when they pass? | Tests |
| N14 | C4 | Do the unit and architecture tests together check everything the document says the product does? | Tests |
| N15 | C5 | Does each choice whose other way would cost a key result say what the other way would lose? | Components, Deployment, Directory structure, Tests |
| N16 | C5 | Does the document hold only what stays true while the product vision and the principles stay, and leave each component's internals out? | the whole |

## Practices

### N1

Does the opening state the one idea by which the product delivers its vision?

**Thinking**

Each part is a piece of one idea, and a developer who knows the idea builds a part that serves it. The solution strategy of [arc42](https://arc42.org) states the few fundamental decisions that shape the whole system. Decide the idea in order. First, take the one way that the product vision's concept states first, by which the product brings its users to their objectives. Second, ask how the system as a whole makes that way work: what it takes in from the roles, and what it turns that into. Third, write the answer in two or three sentences that a developer can hold in mind while building any part. Point to the product vision instead of repeating it.

**Steps**

1. After writing the rest, check that each component carries out a piece of the idea. Change the idea or the component where one doesn't.

### N2

Does each step of each objective's main use, as the README's walkthrough shows it, have one user story that carries it?

**Thinking**

The stories connect the parts to what the users do, so every part can trace back to a step a user takes. Jeff Patton's user story mapping lays the steps of the main use along a backbone, and hangs a [user story](https://www.mountaingoatsoftware.com/agile/user-stories) on each. Take the backbone from the README's walkthrough, and from the main use of each objective that the walkthrough doesn't run. For each step, ask how the role meets the product at its edge there, such as a command they type, and write one story for each such way, naming the steps it carries. Add a story for each convenience the product vision asks for, such as resuming a run that stopped.

**Steps**

1. Go through each exchange of the README's walkthrough, and the main use of each objective it doesn't run, and name the one story that carries each step. Add a story where none does. The trace: `{inputs}` read to its end.

### N3

Does each principle, user story, component, and kind of data trace to what the README promises the users, or to a need of the product's development or operation?

**Thinking**

A part that nothing needs costs effort to build and to keep, and gives no one anything. Three sources say what the parts must do. The README carries what the users get from the product vision: the steps of its walkthrough, and the doubts that its How it works answers. Development adds what the developers need to build, test, and change the parts. Operation adds what keeps the product working across runs and updates, such as where its work outlives a run. For each principle and each story, ask which step, doubt, or need it carries. For each component and each kind of data, ask which principle or which story's sequence reaches it. Remove whatever reaches none. This is requirements traceability, applied from the parts back to their sources.

### N4

Does each principle give a rule and a reason from which two developers decide a case that no line names the same way?

**Thinking**

Developers of different parts meet the same kind of decision, and decide it apart unless a principle settles it. The principles of The Open Group Architecture Framework (TOGAF) give each a statement, a rationale, and its implications. Derive the principles from the README's How it works, which answers each doubt of the users from an idea of the product vision's concept, and from the needs of development and operation. First, for each answer and each need, ask what every part must hold alike for it to come true, such as where the work's state lives. A part that held it otherwise would break a key result. Each answer is a principle. Second, for each, write the rule in one to three short sentences. Third, write the reason: what goes wrong without the rule, for a role of the product vision, naming the key result it guards, or for the developers or the operators. A developer carries the reason to a case that the rule doesn't name. Point to the principles of any architecture this one builds on, and write only what this product adds or changes.

**Steps**

1. Take a case that no rule names, and decide it from each reason as two developers of different parts would. Where they differ, sharpen the reason.

### N5

Does each decision that the stories need belong to exactly one component?

**Thinking**

Two components that make the same decision make it twice, and the two copies drift apart. David Parnas's information hiding gives each module one decision that's hard to make or likely to change, and hides it from the rest. Decide the components in order. First, take from the stories the decisions that are hard to make or likely to change, such as where the product keeps the work's state. Second, give each such decision to one component. Third, where two components need the same decision, give it to one, and have the other ask that one. List under the figure what each component alone decides.

**Steps**

1. Label each arrow with what one component does to another and the data it passes, not a word such as `uses`.

### N6

Does each component state its type and its technology?

**Thinking**

A developer who doesn't know what kind of thing a component is, or what it's built with, chooses alone, and the components stop fitting. The [C4 model](https://c4model.com/diagrams/container) gives each box its name, its type, such as a script, a skill, or a folder of JSON files, and its technology. Draw a store of data as a box like a component's, since its type sets it apart. For each component, decide the type and the technology from the product's constraints, such as the runtime its users have. Give the figure a legend for every symbol.

**Steps**

1. Read the figure without the text around it, and add to the legend whatever symbol a reader would still have to ask about. Draw and lay out the figure as [N4 of the refactor-doc best practice](../refactor-doc/best-practice.md#n4) says.

### N7

Does the data model show how each kind of data relates to the others, without its fields?

**Thinking**

Two developers who build the writer and the reader of the same data must join it to the other data in the same way, while its fields stay free to change. A concept model in a class diagram of the Unified Modeling Language (UML), which most developers read, shows this. Decide it in order. First, list each kind of data that the components pass or keep, and draw each once, as a class by its name alone. Second, for each pair that relates, name the relation, and give how many of each it joins at both ends. Where one holds the other's parts, put a filled diamond at the whole, since readers take a hollow one in different ways. Third, group the data in a frame for each component that keeps them, in the order the stories meet them, with the data that most others join in the middle. Leave the fields to where the developer builds the data. Below the figure, say in a few words what a kind of data is only where a reader could take its name for another's.

### N8

Does each user story have a sequence that shows, at each step, which component acts, along which arrow, and with which data?

**Thinking**

A developer building a step must know who acts there, on what, and what comes next. A [UML](https://www.omg.org/spec/UML) sequence diagram draws a story's steps in order, from the role's first request to what the story gives them. For each story, draw each step as a message from one component to another along an arrow of Components, with the data it passes, named as in the data model. Draw each branch, each step that sends work back, and each question put to the role, since each path of the story, and its test, rests on them. Stories that share their steps share a diagram.

**Steps**

1. Check that each step runs along an arrow of Components. Where none does, add the arrow, or give the step to another component.

### N9

Do the figures, lists, and sentences agree with one another, and with the architecture that the product builds on, on what each part does?

**Thinking**

A developer who finds two places that say different things about a part must choose which to follow, and two developers choose differently. The architecture that the product builds on, such as a shared best practice for its kind of product, holds rules that each part must keep as well. For each part, gather what every figure, list, and sentence says it does, and what each rule of that architecture asks of a part of its kind. Where two disagree, decide by the reasons of the principles and of those rules which is right, and change the other.

### N10

Does Deployment show where each component runs, where the product keeps each kind of data, and how the product starts?

**Thinking**

A developer setting up the product needs to know where each part runs, what it can reach, and how it starts. A [C4 deployment diagram](https://c4model.com/diagrams/deployment) shows this. Decide it in order. First, list each environment the product runs in, such as the user's computer or CI, with its technology. Second, place each component and each kind of data in one deployment unit within its environment. Third, add each thing outside the product that the components depend on, with what they use of it, and no infrastructure that they don't need. Then write in one sentence how the product starts. Check that a developer could set the product up from nothing by the figure and that sentence.

### N11

Does each component and each kind of data have one place for its files?

**Thinking**

A developer making a change must find the one place it belongs. Lay out the folders by component, so that each component and each kind of data has its own place. First, say in one sentence for each top folder whom its files are for, such as the users who install the product or only its developers. Then show each folder and file that holds a component or a kind of data, by its real name, one line each, nested as on disk, without the files inside a component. Beside each, say what it does or holds, in the words a developer looks for when making a change. Check that, for any change to a component, a developer can name the one folder it goes in.

### N12

Does Tests show, for each deployment unit, which test levels cover it, how thoroughly, and why a level is missing?

**Thinking**

A part that no test level covers can break unseen. The [test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) puts most checks at the narrow, fast levels and few at the wide, slow ones. Name each level by what it checks against: unit against a part's contract, architecture against this document, and product vision against the product vision, in real use. Decide the table in order. First, list each deployment unit as a row. Second, for each level, ask what the unit must do by that level's ground, and fill the cell with the tool and how far it tries the unit, and nothing more. `FULL` tries each case and edge, `HAPPY` the main paths, and `SMOKE` one run that confirms what the lower levels checked. Third, where a cell stays empty, say why. Unit and architecture carry most of the checking, and run on every change.

**Steps**

1. Leave out a unit whose every cell would be empty, and say why under the table.
2. Check that each story's sequence runs from start to end at the architecture level in some row.

### N13

Does each test level say what runs real, what test doubles replace, what the tests cover, and when they pass?

**Thinking**

A failing test should name the rule, path, or use that it breaks. Draw each test from the one thing its level checks against: the ways a part's contract divides at unit, the paths the sequences draw at architecture, and an objective's main use at real size at product vision. Run only that thing real, and replace the rest with [test doubles](https://martinfowler.com/bliki/TestDouble.html). Point to the project's shared test rules, and write only where this product differs from them.

**Steps**

1. At unit, divide each input and each result that the contract names into classes that the part treats alike, the refused ones among them, and write one test for each class. This is equivalence partitioning, as the [glossary](https://glossary.istqb.org) of the International Software Testing Qualifications Board defines it.
2. Where a class ends on an ordered scale, such as a length or a count, write one test at each end and one at the nearest value of the next class. This is boundary value analysis.
3. Where the contract's result depends on a combination of conditions, write one test for each combination that can occur, with the result it gives. This is decision table testing.
4. At unit, pass when every test passes, every line and branch runs, and the tests catch every mutant. Add a unit test for each gap that coverage, mutation testing, or a property-based test finds. These tools confirm the tests drawn from the contract, and draw none themselves.
5. At unit, where no guard holds each rule of a part that an AI does on every run, run the part on the real model, with one input for each class, both where the contract says the part acts and where it says it doesn't, and doubles for the parts it works with.
6. At architecture, run real what joins the components, such as hooks and scripts, and replace each component that an AI runs and each thing outside the product with a double, so that the level calls no model and gives the same result on each run.
7. At architecture, write one test for each path through each story's sequence: the main flow, each branch, each step that sends work back, and each question put to the role, until every move from one step to the next lies on some path.
8. Run the unit and architecture tests that a change reaches before each push, and every test in CI. Running every test before each push makes each change wait, and a selection misses a test that reads a file the change edits.
9. At product vision, once unit and architecture pass, run the real product on each objective's main use, as the README's walkthrough shows it, at the size of a real request, with an AI in the role that holds an intent the product never receives.
10. At product vision, measure each key result as the product vision words it, and compare each measure with the last one by the direction the product vision gives, since the product vision sets no target.
11. At product vision, run each role on the model its users run, judge each run from its records, and try no case that a lower level can test. Another model makes other mistakes than the users meet, and each run is slow and costly.
12. For a test whose result varies from run to run, write how many runs out of how many must meet the expectation.

### N14

Do the unit and architecture tests together check everything the document says the product does?

**Thinking**

The product vision tests are slow and few, so they can only confirm what the lower levels already showed. Unit and architecture together show it only if each double behaves like the part it replaces. Give each double only results in the form the part's contract gives, refusals among them, and test the double as the part's unit tests test the part. Then, for each thing the document says the product does, name the unit or architecture test that checks it, and add a test where none does.

**Steps**

1. Draw a double of something outside the product from its documentation or from a recorded run of the real thing. A double that gives what the real thing never would passes a test that the real one fails.
2. For a fault that a higher level finds, name the case or path that the lower level missed, add its test at the level that must catch it, see it fail, and then fix it there.
3. Trust a check, such as a test, a hook, or the judge of a trial, only once you have seen it fail on a case that breaks what it checks. Trust a judge once it's right on kept records whose answer you know.

### N15

Does each choice whose other way would cost a key result say what the other way would lose?

**Thinking**

A developer who doubts a choice and can't see what it was for may undo it and bring back the problem it solved. An [architecture decision record](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), by Michael Nygard, keeps a decision with its context and consequences. For each choice whose other way would bring back a problem that costs a key result, such as a technology, a tool, or how far a level tests a unit, name the other way it beat, what the choice gives, ending with the key result it serves, and what it costs. Write it beside the choice, one sentence for each.

**Steps**

1. For each choice that a figure shows, ask what the other way would bring back. Give a reason and a cost only where it would cost a key result.

### N16

Does the document hold only what stays true while the product vision and the principles stay, and leave each component's internals out?

**Thinking**

A line about how a component works inside becomes untrue at the next change to that component, and the developer then can't trust the document. Information hiding keeps such details inside the module. For each line, ask whether it would become untrue if a component's internals changed while the product vision and the principles stayed. If it would, move it to where the developer builds the component.

**Steps**

1. Imagine a change to how a component works inside, such as its steps, a value it uses, or a data's fields, and mark each line it would make untrue. Repeat with a change of another kind until you mark no line.
