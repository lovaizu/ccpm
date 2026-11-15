# `architecture`

## Goal tree

- The developers build and change the parts of the product so that together they deliver what the README promises the users.
  - **C1** The developers know what each part must do, for the users or for the product's development and operation, and why.
    - **N1** Does Solution strategy state first the one idea by which the product delivers what its README promises? (Solution strategy)
    - **N2** Does each user story state what a role wants, in the role's words and without the product's means, and do the stories together cover each objective of the product vision and each promise of the README? (User stories)
    - **N3** Does each rule of Solution strategy, user story, component, and kind of data trace to what the README promises the users, or to a need of the product's development or operation? (Solution strategy, User stories, Components, Data model, Sequences)
  - **C2** Parts that different developers build fit together.
    - **N4** Does each rule of Solution strategy give a rule and a reason from which two developers decide a case that no line names the same way? (Solution strategy)
    - **N5** Does each component state its responsibility, and does each decision that the stories need belong to exactly one component? (User stories, Components)
    - **N6** Does each component state its type and its technology? (Components)
    - **N7** Does the data model show how each kind of data relates to the others, without its fields? (Data model)
    - **N8** Does each user story have a sequence that shows, at each step, which component acts, along which arrow, and with which data? (User stories, Components, Data model, Sequences)
    - **N9** Do the figures, lists, and sentences agree with one another, and with the architecture that the product builds on, on what each part does? (the whole)
  - **C3** The developers can place, set up, and start every part without asking anyone.
    - **N10** Does Deployment show where each component runs, where the product keeps each kind of data, and how the product starts? (Components, Data model, Deployment)
    - **N11** Does each component and each kind of data have one place for its files? (Components, Data model, Directory structure)
  - **C4** The developers find each gap between the parts before they build any part, and know, as they build, that the product does what the document and the product vision say.
    - **N12** Does Test strategy give only the test types that the product's purpose needs, picked from the test strategy guide, each with its test target, and for a quality its tool and criterion, or for a benchmark its tool and what it measures? (Test strategy)
    - **N13** Does each part have its skeleton, and every part, every element of this document, and every key result its test cases in the test code, each written as Given, When, and Then through that skeleton, and each naming the case or the element one level up that it supports? (Test strategy)
    - **N14** Does each thing that the document says the product does rest on a part that a unit or integration test can check? (Components, Test strategy)
  - **C5** The developers can change the product without making the document wrong.
    - **N15** Does each view give each decision that a key result rests on, with its intent? (Components, Data model, Sequences, Deployment, Directory structure)
    - **N16** Does the document hold only what stays true while the product vision and Solution strategy stay, and leave each component's internals out? (the whole)

## Template

[template.md](template.md)

## Inputs

- [product-vision](../product-vision/best-practice.md)
- [readme](../readme/best-practice.md)

## Practices

### N1

Does Solution strategy state first the one idea by which the product delivers what its README promises?

Each view carries out one idea, and a developer who knows the idea builds a part that serves it. The [solution strategy](https://docs.arc42.org/section-4/) of arc42 sums up first the few decisions that shape the whole.

1. *While deciding.* Open your cut, and read to its end each input it names: the product vision, the README, and, where the product builds on another's rules, the architecture it builds on, such as a guide to building a plugin of the host it runs in. The trace: `{inputs}` read to its end.
2. *While deciding.* In the README's How it works, take the first way it states, from the product vision's concept, by which the product brings its users to their objectives, such as keeping every decision of a run in one file that each role reads.
3. *While deciding.* Ask how the system as a whole makes that way work: what it takes in from the roles, and what it turns that into, such as a request typed in a session turned into a deliverable that passed its checks.
4. *While making.* Write the answer in two or three sentences that a developer can hold in mind while building any part. Point to the README instead of repeating it, and put it first in Solution strategy, before the rules that follow from it.
5. *While making.* After writing the rest, read each component's line as a developer who knows only the idea, and check that they can see which piece of the idea it carries out. Change the idea or the component where they can't.

### N2

Does each user story state what a role wants, in the role's words and without the product's means, and do the stories together cover each objective of the product vision and each promise of the README?

The stories are the product's requirements: what each role wants, which the views then meet. A story that names a means, such as a command, states a design as a want, so no one asks whether the design serves the want. A [user story](https://www.mountaingoatsoftware.com/agile/user-stories) doesn't prescribe the solution, which the conversation and the acceptance criteria settle. Jeff Patton's [user story mapping](https://jpattonassociates.com/wp-content/uploads/2015/03/story_mapping.pdf) lays the role's activities along a backbone at one goal level, and hangs the stories on them, so a story covers what the use needs, not one step each.

1. *While deciding.* Open the product vision and the README, and list each objective and each promise the README makes, in its walkthrough, its Non-goals, and its How it works.
2. *While deciding.* For each objective, lay out as its backbone the activities its role does from where they start to the result they keep, read from the README's walkthrough for its main use. Name each in the words the role would say, such as approving the plan. A command or a screen of the product is no activity.
3. *While deciding.* For each activity, ask what the role wants there and why, and write it as a story in the role's words, without a command, a screen, or a part of the product, since Sequences shows how the product meets it. One want often serves several activities, such as giving yes or a change at each sign-off.
4. *While deciding.* Keep each story at the level of a goal the role reaches in one sitting, such as approving a deliverable, not a step within it, such as reading its changes, since stories at mixed levels leave gaps and overlaps that no one sees.
5. *While deciding.* Read each idea of the product vision's Concept, and ask at which moment of the use it keeps the one way holding. Where the role wants something there that no story carries, add a story for it, such as going on with a run that stopped.
6. *While deciding.* Where the product's development or operation wants something of the product, such as a release, write a story with the developer or the operator as its role.
7. *While making.* For each objective and each promise, name the stories that carry it, and add a story where none does. Leave an activity without a story of its own where another story already carries it.
8. *While making.* Read each story and ask whether it still holds where the product met it another way, such as a reply in place of a command. Rewrite each that doesn't, as it names a means, not a want, unless the role wants that means itself, such as working within the tool they already use.

### N3

Does each rule of Solution strategy, user story, component, and kind of data trace to what the README promises the users, or to a need of the product's development or operation?

A part that nothing needs costs effort to build and to keep, and gives no one anything.

1. *While deciding.* For each story, ask which activity, doubt, or need it carries, from three sources. The README and the product vision carry what the users get: the objectives and the promises that N2 lists, and the doubts that the README's How it works answers. Development adds what the developers need to build, test, and change the parts. Operation adds what keeps the product working across runs and updates, such as where its work outlives a run.
2. *While making.* Once you have written Solution strategy, for each rule, name the doubt of the README's How it works, or the need of development or operation, that it carries.
3. *While making.* Once you have drawn Sequences, for each component and each kind of data, find the rule or the step of a sequence that reaches it.
4. *While making.* Remove each story or rule that carries none, and each component or kind of data that none reaches, from every figure, list, and sentence that names it.

### N4

Does each rule of Solution strategy give a rule and a reason from which two developers decide a case that no line names the same way?

Developers of different parts meet the same kind of decision, and decide it apart unless a rule that every view follows settles it.

1. *While deciding.* Derive the rules from the README's How it works, which answers each doubt of the users from an idea of the product vision's concept, and from the needs of development and operation.
2. *While deciding.* For each answer and each need, ask what every part must hold alike for it to come true, such as where the work's state lives. A part that held it otherwise would break a key result. Each thing that every part must hold alike is a rule of Solution strategy.
3. *While deciding.* Leave out what a single view already says, since a rule of Solution strategy holds only what spans the views.
4. *While making.* For each rule, write it in one sentence, naming the parts as Components names them.
5. *While making.* Write the reason in one sentence: what goes wrong without the rule, for a role of the product vision, naming the key result it guards, or for the developers or the operators. A developer carries the reason to a case that the rule doesn't name.
6. *While making.* Where your cut names an architecture that the product builds on, point to its rules, and write only what this product adds or changes.
7. *While making.* Take a case that no rule names, and decide it from each reason as two developers of different parts would. Where they differ, sharpen the reason.

### N5

Does each component state its responsibility, and does each decision that the stories need belong to exactly one component?

Two components that make the same decision make it twice, and the two copies drift apart. David Parnas's information hiding gives each module one decision that's hard to make or likely to change, and hides it from the rest.

1. *While deciding.* Walk each story's steps, and name who acts at each: the role, a part of the product, or a thing outside the product. Each part of the product that acts is a component, of a kind that the architecture the product builds on offers where it offers kinds, such as a skill, a hook, or a script of a Claude Code plugin.
2. *While deciding.* Take from the stories the decisions that are hard to make or likely to change, such as where the product keeps the work's state, or the form of a file that two parts share.
3. *While deciding.* Give each decision to the one component that holds what it decides on, such as the form of the work's state to the component that writes the state. Where no component holds it, make a component for it.
4. *While deciding.* Where another component needs the same decision, leave it with the component that holds it, and draw an arrow by which the other asks it, such as a hook that asks a script whether a step is done instead of reading the state itself.
5. *While making.* Write under the figure each component's responsibility in one sentence: what the others expect it to do, the decisions it holds among it, such as `renders each page and sends what the user enters to the API`, so that a developer knows what to build and what to leave to the others.
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
2. *While making.* Where two disagree, decide by the reasons of the rules of Solution strategy and of those of the architecture it builds on which is right, and change the other.

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

Does Test strategy give only the test types that the product's purpose needs, picked from the test strategy guide, each with its test target, and for a quality its tool and criterion, or for a benchmark its tool and what it measures?

A failure that no test looks for reaches the users unseen, and a case's pass or fail decides the work only where its criterion is set before anyone writes it. Where a result varies from run to run, as a prompt's does, a criterion passes or fails by chance, so a benchmark measures it and a person decides. A row for every type of the guide decides nothing for most of them, so Test strategy holds only the types the product's purpose needs.

1. *While deciding.* Read [the test strategy guide](test-strategy-guide.md) to its end. The trace: `${CLAUDE_PLUGIN_ROOT}/domain/best-practices/architecture/test-strategy-guide.md` read to its end.
2. *While deciding.* Take each type's test target from the guide. Unit tests try the parts against their contracts, each prompt among them. Integration tests try the parts joined against each element of this document. End-to-end (E2E) tests try the product in real use against each key result of the product vision. Use no other name for a test, so that each case's level tells which target it checks.
3. *While deciding.* Pick a type only where, without it, a key result could worsen and no type picked would show it, given what the product is and what it builds on, such as compatibility with a new version of a host that changes on its own schedule. Unit, integration, and scenario testing, and traceability, pass this for every product, as the cases of N13 rest on them. Write no row for a type left out.
4. *While deciding.* Make each type a benchmark where its test's path runs a prompt, as the guide's rule says, and each other type as the guide gives it.
5. *While deciding.* For each type the product runs, choose its tool from the product's constraints, such as the runtime its users have, and name it.
6. *While deciding.* Take each quality's criterion that the guide recommends, or the one that the architecture the product builds on sets. Change it only where the product can't meet it, or a key result needs more, and say why in the row.
7. *While deciding.* For each benchmark, name what it measures, such as a key result or the share of a prompt's runs that are right, and what it compares the value with, such as the last version's. Set no criterion, as the person who decides the change reads it.
8. *While deciding.* Set how many times a benchmark runs each case by its first runs: add runs until one more no longer moves the measure by a step, such as one case or one question answered, since the AI's variance shows only across runs. Where the product can't run yet, write this rule in place of the number, for the first run to set it.
9. *While deciding.* For the trace of the architecture, set as the criterion that every element of this document, each story, rule, component, and kind of data, has an integration test, and that every test names an element or a case one level up that exists. Name the script that checks this by the names of the elements, not by reading, since only a check by name finds each element that no test reaches.
10. *While deciding.* Where an AI judges a key result, trust the judge only once it's right on every kept record whose answer you know.
11. *While making.* Write one row for each type picked, in the guide's order, in the template's table of qualities or of benchmarks.

### N13

Does each part have its skeleton, and every part, every element of this document, and every key result its test cases in the test code, each written as Given, When, and Then through that skeleton, and each naming the case or the element one level up that it supports?

Every case written through a skeleton of the parts before any body is built checks the architecture while a gap between the parts is still cheap to fix: a case that no part can hold, or a handoff that no interface carries, shows the gap before anyone builds around it. Steve Freeman and Nat Pryce's outside-in test-driven development, in [Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/) and [Mock Roles, not Objects](http://jmock.org/oopsla2004.pdf), finds each part's roles and interface by first writing the tests one level up. A case finds a gap only where it calls a real interface, and the skeleton is code, apart from this document, which keeps no part's internals.

1. *While making.* Once Test strategy names the tools, make the skeleton of each module where Directory structure places it, from the arrows and the data that Sequences hand to it: a file whose docstring names the decision it alone makes, and, for each arrow it takes, an interface whose signature and docstring state what it takes, what it gives, and what it refuses, each body left empty, such as one that raises `NotImplementedError`.
2. *While making.* Where a part holds a prompt, make its skeleton where Directory structure places it: a file with its description, which says when to use the prompt and what it gives, and the form of what it takes and gives, such as a JSON Schema, its steps left empty.
3. *While making.* Write the E2E cases first: for each key result, a case that runs an objective's main use, as the README's walkthrough shows it, at the size of a real request, and names the key result, such as `KR1.1`.
4. *While making.* Write the integration cases from the elements of this document, each naming its element by its name: a case for each path through each story's sequence, the main flow, each branch, each step that sends work back, and each question put to the role, until every move from one step to the next lies on some path; a case for each rule of Solution strategy, where the parts keep it and where one breaks it; a case for each decision that a component alone makes; and a case for each handoff between parts, with the data it passes as the data model names it, until each kind of data lies on some case.
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
15. *While making.* Make the script that checks the trace, which N12.9 names, beside the test code where Directory structure places it, so that it finds each element by where the template puts its name, such as each story by its `S<n>` and each key result by its `KR<n>.<m>`, finds each case by the name it gives of what it supports, and checks each rule that N12.10 sets. Where the architecture the product builds on keeps such a script, such as one that a guide to building plugins runs on every plugin, run that one on this product instead, and add only the checks it lacks.
16. *While making.* Run the script that checks the trace, and mend each case or element it names until it names none. The script finds only a name that leads nowhere, so its 0 shows no more than that: whether the cases are enough, and whether the parts are cut right, the reading before it judges.

### N14

Does each thing that the document says the product does rest on a part that a unit or integration test can check?

The E2E tests are slow and few, so they can only confirm what the lower levels already showed, and a thing that only a prompt holds varies from run to run, where only many runs on the model show it. The [Humble Object](https://martinfowler.com/bliki/HumbleObject.html) pattern of Gerard Meszaros's *xUnit Test Patterns* moves the logic out of a part that's hard to test into a part that a test can run.

1. *While deciding.* For each thing the document says the product does, name the part that holds it.
2. *While deciding.* Where only a prompt holds a rule that must hold on every run, give the rule to a part that a test can run, such as a guard of the architecture the product builds on, and draw that part in Components.
3. *While deciding.* Leave a judgment that only an AI can make, such as whether a point is the user's, with the AI, and measure it by the prompt's unit tests on the model, as N12.8 sets.
4. *While making.* The lower levels show a part only if each double behaves like the part it replaces, so give each double only results in the form the part's contract gives, refusals among them.
5. *While making.* Test each double as the part's unit tests test the part.
6. *While making.* Draw a double of something outside the product from its documentation or from a recorded run of the real thing, and name that source beside what the double gives, so that the script that N13.15 makes to check the trace can check it. A double that gives what the real thing never would passes a test that the real one fails.
7. *While making.* Trust a check, such as a test, a hook, or the judge of an E2E test, only once you have seen it fail on a case that breaks what it checks, such as a test of a rule run with the part that holds the rule taken out, which the script that N13.15 makes to check the trace can run. Trust a judge once it's right on kept records whose answer you know.

### N15

Does each view give each decision that a key result rests on, with its intent?

A developer who doubts a decision and can't see what it was for may undo it and bring back the problem it solved. An [architecture decision record](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), by Michael Nygard, keeps a decision with its context, and its intent is what a developer needs to keep it.

1. *While deciding.* For each view, take each decision that a key result rests on, such as a technology, a tool, or the form of a file that two parts share, and ask why it's taken, ending with the key result it serves.
2. *While making.* Write each under its view's Strategies: the decision in a few words, and its intent in one sentence.
3. *While making.* Leave out a decision that no key result rests on, since its intent gives a developer nothing to keep.

### N16

Does the document hold only what stays true while the product vision and Solution strategy stay, and leave each component's internals out?

A line about how a component works inside becomes untrue at the next change to that component, and the developer then can't trust the document. David Parnas's [information hiding](https://doi.org/10.1145/361598.361623) keeps such details inside the module.

1. *While making.* For each line, ask whether it would become untrue if a component's internals changed while the product vision and Solution strategy stayed.
2. *While making.* If it would, move it to where the developer builds the component.
3. *While making.* Imagine a change to how a component works inside, such as its steps, a value it uses, or a data's fields, and mark each line it would make untrue. Repeat with a change of another kind until you mark no line.
