# `architecture`

## Goal

The developer builds and changes each part of the product on its own, and the parts together give its product vision.

## Template

[template.md](template.md)

## Example

[examples](examples)

## Inputs

- [product-vision](../product-vision/best-practice.md)
- [readme](../readme/best-practice.md)

## Intents

| ID | About | Question |
| --- | --- | --- |
| Q1 | Drivers | Choosing between structures, does the developer find each use case the product carries and each quality it must have, each quality said as a scenario with a measure, so that each part is there for a driver and the drivers decide between structures? |
| Q2 | Structure | Starting on a part, does the developer find it as one element at one level of abstraction, a container that runs code or keeps data or a component inside one, with its type, its technology, the one responsibility it holds, and where its files lie, so that they build it on its own and a change of one responsibility lands in one element? |
| Q3 | Dependencies | Adding a dependency between two parts, does the developer find which part may depend on which, the core on nothing outside it and each outside thing reached through a port at its edge, stated where a machine checks it on each change, so that a change of the outside stays in one adapter and the core runs whole in a test? |
| Q4 | Interfaces | Making a part that hands data to another, do the developers of both sides find what crosses, its form, which side owns that form, and where its contract lies, with each data named alike in every view, so that the parts join without either reading the other's code? |
| Q5 | Runtime | Following a use case from its role's first request to its end, does the developer see at each step which element acts, along which relation, with which data, and each branch, so that they build each step knowing who acts on what? |
| Q6 | Deployment | Setting the product up from nothing, does the developer find where each container runs and where it keeps each data, what each environment gives it, each outside thing it uses, and how it starts, so that they need ask no one? |
| Q7 | the opening, Decisions | Doubting a choice, or meeting a case no line names, does the developer find the idea the parts carry out, the rules every part follows with their reasons, and for each decision its context, the options it beat, and its consequences, so that they keep, change, or extend it knowing what it was for? |
| Q8 | the whole | Changing how a component works inside while the drivers stay, does the developer find every line of the architecture still true, so that the architecture changes only with its drivers and its structure, and its readers trust it? |
| Q9 | Tests | Testing a part or a path, does the developer find for each level what it checks against, what runs real, where doubles stand in and what keeps each true to what it stands for, and when the level passes, with each case at the lowest level that can catch it, so that a failing test points to one part or one path and the slow levels stay few? |
| Q10 | Runtime, Tests | Before writing the code of a use case, does the developer find a test for each path through its runtime view at the level that joins the parts, so that they build the parts to join as the architecture says and see when they do? |
| Q11 | the whole | With only the architecture and what it rests on, can a developer new to the product build a part in its place, test it at each level, and have it join the others, meeting each element under one name in every view? |

## Practices

### Q1

Choosing between structures, does the developer find each use case the product carries and each quality it must have, each quality said as a scenario with a measure, so that each part is there for a driver and the drivers decide between structures?

**Name**

Quality attribute scenarios, also known as architecturally significant requirements, architecture drivers, and utility tree

**Thinking**

List the drivers before any structure. Take a use case for each way a role meets the product at its edge, from the product vision and the README, such as a command typed or a page opened, each naming the steps of the README's walkthrough it carries. Write each quality the product must have as a scenario of six parts: the source, the stimulus, the environment, the part it reaches, the response, and the measure that judges the response, such as "a developer adds a kind of rule, and the change touches one component and its tests." A quality named alone, such as maintainable or fast, gives a structure nothing to meet, as every system is modifiable for some changes and not for others. Take the qualities from what the product vision asks, and from the developer's own needs, most of all how the product changes and how its tests run. These decide its structure, and no user names them. Rank the scenarios by what each is worth and the effort it takes to meet, and weigh each structure the document chooses by those at the top. Trace each element, relation, and data of the document to the use cases and scenarios that need it, and take out what none needs.

**Applies**

Every architecture, before its structure, and again when the product vision or the README changes.

**Excludes**

A requirement that shapes no structure, such as the wording of a message, is no driver. The part that holds it keeps it.

**Cost**

The scenarios take thought before any structure, and each measure must be one someone can check. A measure set higher than the product vision needs costs structure that nobody uses.

**Sources**

- [Bass, Clements and Kazman, Software Architecture in Practice, second edition, section 4.3, Quality Attribute Scenarios](https://people.ece.ubc.ca/matei/EECE417/BASS/ch04lev1sec3.html)
- [arc42, section 10, Quality Requirements](https://docs.arc42.org/section-10/)
- [ADR GitHub organization, Architectural Decision Records](https://adr.github.io/)

**Steps**

1. Read each input whole, the product vision and the README, before you list the drivers. The trace: `{inputs}` read to its end.

### Q2

Starting on a part, does the developer find it as one element at one level of abstraction, a container that runs code or keeps data or a component inside one, with its type, its technology, the one responsibility it holds, and where its files lie, so that they build it on its own and a change of one responsibility lands in one element?

**Name**

C4 model, also known as levels of abstraction, hierarchical decomposition, and building block view

**Thinking**

Describe the product at one level of abstraction at a time. Its context holds the people and the systems outside it that it meets. Its containers each run code or keep data, such as a command, a hook script, a service, or a folder of files. Inside each container that holds more than one decision likely to change, its components each group code behind one interface. Draw each level as a figure of its own, as a figure that sets a person, a process, and a module side by side shows neither how the product runs nor how its code divides. Give each element its type, its technology, and the one responsibility it holds in a few words, and give each figure a legend for every symbol. Give a component one decision to hide, such as a data format or how the product talks to another program, as a component that holds a list of unrelated decisions changes for each of them and grows until no one reads it whole. Split an element whose responsibility takes an "and" to say. Name where each element's files lie, so that a change lands in one place. Stop at the component, as the modules and functions inside one are its code's, which the code best practice divides.

**Applies**

Every product. The component level applies to each container that holds more than one decision likely to change.

**Excludes**

A container that holds one decision, such as a script of a few lines, needs no component level.

**Cost**

Each level is a figure to keep true, and where a component ends takes thought that the code would otherwise take later, at a higher price.

**Sources**

- [Brown, The C4 model for visualising software architecture](https://c4model.com/)
- [Brown, C4 model, Container](https://c4model.com/abstractions/container)
- [Brown, C4 model, Component](https://c4model.com/abstractions/component)
- [Brown, C4 model, Notation](https://c4model.com/diagrams/notation)
- [arc42, Overview](https://arc42.org/overview)

### Q3

Adding a dependency between two parts, does the developer find which part may depend on which, the core on nothing outside it and each outside thing reached through a port at its edge, stated where a machine checks it on each change, so that a change of the outside stays in one adapter and the core runs whole in a test?

**Name**

Dependency rule, also known as ports and adapters, hexagonal architecture, clean architecture, and layered architecture

**Thinking**

Say which element may depend on which, with every dependency pointing inward. The core, the elements that hold the product's rules, depends on nothing outside it, such as a file system, a clock, a network, a program the product calls, or the platform that runs it. Where the core needs something outside, it names what it needs as a port, in its own terms, and an adapter at the edge carries the port out for one technology. A test then stands its own adapter in the real one's place, and a new technology is a new adapter. Draw the dependencies as arrows with no cycle among them, as a cycle makes two elements one, which the developer builds and tests only as a whole. Say where a machine checks the rule on each change, such as a test that reads the imports or a tool of the language, as a rule that's only drawn erodes at the first deadline. Give a port to each outside thing that varies or that a test must stand in for, as a port with one adapter and no test that needs it costs a layer and gives nothing.

**Applies**

Every product with rules of its own and something outside them.

**Excludes**

A product that only joins outside things, with no rules of its own, such as a script that pipes one command into another, has no core to keep apart. How the code holds the rule inside a component is the code's, as the code best practice's dependency rule says.

**Cost**

Each port is an interface and an adapter more, and the adapter copies the data that crosses it into the core's own form.

**Sources**

- [Martin, The Clean Architecture, 2012](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Cockburn, Hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [ArchUnit User Guide](https://www.archunit.org/userguide/html/000_Index.html)
- [Thoughtworks, Fitness function-driven development](https://www.thoughtworks.com/insights/articles/fitness-function-driven-development)

### Q4

Making a part that hands data to another, do the developers of both sides find what crosses, its form, which side owns that form, and where its contract lies, with each data named alike in every view, so that the parts join without either reading the other's code?

**Name**

Interface contract, also known as published interface, consumer-driven contract, and concept model

**Thinking**

For each relation between two containers, or between the product and something outside it, name what crosses, its form, such as a JSON Schema, a command's arguments, or an API, which side owns that form, and where the contract lies, as two developers who each guess the form build halves that don't join. Let the side that offers the interface own it, and the side that takes it test against it. Pass plain data in the form the inner side uses, as passing the outer side's own records ties the core to it. Draw the data the parts pass or keep as a concept model, each data once by its name, with the relations between them and how many of each a relation joins, in a notation its readers know, such as a class diagram of the Unified Modeling Language, so that every view names each data alike. Leave each data's fields to its contract or its code, as the concept model holds only what stays while the fields change.

**Applies**

Every relation between containers, and each with the outside.

**Excludes**

A call between components inside one container is an interface of the code, as the code best practice's interface part says.

**Cost**

Each contract is a file to keep, and a change to it reaches both sides at once.

**Sources**

- [Martin, The Clean Architecture, 2012](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Vocke, The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Brown, C4 model, Notation](https://c4model.com/diagrams/notation)
- [Cockburn, Hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/)

### Q5

Following a use case from its role's first request to its end, does the developer see at each step which element acts, along which relation, with which data, and each branch, so that they build each step knowing who acts on what?

**Name**

Runtime view, also known as dynamic diagram, sequence diagram, and use case realization

**Thinking**

For each use case that branches, or whose path crosses the elements in an order one sentence can't give, draw its steps in order, from the role's first request to what the use case gives them. At each step, show which element acts, along which relation of the structure, and with which data of the concept model. Draw each branch, each step that sends work back, and each question put to a role, as each is a path the parts must join on and a test must take. Keep each step at the boundary between elements, as a step inside one component is its code's and goes untrue when the code changes. Check that each step runs along a relation the structure draws, and add the relation or move the step where none does.

**Applies**

Each use case whose steps cross elements in an order a developer would otherwise guess.

**Excludes**

A use case that one element carries alone, or whose path one sentence says, needs no figure, as each figure is one more to keep true.

**Cost**

A figure for each use case, kept true as the structure changes.

**Sources**

- [Brown, C4 model, Dynamic diagram](https://c4model.com/diagrams/dynamic)
- [arc42, Overview](https://arc42.org/overview)

### Q6

Setting the product up from nothing, does the developer find where each container runs and where it keeps each data, what each environment gives it, each outside thing it uses, and how it starts, so that they need ask no one?

**Name**

Deployment view, also known as deployment diagram and physical view

**Thinking**

Draw each environment the product runs in, such as the user's computer, a server, or a CI runner, with what it gives the product, such as an interpreter's version. In each, draw the containers it runs, and the data it keeps. Beside them, draw each thing outside the product that the containers depend on, with what they use of it. Say how a developer sets the product up and starts it, in a few sentences. A developer then runs the product without asking, and knows what each container can reach.

**Applies**

Every product, with an environment for each place it runs that differs, such as a test environment.

**Excludes**

How a user installs the product lies in its README. Point to it.

**Cost**

A figure for each environment, kept true as the infrastructure changes.

**Sources**

- [Brown, C4 model, Deployment diagram](https://c4model.com/diagrams/deployment)
- [arc42, Overview](https://arc42.org/overview)

### Q7

Doubting a choice, or meeting a case no line names, does the developer find the idea the parts carry out, the rules every part follows with their reasons, and for each decision its context, the options it beat, and its consequences, so that they keep, change, or extend it knowing what it was for?

**Name**

Architecture decision records, also known as decision log, crosscutting concepts, and solution strategy

**Thinking**

Open with the strategy, in a few sentences: the idea by which the parts give the product vision, and the few decisions that shape every part. Keep each rule that every part meeting the same case follows, with its reason, so that a developer carries the reason to a case no line names. Record each decision that shapes the structure, a quality, a dependency, an interface, or how the developers build the product, and that a developer would question. Give its context, the forces at play. Give the decision, and each option it beat. Give its consequences, its costs among them. A developer who meets a decision without its reasons can only follow it blindly or undo it blindly. Mark a decision that a later one replaces, with a link to the later one, and keep it, as the decision and its reasons still explain the code built on it.

**Applies**

Each decision that's hard to undo or that a developer would question.

**Excludes**

A decision any capable developer would make the same way needs no record.

**Cost**

Each record takes writing as the team makes the decision, and a reader meets the replaced records beside the ones that hold.

**Sources**

- [Nygard, Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR GitHub organization, Architectural Decision Records](https://adr.github.io/)
- [MADR](https://adr.github.io/madr/)
- [arc42, Overview](https://arc42.org/overview)

### Q8

Changing how a component works inside while the drivers stay, does the developer find every line of the architecture still true, so that the architecture changes only with its drivers and its structure, and its readers trust it?

**Name**

Architecturally significant decisions, also known as the important stuff

**Thinking**

Keep in the architecture only what stays while the drivers stay: the elements, their responsibilities, their relations and contracts, the rules, and the decisions behind them. Leave how an element works inside, such as its steps, a value it uses, a retry's seconds, or a data's fields, to its code and its contract, as a line about the inside goes untrue at the next change, and an architecture that changes with every fix is one its readers stop trusting. To check, imagine a change inside a component, such as a new value or a step moved, mark each line it would make untrue, and move each marked line to where that component's code or contract keeps it. Repeat with a change of another kind until the change marks no line.

**Applies**

Every line of the architecture.

**Excludes**

A detail that more than one part relies on, such as a limit two containers share, belongs to a contract, and the contract holds it.

**Cost**

A developer looks up the inside of a component in its code, not in the architecture.

**Sources**

- [Fowler, Software Architecture Guide](https://martinfowler.com/architecture/)
- [Nygard, Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [ADR GitHub organization, Architectural Decision Records](https://adr.github.io/)

### Q9

Testing a part or a path, does the developer find for each level what it checks against, what runs real, where doubles stand in and what keeps each true to what it stands for, and when the level passes, with each case at the lowest level that can catch it, so that a failing test points to one part or one path and the slow levels stay few?

**Name**

Test pyramid, also known as test sizes, practical test pyramid, and contract test

**Thinking**

Give each test level the one thing it checks against, and test each case at the lowest level that can catch it. The unit level checks a part against its contract, and holds most of the cases, as the code best practice draws them. The integration level checks the parts against this document, each path of the runtime view across the real joins between the parts, such as a repository's architecture tests. The acceptance level checks the real product in real use against the product vision, in a few runs that confirm what the lower levels checked. A case tested again at a higher level adds that level's slowness and flakiness and catches nothing new, and a level that holds most of the cases, such as end-to-end tests, fails in ways no one can place. For each level, say what runs real, where doubles stand in, at the ports of the dependency rule, and what keeps each double true to what it stands for. Draw a double from the real thing's documentation or a recorded run of it, and check it against the real thing by a contract test, as a double that gives what the real thing never would passes a test that the real one fails. Say when each level passes. For a test whose result varies by nature, such as one that runs an AI, say how many runs of how many must meet the expectation. When a higher level finds a fault, first add its test at the lowest level that missed it, see it fail, and fix it there. Trust a check that the levels rest on, such as a trial's judge, only once it has failed on a case that breaks what it checks.

**Applies**

Every product with more than one part.

**Excludes**

How to draw the cases of a unit is the code best practice's. Where a higher level is as fast and as steady as the unit level, the pyramid's shape matters less.

**Cost**

Each level needs its own doubles and setup, and the contract tests run against the real thing on its schedule, not on each change.

**Sources**

- [Fowler, TestPyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Vocke, The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Winters, Manshreck and Wright, Software Engineering at Google, chapter 11, Testing Overview](https://abseil.io/resources/swe-book/html/ch11.html)
- [Fowler, ContractTest](https://martinfowler.com/bliki/ContractTest.html)

### Q10

Before writing the code of a use case, does the developer find a test for each path through its runtime view at the level that joins the parts, so that they build the parts to join as the architecture says and see when they do?

**Name**

Acceptance test-driven development, also known as outside-in development and double-loop test-driven development

**Thinking**

Draw the integration level's test list from the runtime view, before any code. Take one test for each path through each use case: the main flow, each branch, each step that sends work back, and each question put to a role, until every move from one step to the next lies on some path. Each test runs its path from the first step to the end, through the real joins between the parts, with a double only at a port whose real thing the level can't run. The work on a use case starts with its failing test, and the unit tests drawn from each part's contract run inside it, as the code best practice says. A test list drawn from the code after it's written follows what the code does, not what the architecture says, and a path no test takes is one where the parts may not join.

**Applies**

Each use case the runtime view draws.

**Excludes**

A use case that one element carries alone gets its tests at that element's unit level.

**Cost**

Each test comes before the code that would make it easy to write, so the first one builds the harness the others use.

**Sources**

- [Freeman and Pryce, Growing Object-Oriented Software, Guided by Tests, as its table of contents gives it](https://growing-object-oriented-software.com/toc.html), secondary, as the maker read only a summary of it
- [Vocke, The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Beck, Canon TDD, 2023](https://newsletter.kentbeck.com/p/canon-tdd)

### Q11

With only the architecture and what it rests on, can a developer new to the product build a part in its place, test it at each level, and have it join the others, meeting each element under one name in every view?

**Name**

Views and viewpoints, also known as architecture description and correspondence rules

**Thinking**

Make each view answer one concern of the developer, as the other questions give them, and name each element, relation, and data alike in every view. A developer who meets a figure that breaks a rule, or a name that differs from the list, must choose which to follow, and guesses. Check the whole by building one use case in thought, with only the architecture and what it rests on: follow it from its driver through the structure, its contracts, its runtime path, its place on disk and in deployment, and its tests, and mend each place where the trail breaks. Repeat with a use case of another shape.

**Applies**

The whole architecture, once each section holds its content, and after each change.

**Excludes**

Whether the product built from it gives the product vision is the acceptance level's to show, not this reading's.

**Cost**

A reading of the whole after each change.

**Sources**

- [ISO/IEC/IEEE 42010, as Wikipedia's IEEE 1471 sums it up](https://en.wikipedia.org/wiki/IEEE_1471), secondary, as the maker read only a summary of it
- [ISO/IEC/IEEE 42010, as TRAK's What is an Architecture Viewpoint sums it up](https://trakviewpoints.sourceforge.io/what_is_an_architecture_viewpoint.html), secondary, as the maker read only a summary of it
- [Brown, C4 model, Notation](https://c4model.com/diagrams/notation)
