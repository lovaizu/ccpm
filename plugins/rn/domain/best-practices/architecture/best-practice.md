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
    - **N12** Does Test strategy decide the types of testing of each target, every type of code and test quality for the parts and those the key results call for in the product vision's, and, for each test level, what it tests, what runs real, its tools, when it runs, and each quality check with the criterion by which it passes? (Test strategy)
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

Each part is a piece of one idea, and a developer who knows the idea builds a part that serves it.

1. *While deciding.* Open your cut, and read to its end each input it names: the product vision, the README, and, where the product builds on another's rules, the architecture it builds on, such as a guide to building a plugin of the host it runs in. The trace: `{inputs}` read to its end.
2. *While deciding.* In the README's How it works, take the first way it states, from the product vision's concept, by which the product brings its users to their objectives, such as keeping every decision of a run in one file that each role reads.
3. *While deciding.* Ask how the system as a whole makes that way work: what it takes in from the roles, and what it turns that into, such as a request typed in a session turned into a deliverable that passed its checks.
4. *While making.* Write the answer in two or three sentences that a developer can hold in mind while building any part. Point to the README instead of repeating it.
5. *While making.* After writing the rest, read each component's line as a developer who knows only the idea, and check that they can see which piece of the idea it carries out. Change the idea or the component where they can't.

### N2

Does each step of each objective's main use, as the README's walkthrough shows it, have one user story that carries it?

The stories connect the parts to what the users do, so every part can trace back to a step a user takes. Jeff Patton's user story mapping lays the steps of the main use along a backbone, and hangs a [user story](https://www.mountaingoatsoftware.com/agile/user-stories) on each.

1. *While deciding.* Open the README's walkthrough, and lay its steps in order as the backbone, with the steps of the main use of each objective that the walkthrough doesn't run.
2. *While deciding.* For each step, ask how the role meets the product at its edge there, such as a command they type, and write one story for each such way, naming the steps it carries.
3. *While deciding.* Read the product vision's intent, and add a story for each convenience it asks for, such as resuming a run that stopped.
4. *While making.* Go through each exchange of the README's walkthrough, and the main use of each objective it doesn't run, and name the one story that carries each step. Add a story where none does.

### N3

Does each principle, user story, component, and kind of data trace to what the README promises the users, or to a need of the product's development or operation?

A part that nothing needs costs effort to build and to keep, and gives no one anything.

1. *While deciding.* For each principle and each story, ask which step, doubt, or need it carries, from three sources. The README carries what the users get from the product vision: the steps of its walkthrough, and the doubts that its How it works answers. Development adds what the developers need to build, test, and change the parts. Operation adds what keeps the product working across runs and updates, such as where its work outlives a run.
2. *While making.* Once you have drawn Sequences, for each component and each kind of data, find the principle or the step of a sequence that reaches it.
3. *While making.* Remove whatever reaches none, from every figure, list, and sentence that names it.

### N4

Does each principle give a rule and a reason from which two developers decide a case that no line names the same way?

Developers of different parts meet the same kind of decision, and decide it apart unless a principle settles it.

1. *While deciding.* Derive the principles from the README's How it works, which answers each doubt of the users from an idea of the product vision's concept, and from the needs of development and operation.
2. *While deciding.* For each answer and each need, ask what every part must hold alike for it to come true, such as where the work's state lives. A part that held it otherwise would break a key result. Each thing that every part must hold alike is a principle.
3. *While deciding.* Leave out what a single component's line already says, since a principle holds only a rule that spans parts.
4. *While making.* For each principle, write the rule in one sentence, naming the parts as Components names them.
5. *While making.* Write the reason in one sentence: what goes wrong without the rule, for a role of the product vision, naming the key result it guards, or for the developers or the operators. A developer carries the reason to a case that the rule doesn't name.
6. *While making.* Where your cut names an architecture that the product builds on, point to its principles, and write only what this product adds or changes.
7. *While making.* Take a case that no rule names, and decide it from each reason as two developers of different parts would. Where they differ, sharpen the reason.

### N5

Does each decision that the stories need belong to exactly one component?

Two components that make the same decision make it twice, and the two copies drift apart. David Parnas's information hiding gives each module one decision that's hard to make or likely to change, and hides it from the rest.

1. *While deciding.* Walk each story's steps, and name who acts at each: the role, a part of the product, or a thing outside the product. Each part of the product that acts is a component, of a kind that the architecture the product builds on offers where it offers kinds, such as a skill, a hook, or a script of a Claude Code plugin.
2. *While deciding.* Take from the stories the decisions that are hard to make or likely to change, such as where the product keeps the work's state, or the form of a file that two parts share.
3. *While deciding.* Give each decision to the one component that holds what it decides on, such as the form of the work's state to the component that writes the state. Where no component holds it, make a component for it.
4. *While deciding.* Where another component needs the same decision, leave it with the component that holds it, and draw an arrow by which the other asks it, such as a hook that asks a script whether a step is done instead of reading the state itself.
5. *While making.* List under the figure what each component alone decides.
6. *While making.* Label each arrow with what one component does to another and the data it passes, not a word such as `uses`.

### N6

Does each component state its type and its technology?

A developer who doesn't know what kind of thing a component is, or what it's built with, chooses alone, and the components stop fitting. The [C4 model](https://c4model.com/diagrams/container) gives each box its name, its type, such as a script, a skill, or a folder of JSON files, and its technology.

1. *While deciding.* For each component, decide the type and the technology from the product's constraints, such as the runtime its users have.
2. *While making.* Copy the template's skeleton of the figure to the deliverable's own, and place the boxes in the order the main story reaches them, left to right, so that its arrows run one way and cross no other.
3. *While making.* Draw a store of data as a box like a component's, since its type sets it apart.
4. *While making.* Give the figure a legend for every symbol.
5. *While making.* Read the figure without the text around it, and add to the legend whatever symbol a reader would still have to ask about.

### N7

Does the data model show how each kind of data relates to the others, without its fields?

Two developers who build the writer and the reader of the same data must join it to the other data in the same way, while its fields stay free to change. A concept model in a class diagram of the Unified Modeling Language (UML), which most developers read, shows this.

1. *While deciding.* Walk each story's steps and each arrow that Components draws, and list each kind of data that one component hands to another or that a store keeps, by the name the README gives it where it gives one, such as a run's record.
2. *While deciding.* For each pair that relates, name the relation, and give how many of each it joins at both ends, such as a run that holds one or more rounds.
3. *While making.* Draw each once, as a class by its name alone.
4. *While making.* Where one holds the other's parts, put a filled diamond at the whole, since readers take a hollow one in different ways.
5. *While making.* Group the data in a frame for each component or store that keeps them, in the order the stories meet them, with the data that most others join in the middle.
6. *While making.* Leave the fields to where the developer builds the data.
7. *While making.* Below the figure, say in a few words what a kind of data is only where a reader could take its name for another's.

### N8

Does each user story have a sequence that shows, at each step, which component acts, along which arrow, and with which data?

A developer building a step must know who acts there, on what, and what comes next. A [UML](https://www.omg.org/spec/UML) sequence diagram draws a story's steps in order, from the role's first request to what the story gives them.

1. *While making.* For each story, draw each step as a message from one component to another along an arrow of Components, with the data it passes, named as in the data model.
2. *While making.* At each step, ask what can go otherwise there, from the README's walkthrough and from what each component alone decides: an input that a component refuses, a check that fails, or a choice that only the role can make, such as a question that the walkthrough shows the role answering.
3. *While making.* Draw an input refused as a branch, a check that fails as a step that sends work back to the step it repeats, and a choice of the role as a question put to the role with its answers, since each path of the story, and its integration test, rests on them.
4. *While making.* Let stories that share their steps share a diagram.
5. *While making.* Read each sequence as the developer who builds one of its steps, and check that they can tell, at each step, which component acts, along which arrow of Components, with which data, and what comes next. Where no arrow carries a step, add the arrow, or give the step to another component.

### N9

Do the figures, lists, and sentences agree with one another, and with the architecture that the product builds on, on what each part does?

A developer who finds two places that say different things about a part must choose which to follow, and two developers choose differently.

1. *While making.* For each part, gather what every figure, list, and sentence says it does, and, where your cut names an architecture that the product builds on, what each of its rules asks of a part of that kind, such as a rule that every hook gives its result as JSON.
2. *While making.* Where two disagree, decide by the reasons of the principles and of those rules which is right, and change the other.

### N10

Does Deployment show where each component runs, where the product keeps each kind of data, and how the product starts?

A developer setting up the product needs to know where each part runs, what it can reach, and how it starts. A [C4 deployment diagram](https://c4model.com/diagrams/deployment) shows this.

1. *While deciding.* List each environment the product runs in, such as the user's computer or CI, with its technology.
2. *While deciding.* Place each component and each kind of data in one deployment unit within its environment, such as the plugin's folder that the host installs, or the run's folder in the user's repository.
3. *While deciding.* Add each thing outside the product that the components depend on, with what they use of it, and no infrastructure that they don't need.
4. *While making.* Write in one sentence how the product starts.
5. *While making.* Check that a developer could set the product up from nothing by the figure and that sentence.

### N11

Does each component and each kind of data have one place for its files?

A developer making a change must find the one place it belongs. Simon Brown's package by component, in Robert C. Martin's *Clean Architecture*, lays out the code by the components that the architecture draws.

1. *While deciding.* Lay out the folders by component, so that each component and each kind of data has its own place, such as a folder for the hooks and one for the code they call.
2. *While making.* Say in one sentence for each top folder whom its files are for, such as the users who install the product or only its developers.
3. *While making.* Show each folder and file that holds a component or a kind of data, by its real name, one line each, nested as on disk, without the files inside a component.
4. *While making.* Beside each, say what it does or holds, in the words a developer looks for when making a change.
5. *While making.* Check that, for any change to a component, a developer can name the one folder it goes in.

### N12

Does Test strategy decide the types of testing of each target, every type of code and test quality for the parts and those the key results call for in the product vision's, and, for each test level, what it tests, what runs real, its tools, when it runs, and each quality check with the criterion by which it passes?

A case's pass or fail decides the work only where the developers set its level's tools and criteria before anyone writes the case, and a failure that no type of testing looks for reaches the users unseen.

1. *While deciding.* Name the levels unit tests, integration tests, and end-to-end (E2E) tests, and use no other name for a test. Unit tests try each part, each prompt among them, against its contract. Integration tests try the parts joined against each element of this document. E2E tests try the product in real use against each key result of the product vision.
2. *While deciding.* For each level, run real only what it tests, and replace the rest with [test doubles](https://martinfowler.com/bliki/TestDouble.html). At unit, run the part, with a double for each part it works with that's slow or outside the test. At integration, run what joins the components, such as hooks and scripts, with a double for each component that an AI runs and for each thing outside the product, so that the level calls no model and gives the same result on each run. At E2E, run the whole product on the model its users run, with an AI in the role that holds an intent the product never receives, since another model makes other mistakes than the users meet.
3. *While deciding.* Read [the list of test types](test-types.md) to its end. The trace: `${CLAUDE_PLUGIN_ROOT}/domain/best-practices/architecture/test-types.md` read to its end.
4. *While deciding.* For the parts, take every type that the list gives under code quality and test quality, and, for each part that holds a prompt, every type under a prompt's evaluation, since each looks at every part alike, and a fault that one of them would show costs a key result wherever it lands.
5. *While deciding.* Set the criterion of each type that the parts took. Take it from the architecture that the product builds on where that sets one. Else take the strictest that every part can meet once each line answers a case one level up: every line and branch covered, no mutant left alive, the default limits of the complexity and lint tools, and no finding of static analysis or lint. Where a line can't meet it, mark the line with why, since a check without a criterion passes whatever it finds.
6. *While deciding.* Name each contract that takes a wide input, one that another program or an AI writes, such as the reader of a file that an AI writes, for property-based tests that find no counterexample, and leave the other contracts to the cases drawn by hand.
7. *While deciding.* Set k, how many times a prompt's unit tests run each case on the model its users run, passing a case only where all k runs pass, as pass^k of Anthropic's [demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) measures it. Take r, the number of runs a user makes before a slip would cost them a key result, such as the runs of one session, and set k to 2.3 times r, rounded up, so that a slip once in r runs shows in the k runs nine times in ten, such as k of 7 for r of 3.
8. *While deciding.* Set the quality checks of the architecture, and name the script that checks them by the names of the elements, not by reading: every element of this document, each story, principle, component, and kind of data, has an integration test; every test names an element or a case one level up that exists; every unit case names an integration case; a test of a principle that must not break is trusted only once seen to fail with the principle broken; and each double gives only what a recorded run or the official documentation shows, as N14 says.
9. *While deciding.* For each key result of the product vision, ask of each type that the parts didn't take whether, without it, the key result could worsen and no check would show it, given what the product is and what it builds on, such as compatibility with a new version of the host where the host changes on its own schedule. Keep each type where it could, and drop the rest, since testing every type that could apply is the trivial many. Leave out functional testing, which every level's cases try, as N13 says.
10. *While deciding.* For each type kept, write the key result it guards as its reason, and the lowest level at which what it looks at runs real, such as E2E for the time a main use takes.
11. *While deciding.* Set the criterion of each type kept only as far as the failure it guards calls for, such as no main use slower than in the last run, in place of a fixed time that no key result asks for.
12. *While deciding.* Where you keep compatibility with a new version of what the product builds on, set its check at the integration level, whose doubles it keeps true: on each new version of the thing outside the product, run again the steps that made each recorded run, and compare what the real thing gives with what each double gives, passing only where they agree. This is Martin Fowler's [contract test](https://martinfowler.com/bliki/ContractTest.html), which runs against the real thing apart from the work.
13. *While deciding.* Where a double rests on a page of documentation and not on a recorded run, add to that check that the page still shows the words the double rests on.
14. *While deciding.* Decide what the developers do where that check fails: record the new version's run, change the double to give what the run shows, and fix the product where a test then fails, since a double that the real thing has outgrown passes a test that its users' version fails.
15. *While deciding.* Set the check of each key result: compare its value with the last run's by the order the product vision gives, and pass where it's no worse, since the product vision sets no target.
16. *While deciding.* Where an AI judges a key result, trust the judge only once it's right on every kept record whose answer you know.
17. *While deciding.* Set how many times each E2E test runs its main use at real size by the rule that N12.7 gives k, from how many main uses a user runs before a slip would cost a key result, since the AI's variance shows only across runs.
18. *While deciding.* Choose each level's tools from the product's constraints, such as the runtime its users have, and name each: the test runner, and the tool of each check, such as pytest for a product in Python.
19. *While deciding.* Run before each push the static analysis, the unit tests of code, and the integration tests that the change reaches, with their coverage, since these show whether the change does what its design says, and the work waits on them. Running every such test there meets this too, as a selection by what the change reaches misses a test that reads a file the change edits.
20. *While deciding.* Run on each push, in CI, every unit test of code and every integration test, and mutation testing and property-based tests over the lines that the push changed, apart from the work, since these check the tests and not the change.
21. *While deciding.* Run each night, in CI, every check that runs on its own over the whole, property-based tests at their most inputs among them, since a run over a push's lines misses a test changed alone and a fault between parts that no one push changed together.
22. *While deciding.* Run the compatibility check of each double on each new version of the thing outside the product, which a job in CI finds each night by its version, since only a new version changes what the double must give.
23. *While deciding.* Run a prompt's unit tests before a change of the prompt is taken, since each run calls the model and is slow and costly.
24. *While deciding.* Run the E2E tests once every lower level passes, since each run calls the model and is slow and costly.
25. *While making.* Write a subsection for each level, from unit to E2E, in the form of the template.
26. *While making.* Where your cut names an architecture that the product builds on, point to its test rules, such as the form each case takes, and write only what this product sets.

### N13

Does each part have its skeleton, and every part, every element of this document, and every key result its test cases in the test code, each written as Given, When, and Then through that skeleton, and each naming the case or the element one level up that it supports?

Every case written through a skeleton of the parts before any body is built checks the architecture while a gap between the parts is still cheap to fix: a case that no part can hold, or a handoff that no interface carries, shows the gap before anyone builds around it. Steve Freeman and Nat Pryce's outside-in test-driven development, in [Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/) and [Mock Roles, not Objects](http://jmock.org/oopsla2004.pdf), finds each part's roles and interface by first writing the tests one level up. A case finds a gap only where it calls a real interface, and the skeleton is code, apart from this document, which keeps no part's internals.

1. *While making.* Once Test strategy names the tools, make the skeleton of each module where Directory structure places it, from the arrows and the data that Sequences hand to it: a file whose docstring names the decision it alone makes, and, for each arrow it takes, an interface whose signature and docstring state what it takes, what it gives, and what it refuses, each body left empty, such as one that raises `NotImplementedError`.
2. *While making.* Where a part holds a prompt, make its skeleton where Directory structure places it: a file with its description, which says when to use the prompt and what it gives, and the form of what it takes and gives, such as a JSON Schema, its steps left empty.
3. *While making.* Write the E2E cases first: for each key result, a case that runs an objective's main use, as the README's walkthrough shows it, at the size of a real request, and names the key result, such as `KR1.1`.
4. *While making.* Write the integration cases from the elements of this document, each naming its element by its name: a case for each path through each story's sequence, the main flow, each branch, each step that sends work back, and each question put to the role, until every move from one step to the next lies on some path; a case for each principle, where the parts keep it and where one breaks it; a case for each decision that a component alone makes; and a case for each handoff between parts, with the data it passes as the data model names it, until each kind of data lies on some case.
5. *While making.* Write the unit cases of each part through its interface, each naming the integration case it supports, so that the interface a part offers comes from what the cases one level up need of it, and change the skeleton where a case needs an interface it lacks or calls none it offers.
6. *While making.* Divide each input and each result that a part's contract names into classes that the part treats alike, the refused ones among them, and write one case for each class. This is equivalence partitioning, as the ISTQB glossary defines it.
7. *While making.* Where a class ends on an ordered scale, such as a length or a count, write one case at each end and one at the nearest value of the next class. This is boundary value analysis.
8. *While making.* Where the contract's result depends on a combination of conditions, write one case for each combination that can occur, with the result it gives. This is decision table testing.
9. *While making.* For a prompt, write a case where its contract says it acts and one where it says it doesn't, for each kind of request it's for, and decide by code each point of the result that its record shows.
10. *While making.* Write each case as a test in the test code, in the place that Directory structure names, with its Given, When, and Then stated, and write no list of the cases in a document, since a list beside the code says each case twice.
11. *While making.* Run the type checker over the skeleton and the cases, and see every case fail: a type that doesn't fit across a handoff is a gap between the parts, and a case that passes on an empty body tests nothing.
12. *While making.* Read the cases and the skeleton against the architecture, and list each gap they show: a case that no part can hold; a part that no case reaches; a module that can't state its decision in a few words; a part whose cases change for more than one reason, such as a file's form and a remote's commands; and a handoff that no interface carries.
13. *While making.* For each gap, change the architecture first: give the case a part, or a decision to a part; remove the part that no case reaches, as N3 says; split the module or the part by its decisions or its reasons to change; and give the handoff an arrow and a kind of data.
14. *While making.* Then change the skeleton and the cases to the architecture.
15. *While making.* Run the script that checks the trace, and mend each case or element it names until it names none. The script finds only a name that leads nowhere, so its 0 shows no more than that: whether the cases are enough, and whether the parts are cut right, the reading before it judges.

### N14

Does each thing that the document says the product does rest on a part that a unit or integration test can check?

The E2E tests are slow and few, so they can only confirm what the lower levels already showed, and a thing that only a prompt holds varies from run to run, where only many runs on the model show it. The [Humble Object](https://martinfowler.com/bliki/HumbleObject.html) pattern of Gerard Meszaros's *xUnit Test Patterns* moves the logic out of a part that's hard to test into a part that a test can run.

1. *While deciding.* For each thing the document says the product does, name the part that holds it.
2. *While deciding.* Where only a prompt holds a rule that must hold on every run, give the rule to a part that a test can run, such as a guard of the architecture the product builds on, and draw that part in Components.
3. *While deciding.* Leave a judgment that only an AI can make, such as whether a point is the user's, with the AI, and try it by the prompt's unit tests on the model, as N12.7 sets.
4. *While making.* The lower levels show a part only if each double behaves like the part it replaces, so give each double only results in the form the part's contract gives, refusals among them.
5. *While making.* Test each double as the part's unit tests test the part.
6. *While making.* Draw a double of something outside the product from its documentation or from a recorded run of the real thing, and name that source beside what the double gives, so that the script of N12.8 can check it. A double that gives what the real thing never would passes a test that the real one fails.
7. *While making.* Trust a check, such as a test, a hook, or the judge of an E2E test, only once you have seen it fail on a case that breaks what it checks, such as a test of a principle run with the part that holds the principle taken out, which the script of N12.8 can run. Trust a judge once it's right on kept records whose answer you know.

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
