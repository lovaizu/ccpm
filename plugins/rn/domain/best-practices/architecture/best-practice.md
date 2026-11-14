# `architecture`

## Goal tree

- The developers build and change the parts of the product so that together they deliver what the README promises the users.
  - **C1** The developers know what each part must do, for the users or for the product's development and operation, and why.
    - **N1** Does the opening state the one idea by which the product delivers what its README promises? (the opening)
    - **N2** Does each step of each objective's main use, as the README's walkthrough shows it, have one user story that carries it? (User stories)
    - **N3** Does each principle, user story, component, and kind of data trace to what the README promises the users, or to a need of the product's development or operation? (Principles, User stories, Components, Data model, Sequences)
  - **C2** Parts that different developers build fit together.
    - **N4** Does each principle give a rule and a reason from which two developers decide a case that no line names the same way? (Principles)
    - **N5** Does each decision that the stories need belong to exactly one component? (User stories, Components)
    - **N6** Does each component state its type and its technology? (Components)
    - **N7** Does the data model show how each kind of data relates to the others, without its fields? (Data model)
    - **N8** Does each user story have a sequence that shows, at each step, which component acts, along which arrow, and with which data? (User stories, Components, Data model, Sequences)
    - **N9** Do the figures, lists, and sentences agree with one another, and with the architecture that the product builds on, on what each part does? (the whole)
  - **C3** The developers can place, set up, and start every part without asking anyone.
    - **N10** Does Deployment show where each component runs, where the product keeps each kind of data, and how the product starts? (Components, Data model, Deployment)
    - **N11** Does each component and each kind of data have one place for its files? (Components, Data model, Directory structure)
  - **C4** The developers find each gap between the parts before they build any part, and know, as they build, that the product does what the document and the product vision say.
    - **N12** Does Test strategy decide the types of testing that the key results call for, and, for each test level, what it tests, what runs real, its tools, when it runs, and each quality check with the criterion by which it passes? (Test strategy)
    - **N13** Does each part have its skeleton, and every part, every element of this document, and every key result its test cases in the test code, each written as Given, When, and Then through that skeleton, and each naming the case or the element one level up that it supports? (Test strategy)
    - **N14** Does each thing that the document says the product does rest on a part that a unit or integration test can check? (Components, Test strategy)
  - **C5** The developers can change the product without making the document wrong.
    - **N15** Does each choice whose other way would cost a key result say what the other way would lose? (Components, Deployment, Directory structure, Test strategy)
    - **N16** Does the document hold only what stays true while the product vision and the principles stay, and leave each component's internals out? (the whole)

## Template

[template.md](template.md)

## Inputs

- [product-vision](../product-vision/best-practice.md)
- [readme](../readme/best-practice.md)

## Practices

### N1

Does the opening state the one idea by which the product delivers what its README promises?

Each part is a piece of one idea, and a developer who knows the idea builds a part that serves it. The solution strategy of [arc42](https://arc42.org) states the few fundamental decisions that shape the whole system.

1. *While deciding.* Take the one way that the README's How it works states first, from the product vision's concept, by which the product brings its users to their objectives. The trace: `{inputs}` read to its end.
2. *While deciding.* Ask how the system as a whole makes that way work: what it takes in from the roles, and what it turns that into.
3. *While making.* Write the answer in two or three sentences that a developer can hold in mind while building any part. Point to the README instead of repeating it.
4. *While making.* After writing the rest, read each component's line as a developer who knows only the idea, and check that they can see which piece of the idea it carries out. Change the idea or the component where they can't.

### N2

Does each step of each objective's main use, as the README's walkthrough shows it, have one user story that carries it?

The stories connect the parts to what the users do, so every part can trace back to a step a user takes. Jeff Patton's user story mapping lays the steps of the main use along a backbone, and hangs a [user story](https://www.mountaingoatsoftware.com/agile/user-stories) on each.

1. *While deciding.* Take the backbone from the README's walkthrough, and from the main use of each objective that the walkthrough doesn't run.
2. *While deciding.* For each step, ask how the role meets the product at its edge there, such as a command they type, and write one story for each such way, naming the steps it carries.
3. *While deciding.* Add a story for each convenience the product vision asks for, such as resuming a run that stopped.
4. *While making.* Go through each exchange of the README's walkthrough, and the main use of each objective it doesn't run, and name the one story that carries each step. Add a story where none does.

### N3

Does each principle, user story, component, and kind of data trace to what the README promises the users, or to a need of the product's development or operation?

A part that nothing needs costs effort to build and to keep, and gives no one anything. The method is requirements traceability, as Orlena Gotel and Anthony Finkelstein [analyze it](https://doi.org/10.1109/ICRE.1994.292398), applied from the parts back to their sources.

1. *While deciding.* For each principle and each story, ask which step, doubt, or need it carries, from three sources. The README carries what the users get from the product vision: the steps of its walkthrough, and the doubts that its How it works answers. Development adds what the developers need to build, test, and change the parts. Operation adds what keeps the product working across runs and updates, such as where its work outlives a run.
2. *While deciding.* For each component and each kind of data, ask which principle or which story's sequence reaches it.
3. *While making.* Remove whatever reaches none.

### N4

Does each principle give a rule and a reason from which two developers decide a case that no line names the same way?

Developers of different parts meet the same kind of decision, and decide it apart unless a principle settles it. The principles of The Open Group Architecture Framework (TOGAF) give each a statement, a rationale, and its implications.

1. *While deciding.* Derive the principles from the README's How it works, which answers each doubt of the users from an idea of the product vision's concept, and from the needs of development and operation.
2. *While deciding.* For each answer and each need, ask what every part must hold alike for it to come true, such as where the work's state lives. A part that held it otherwise would break a key result. Each thing that every part must hold alike is a principle.
3. *While deciding.* Leave out what a single component's line already says, since a principle holds only a rule that spans parts.
4. *While making.* For each principle, write the rule in one sentence, naming the parts as Components names them.
5. *While making.* Write the reason in one sentence: what goes wrong without the rule, for a role of the product vision, naming the key result it guards, or for the developers or the operators. A developer carries the reason to a case that the rule doesn't name.
6. *While making.* Point to the principles of any architecture this one builds on, and write only what this product adds or changes.
7. *While making.* Take a case that no rule names, and decide it from each reason as two developers of different parts would. Where they differ, sharpen the reason.

### N5

Does each decision that the stories need belong to exactly one component?

Two components that make the same decision make it twice, and the two copies drift apart. David Parnas's information hiding gives each module one decision that's hard to make or likely to change, and hides it from the rest.

1. *While deciding.* Take from the stories the decisions that are hard to make or likely to change, such as where the product keeps the work's state.
2. *While deciding.* Give each such decision to one component.
3. *While deciding.* Where two components need the same decision, give it to one, and have the other ask that one.
4. *While making.* List under the figure what each component alone decides.
5. *While making.* Label each arrow with what one component does to another and the data it passes, not a word such as `uses`.

### N6

Does each component state its type and its technology?

A developer who doesn't know what kind of thing a component is, or what it's built with, chooses alone, and the components stop fitting. The [C4 model](https://c4model.com/diagrams/container) gives each box its name, its type, such as a script, a skill, or a folder of JSON files, and its technology.

1. *While deciding.* For each component, decide the type and the technology from the product's constraints, such as the runtime its users have.
2. *While making.* Draw and lay out the figure as [the refactor-doc best practice](../refactor-doc/best-practice.md) says of diagrams.
3. *While making.* Draw a store of data as a box like a component's, since its type sets it apart.
4. *While making.* Give the figure a legend for every symbol.
5. *While making.* Read the figure without the text around it, and add to the legend whatever symbol a reader would still have to ask about.

### N7

Does the data model show how each kind of data relates to the others, without its fields?

Two developers who build the writer and the reader of the same data must join it to the other data in the same way, while its fields stay free to change. A concept model in a class diagram of the Unified Modeling Language (UML), which most developers read, shows this.

1. *While deciding.* List each kind of data that the components pass or keep.
2. *While deciding.* For each pair that relates, name the relation, and give how many of each it joins at both ends.
3. *While making.* Draw each once, as a class by its name alone.
4. *While making.* Where one holds the other's parts, put a filled diamond at the whole, since readers take a hollow one in different ways.
5. *While making.* Group the data in a frame for each component or store that keeps them, in the order the stories meet them, with the data that most others join in the middle.
6. *While making.* Leave the fields to where the developer builds the data.
7. *While making.* Below the figure, say in a few words what a kind of data is only where a reader could take its name for another's.

### N8

Does each user story have a sequence that shows, at each step, which component acts, along which arrow, and with which data?

A developer building a step must know who acts there, on what, and what comes next. A [UML](https://www.omg.org/spec/UML) sequence diagram draws a story's steps in order, from the role's first request to what the story gives them.

1. *While making.* For each story, draw each step as a message from one component to another along an arrow of Components, with the data it passes, named as in the data model.
2. *While making.* Draw each branch, each step that sends work back, and each question put to the role, since each path of the story, and its integration test, rests on them.
3. *While making.* Let stories that share their steps share a diagram.
4. *While making.* Read each sequence as the developer who builds one of its steps, and check that they can tell, at each step, which component acts, along which arrow of Components, with which data, and what comes next. Where no arrow carries a step, add the arrow, or give the step to another component.

### N9

Do the figures, lists, and sentences agree with one another, and with the architecture that the product builds on, on what each part does?

A developer who finds two places that say different things about a part must choose which to follow, and two developers choose differently. [ISO/IEC/IEEE 42010](https://www.iso.org/standard/74393.html) keeps the views of an architecture consistent by correspondences, which relate what each view says about the same element.

1. *While making.* For each part, gather what every figure, list, and sentence says it does, and what each rule of the architecture that the product builds on asks of a part of its kind. That architecture, such as a shared best practice for its kind of product, holds rules that each part must keep as well.
2. *While making.* Where two disagree, decide by the reasons of the principles and of those rules which is right, and change the other.

### N10

Does Deployment show where each component runs, where the product keeps each kind of data, and how the product starts?

A developer setting up the product needs to know where each part runs, what it can reach, and how it starts. A [C4 deployment diagram](https://c4model.com/diagrams/deployment) shows this.

1. *While deciding.* List each environment the product runs in, such as the user's computer or CI, with its technology.
2. *While deciding.* Place each component and each kind of data in one deployment unit within its environment.
3. *While deciding.* Add each thing outside the product that the components depend on, with what they use of it, and no infrastructure that they don't need.
4. *While making.* Write in one sentence how the product starts.
5. *While making.* Check that a developer could set the product up from nothing by the figure and that sentence.

### N11

Does each component and each kind of data have one place for its files?

A developer making a change must find the one place it belongs. Simon Brown's package by component, in Robert C. Martin's *Clean Architecture*, lays out the code by the components that the architecture draws.

1. *While deciding.* Lay out the folders by component, so that each component and each kind of data has its own place.
2. *While making.* Say in one sentence for each top folder whom its files are for, such as the users who install the product or only its developers.
3. *While making.* Show each folder and file that holds a component or a kind of data, by its real name, one line each, nested as on disk, without the files inside a component.
4. *While making.* Beside each, say what it does or holds, in the words a developer looks for when making a change.
5. *While making.* Check that, for any change to a component, a developer can name the one folder it goes in.

### N12

Does Test strategy decide the types of testing that the key results call for, and, for each test level, what it tests, what runs real, its tools, when it runs, and each quality check with the criterion by which it passes?

A case's pass or fail decides the work only where its level's tools and criteria are set before anyone writes the case. The V-model, as the [glossary](https://glossary.istqb.org) of the International Software Testing Qualifications Board (ISTQB) defines it, pairs each level of development with a test level, and the [test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) puts most checks at the narrow, fast levels. The product quality model of [ISO/IEC 25010](https://www.iso.org/standard/78176.html) names the kinds of quality from which the types of testing a product needs are chosen.

1. *While deciding.* Name the levels unit tests, integration tests, and end-to-end (E2E) tests, and use no other name for a test. Unit tests try each part, each prompt among them, against its contract. Integration tests try the parts joined against each element of this document. E2E tests try the product in real use against each key result of the product vision.
2. *While deciding.* For each level, run real only what it tests, and replace the rest with [test doubles](https://martinfowler.com/bliki/TestDouble.html). At unit, run the part, with a double for each part it works with that's slow or outside the test. At integration, run what joins the components, such as hooks and scripts, with a double for each component that an AI runs and for each thing outside the product, so that the level calls no model and gives the same result on each run. At E2E, run the whole product on the model its users run, with an AI in the role that holds an intent the product never receives, since another model makes other mistakes than the users meet.
3. *While deciding.* List the candidate types of testing by the characteristics of the product quality model of ISO/IEC 25010, such as performance efficiency, compatibility, reliability, and security, each the kind of quality that a type of testing checks, since a strategy that starts from the levels alone tests only what each level's cases name, and leaves unasked a kind of quality that the users meet.
4. *While deciding.* Of those types, choose the vital few for each target of the quality checks, the parts, the architecture, and the product vision, and how far each goes, since every type in a catalog could be tested and testing them all is the trivial many: for each type, ask whether, given what the product is and what it builds on, its users would fail a key result of the product vision without it, such as a host whose new version behaves otherwise, and drop each type where they wouldn't. For each type kept, write that failure as its reason, and name the target and the level it checks, and its quality check with the criterion by which it passes, set only as far as that failure calls for. Leave out functional suitability, which every level's cases try, as N13 says.
5. *While deciding.* Where compatibility is kept for something outside the product that changes on its own schedule, such as the host the product runs in, set the check of each double of it against the real thing, at the integration level whose doubles it keeps true: run the steps that made each recorded run again on each new version, and compare what the real thing gives with what the double gives, and check that each page of documentation that a double rests on still shows its words, passing only where they agree. Where they differ, the developers record the new version's run, change the double to give what it shows, and fix the product where a test then fails, since a double that the real thing has outgrown passes a test that its users' version fails. This is Martin Fowler's [contract test](https://martinfowler.com/bliki/ContractTest.html), which runs against the real thing apart from the work, and the check that [Software Engineering at Google](https://abseil.io/resources/swe-book/html/ch13.html) runs on both the real thing and its double, so that the double doesn't drift as the real thing evolves.
6. *While deciding.* Choose each level's tools from the product's constraints, such as the runtime its users have, and name each: the test runner, and the tool of each quality check.
7. *While deciding.* Set the quality checks of the parts, each with its criterion, since a check without one passes whatever it finds: line and branch coverage, the mutants that survive, the limits on each function's complexity, its returns, branches, arguments, and statements, and the findings of static analysis, such as types, import cycles, and copied code, and of lint.
8. *While deciding.* Name each contract that takes a wide input, such as the reader of a file that an AI writes, for property-based tests that find no counterexample, and leave the other contracts to the cases drawn by hand.
9. *While deciding.* Set k, how many times a prompt's unit tests run each case on the model its users run, and pass the case only where all k runs pass, as pass^k of Anthropic's [demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) measures it. Choose k by how rare a slip must still show against what each run costs.
10. *While deciding.* Set the quality checks of the architecture, and name the script that checks them by the names of the elements, not by reading: every element of this document, each story, principle, component, and kind of data, has an integration test; every test names an element or a case one level up that exists; every unit case names an integration case; a test of a principle that must not break is trusted only once seen to fail with the principle broken; and each double gives only what a recorded run or the official documentation shows, as N14 says.
11. *While deciding.* Set the quality checks of the product vision: each key result's value, compared with the last run's by the order the product vision gives, since the product vision sets no target; a judge, trusted only once it's right on kept records whose answer is known; and how many times each E2E test runs its main use at real size, since the AI's variance shows only across runs.
12. *While deciding.* Run each check at the time that what it checks calls for, not by how long it takes. Before each push, run the static analysis, the unit tests of code and the integration tests that the change reaches, and their coverage, since these show whether the change does what its design says, and the work waits on them. Running every such test there meets this too, as a selection by what the change reaches misses a test that reads a file the change edits. On each push, in CI, run every unit test of code and every integration test, and mutation testing and property-based tests over the lines that the push changed, apart from the work, since these check the tests and not the change. Each night, in CI, run every check that runs on its own over the whole, property-based tests at their most inputs among them, since a run over a push's lines misses a test changed alone and a fault between parts that no one push changed together. Run the check of each double against the real thing on each new version of the thing, which a job in CI finds each night by its version, since only a new version changes what the double must give. Run a prompt's unit tests before a change of the prompt is taken, and the E2E tests once every lower level passes, since each run calls the model and is slow and costly.
13. *While making.* Write a subsection for each level, from unit to E2E, in the form of the template.
14. *While making.* Point to the test rules of the architecture that the product builds on, such as the form each case takes, and write only what this product sets.

### N13

Does each part have its skeleton, and every part, every element of this document, and every key result its test cases in the test code, each written as Given, When, and Then through that skeleton, and each naming the case or the element one level up that it supports?

Every case written through a skeleton of the parts before any body is built checks the architecture while a gap between the parts is still cheap to fix: a case that no part can hold, or a handoff that no interface carries, shows the gap before anyone builds around it. The V-model of the [ISTQB glossary](https://glossary.istqb.org) designs each level's tests during the development activity it pairs with, and Steve Freeman and Nat Pryce's outside-in test-driven development, in [Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/) and [Mock Roles, not Objects](http://jmock.org/oopsla2004.pdf), finds each part's roles and interface by first writing the tests one level up. A case finds a gap only where it calls a real interface, and the skeleton is code, apart from this document, which keeps no part's internals.

1. *While making.* Once Test strategy names the tools, make the skeleton of each part where Directory structure places it, from the arrows and the data that Sequences hand to the part: each module with the decision it alone makes and each interface with its contract, as [the code best practice](../code/best-practice.md) says of modules and interfaces, and each prompt with its description and the form of what it takes and gives, as [the prompt best practice](../prompt/best-practice.md) says, each body left empty, such as one that raises `NotImplementedError`.
2. *While making.* Write the E2E cases first: for each key result, a case that runs an objective's main use, as the README's walkthrough shows it, at the size of a real request, and names the key result, such as `KR1.1`.
3. *While making.* Write the integration cases from the elements of this document, each naming its element by its name: a case for each path through each story's sequence, the main flow, each branch, each step that sends work back, and each question put to the role, until every move from one step to the next lies on some path; a case for each principle, where the parts keep it and where one breaks it; a case for each decision that a component alone makes; and a case for each handoff between parts, with the data it passes as the data model names it, until each kind of data lies on some case.
4. *While making.* Write the unit cases of each part through its interface, each naming the integration case it supports, so that the interface a part offers comes from what the cases one level up need of it, and change the skeleton where a case needs an interface it lacks or calls none it offers.
5. *While making.* Divide each input and each result that a part's contract names into classes that the part treats alike, the refused ones among them, and write one case for each class. This is equivalence partitioning, as the ISTQB glossary defines it.
6. *While making.* Where a class ends on an ordered scale, such as a length or a count, write one case at each end and one at the nearest value of the next class. This is boundary value analysis.
7. *While making.* Where the contract's result depends on a combination of conditions, write one case for each combination that can occur, with the result it gives. This is decision table testing.
8. *While making.* For a prompt, write a case where its contract says it acts and one where it says it doesn't, for each kind of request it's for, and decide by code each point of the result that its record shows.
9. *While making.* Write each case as a test in the test code, in the place that Directory structure names, with its Given, When, and Then stated, and write no list of the cases in a document, since a list beside the code says each case twice.
10. *While making.* Run the type checker over the skeleton and the cases, and see every case fail: a type that doesn't fit across a handoff is a gap between the parts, and a case that passes on an empty body tests nothing.
11. *While making.* Read the cases and the skeleton against the architecture, and go back to the architecture where they show a gap: a case that no part can hold needs a part, or a decision given to one; a part that no case reaches serves no element, as N3 says; a module that can't state its decision in a few words makes more than one; a part whose cases change for more than one reason, such as a file's form and a remote's commands, holds more than one part, as Robert C. Martin's single responsibility principle has it; and a handoff that no interface carries needs an arrow and a kind of data. Change the architecture first, and then the skeleton and the cases.
12. *While making.* Run the script that checks the trace, and mend each case or element it names until it names none. The script finds only a name that leads nowhere, so its 0 shows no more than that: whether the cases are enough, and whether the parts are cut right, the reading before it judges.
13. *While making.* Once the parts are being built, add a case only where it names a case one level up, and take a case that names none back to the architecture, since such a case tests what no element asks for.

### N14

Does each thing that the document says the product does rest on a part that a unit or integration test can check?

The E2E tests are slow and few, so they can only confirm what the lower levels already showed, and a thing that only a prompt holds varies from run to run, where only many runs on the model show it. The [Humble Object](https://martinfowler.com/bliki/HumbleObject.html) pattern of Gerard Meszaros's *xUnit Test Patterns* moves the logic out of a part that's hard to test into a part that a test can run.

1. *While deciding.* For each thing the document says the product does, name the part that holds it.
2. *While deciding.* Where only a prompt holds a rule that must hold on every run, give the rule to a part that a test can run, such as a guard of the architecture the product builds on, and draw that part in Components.
3. *While deciding.* Leave a judgment that only an AI can make, such as whether a point is the user's, with the AI, and try it by the prompt's unit tests on the model, as N12.9 sets.
4. *While making.* The lower levels show a part only if each double behaves like the part it replaces, so give each double only results in the form the part's contract gives, refusals among them.
5. *While making.* Test each double as the part's unit tests test the part.
6. *While making.* Draw a double of something outside the product from its documentation or from a recorded run of the real thing, and name that source beside what the double gives, so that the script of N12.10 can check it. A double that gives what the real thing never would passes a test that the real one fails.
7. *While making.* For a fault that a higher level finds, name the case that the lower level missed, add it at the level that must catch it, naming the case one level up, see it fail, and then fix it there.
8. *While making.* Trust a check, such as a test, a hook, or the judge of an E2E test, only once you have seen it fail on a case that breaks what it checks, such as a test of a principle run with the part that holds the principle taken out, which the script of N12.10 can run. Trust a judge once it's right on kept records whose answer you know.

### N15

Does each choice whose other way would cost a key result say what the other way would lose?

A developer who doubts a choice and can't see what it was for may undo it and bring back the problem it solved. An [architecture decision record](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), by Michael Nygard, keeps a decision with its context and consequences.

1. *While deciding.* For each choice whose other way would bring back a problem that costs a key result, such as a technology, a tool, or the k of a prompt's unit tests, name the other way it beat, what the choice gives, ending with the key result it serves, and what it costs.
2. *While making.* Write it beside the choice, one sentence for each.
3. *While making.* For each choice that a figure shows, ask what the other way would bring back. Give a reason and a cost only where it would cost a key result.

### N16

Does the document hold only what stays true while the product vision and the principles stay, and leave each component's internals out?

A line about how a component works inside becomes untrue at the next change to that component, and the developer then can't trust the document. David Parnas's [information hiding](https://doi.org/10.1145/361598.361623) keeps such details inside the module.

1. *While making.* For each line, ask whether it would become untrue if a component's internals changed while the product vision and the principles stayed.
2. *While making.* If it would, move it to where the developer builds the component.
3. *While making.* Imagine a change to how a component works inside, such as its steps, a value it uses, or a data's fields, and mark each line it would make untrue. Repeat with a change of another kind until you mark no line.
