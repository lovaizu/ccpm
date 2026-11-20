# `test-design`

## Goal tree

- The developers see, before anyone builds a part, whether the parts joined as the architecture draws give each key result, and the architecture's maker mends each place where they can't.
  - **C1** Each level that Test strategy names has the cases that check what its target promises.
    - **N1** Does each key result have an E2E case that runs an objective's main use at the size of a real request, and names the key result? (E2E cases)
    - **N2** Does each element of the architecture, each path through each sequence, each principle item of Principles, each decision of a component, and each handoff with its data, have an integration case that names it? (Integration cases)
    - **N3** Does each interface of the skeleton have a unit case for each class of what it takes and gives, its refusals, its edges, and the collections inside it included, and, where its result depends on what came before, for each transition that the product's use can bring about, so that each fault likely in its body fails a case, each naming the integration case it supports? (Unit cases)
  - **C2** Each case checks the parts through their interfaces, and fails until the parts are built.
    - **N4** Is each case a test in the test code, with its Given, When, and Then stated, that calls the skeleton only through its interfaces and fails on the empty bodies? (E2E cases, Integration cases, Unit cases)
  - **C3** No element and no case is left without the other.
    - **N5** Does the script that checks the trace give 0, finding that every element of the architecture has an integration case and every case names something one level up that exists? (Trace)
  - **C4** Each place where the cases show the architecture can't give a key result reaches its maker before anyone builds around it.
    - **N6** Does the list of gaps name each place where the cases can't follow the architecture, each with the element of the architecture that it bears on? (Gaps)

## Template

[template.md](template.md)

## Inputs

- [product-vision](../product-vision/best-practice.md), taking `Objectives and key results`
- [readme](../readme/best-practice.md), taking `Walkthrough`
- [architecture](../architecture/best-practice.md), taking `Solution strategy`, `Components`, `Data model`, `Sequences`, `Test strategy`
- [software-design](../software-design/best-practice.md), taking `Interface`, `Prompt`

## Practices

### N1

Does each key result have an E2E case that runs an objective's main use at the size of a real request, and names the key result?

The developers know that the product does what its product vision promises only where a case runs it as its users do, and a case written before any part is built fixes what the parts together must give. ISTQB's test analysis takes each test condition from the test basis, here each key result.

1. *While deciding.* Open the product vision, the README, the architecture, and the skeleton, and read the sections that `inputs` takes from each: the key results, the walkthrough, each principle item, decision, and handoff of the architecture, Test strategy with its checks and levels, and each interface that the skeleton offers, such as the one through which a test puts a double of the host in its place. The trace: `{inputs}` read to its end.
2. *While making.* For each key result, write a case that runs the main use of its objective, as the README's walkthrough shows it, at the size of a real request, and names the key result, such as `KR1.1`.

### N2

Does each element of the architecture, each path through each sequence, each principle item of Principles, each decision of a component, and each handoff with its data, have an integration case that names it?

An element that no case reaches is one whose parts no one has seen fit together, and a case written through the skeleton before any body shows a gap between the parts while it's still cheap to mend. Steve Freeman and Nat Pryce's outside-in test-driven development, in [Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/), finds each part's roles by first writing the tests one level up.

1. *While making.* For each story's sequence, write a case for each path through it: the main flow, each branch, each step that sends work back, and each question put to the role, until every move from one step to the next lies on some path.
2. *While making.* For each principle item of Principles, write a case where the parts keep it, which can be run again with the part that holds it taken out, to see it fail, such as by the script that checks the trace.
3. *While making.* For each decision that a component alone makes, write a case that shows it, and for each handoff between parts, a case with the data it passes as Data model names it, until each kind of data lies on some case.
4. *While making.* Once the cases are written, go through each sequence arrow by arrow and branch by branch, name the case that runs each, and write a case for each arrow or branch that none runs, since the script that checks the trace finds only an element that no case names, not a branch left out.

### N3

Does each interface of the skeleton have a unit case for each class of what it takes and gives, its refusals, its edges, and the collections inside it included, and, where its result depends on what came before, for each transition that the product's use can bring about, so that each fault likely in its body fails a case, each naming the integration case it supports?

The interface a part offers comes from what the cases one level up need of it, and a case for each class finds the inputs that the part must treat apart before its body is written. A part that keeps what came before, such as the steps a run has taken, breaks where its use sends an event in a state that no sequence draws, such as a subagent's end that reaches the main conversation after it resumed that subagent, which a case for each class of one call doesn't reach. The techniques are the four black-box techniques of the [ISTQB Foundation Level syllabus](https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/): equivalence partitioning, boundary value analysis, decision table testing, and state transition testing. A fault that no case catches shows only later, to a detector such as mutation testing, and a case written then comes from the code, not from what the part must do, so the maker designs cases until no likely fault passes them. James Grenning's ZOMBIES takes each collection through zero, one, and many, and the syllabus's error guessing lists the faults likely in a body, each to design a case for.

1. *While making.* Divide each input and each result that an interface's contract names into classes that the part treats alike, the refused ones among them, and write one case for each class, naming the integration case it supports.
2. *While making.* Where a class ends on an ordered scale, such as a length or a count, write one case at each end and one at the nearest value of the next class.
3. *While making.* Where what an interface takes holds a collection, such as a role's steps, a run's starts, or a subagent's results, write a case with none, one, and several of it, each that the use can bring about. Where the contract picks one of several, such as the latest or the one whose name matches, write a case of several in which any other pick, such as the first in place of the latest, gives another result.
4. *While making.* Where the contract compares a value, such as an ID, a name, or a prefix, write a case that holds, beside the value that matches, one that nearly matches, such as another plugin's name with the same prefix, and values on each side of it in order.
5. *While making.* Divide an input that sets the part up, such as a rule file or a plugin's folder, into its classes like any other input, such as a role of one step, of several, and with its result on a step that isn't its last, and give each case the setup that its class needs, since one setup shared by every case leaves each of its classes but one untested.
6. *While making.* Take as a class each event of the same stream that the part must leave alone, such as another plugin's event or the notice of a subagent that isn't the run's, as the use sends it beside the events that the part acts on.
7. *While making.* Where the contract's result depends on a combination of conditions, write one case for each combination that can occur, with the result it gives.
8. *While making.* Where an interface's result depends on what came before, such as a guard that keeps each start still open or a check that reads a record entry by entry, list each state that the product's use brings the part into and each event that the use sends it there, from the architecture's sequences and from what the host's records show it sends. Write one case for each of those transitions, with the state it moves to or the refusal it gives, an event that its state doesn't expect included where the use sends it, since a case of a transition that no use brings about fixes a behavior that no person meets, and a mend made for it breaks the use.
9. *While making.* For a part that holds a prompt, write a case where its description says it acts and one where it says it doesn't, for each kind of request it's for, and decide by code each point of the result that its record shows.
10. *While making.* Once an interface's cases are written, take each condition that its contract states and list the faults likely in a body that meets it: a bound one off, another element of several picked, a comparison turned around, and for or, a field left unread, and a refusal left out. Name for each the case that fails on it, and write a case where none does, with the result that the contract gives, since a fault that no case fails on is found only once the body is built, by a detector, and a case written then comes from the code.

### N4

Is each case a test in the test code, with its Given, When, and Then stated, that calls the skeleton only through its interfaces and fails on the empty bodies?

A case kept as a test is the one statement of what a part must do, and a case that passes on an empty body tests nothing. Dan North's [behaviour-driven development](https://dannorth.net/introducing-bdd/) writes each scenario as Given, When, and Then.

1. *While making.* Write each case as a test in the place that Directory structure names for its level, in the form that the note of its section in the template gives, and keep the cases in the test code alone, since a list beside the code says each case twice.
2. *While making.* Write in each case's Then the whole of what the interface gives and each change it makes, as its contract states them, such as the whole entry that a record gains and whether a call is stopped, since a Then that names a part of the result passes a body that gets the rest wrong.
3. *While making.* Give each case what the interface takes in the form that its use reads it, such as a record read from the JSON of its file in place of a literal written in the test, since a literal of the test and one of the code can be one object, and a body that compares them by identity passes the case and fails in use.
4. *While making.* Run the tests and the type checker that Test strategy names, and see every case fail at an empty body, not at a fault of the test or a file that the skeleton lacks: a type that doesn't fit across a handoff is a gap that N6 lists, and a case that passes on an empty body tests nothing. Leave unrun a case that runs the real host or a model, which only the type checker reads at this point.

### N5

Does the script that checks the trace give 0, finding that every element of the architecture has an integration case and every case names something one level up that exists?

Only a check by name finds each element that no case reaches among many, while the reading that N6 asks for judges whether the cases are enough.

1. *While making.* Where the architecture the product builds on keeps a script that checks the trace, such as one that a guide to building plugins runs on every plugin, take that one, and add only the checks it lacks. Elsewhere, make the script where Directory structure places it, so that it finds each element by where the architecture's template puts its name, such as each story by its `S<n>` and each key result by its `KR<n>.<m>`, and each case by the name it gives of what it supports.
2. *While making.* Run the script, and mend each case it names until it names none.

### N6

Does the list of gaps name each place where the cases can't follow the architecture, each with the element of the architecture that it bears on?

A gap that the cases show is mended in the architecture while nothing rests on it, and a case bent around it leaves the document wrong for every developer after.

1. *While making.* Read the cases against the architecture and the skeleton, and list each gap: a case that no part can hold; a part that no case reaches; a part whose cases change for more than one reason, such as a file's form and a remote's commands; and a handoff that no interface carries.
2. *While making.* Write each gap in the form that the note of Gaps in the template gives, and write the case that meets the gap as the architecture draws it, with only the parts, interfaces, and behaviors that the architecture draws, since a case built on a part invented around the gap fixes that part in place before the architecture's maker decides the mend.
3. *While making.* Where the architecture or the skeleton changes, change the cases to it as N1 to N4 say, and read them again for gaps, until you list none.
