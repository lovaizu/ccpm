# `test-design`

## Goal tree

- The developers see, before anyone builds a part, whether the parts joined as the architecture draws give each key result, and the architecture's maker mends each place where they can't.
  - **C1** Each level that Test strategy names has the cases that check what its target promises.
    - **N1** Does each key result have an E2E case that runs an objective's main use at the size of a real request, and names the key result? (E2E cases)
    - **N2** Does each element of the architecture, each path through each sequence, each rule of Solution strategy, each decision of a component, and each handoff with its data, have an integration case that names it? (Integration cases)
    - **N3** Does each interface of the skeleton have a unit case for each class of what it takes and gives, its refusals and edges included, each naming the integration case it supports? (Unit cases)
  - **C2** Each case checks the parts through their interfaces, and fails until the parts are built.
    - **N4** Is each case a test in the test code, with its Given, When, and Then stated, that calls the skeleton only through its interfaces and fails on the empty bodies? (E2E cases, Integration cases, Unit cases)
  - **C3** No element and no case is left without the other.
    - **N5** Does the script that checks the trace give 0, finding that every element of the architecture has an integration case and every case names something one level up that exists? (Trace)
  - **C4** Each place where the cases show the architecture can't give a key result reaches its maker before anyone builds around it.
    - **N6** Does the list of gaps name each place where the cases can't follow the architecture, each with the element of the architecture that it bears on? (Gaps)

## Template

[template.md](template.md)

## Inputs

- [product-vision](../product-vision/best-practice.md)
- [readme](../readme/best-practice.md)
- [architecture](../architecture/best-practice.md)
- [software-design](../software-design/best-practice.md)

## Practices

### N1

Does each key result have an E2E case that runs an objective's main use at the size of a real request, and names the key result?

The developers know that the product does what its product vision promises only where a case runs it as its users do, and a case written before any part is built fixes what the parts together must give. ISTQB's test analysis takes each test condition from the test basis, here each key result.

1. *While deciding.* Open the product vision, the README, the architecture, and the skeleton, and read each to its end: the key results, the walkthrough, Test strategy with its levels and tools, each interface that the skeleton offers, and each double and tool that Test strategy names for the tests to run the parts and the product with, such as a double of the host. The trace: `{inputs}` read to its end.
2. *While making.* For each key result, write a case that runs the main use of its objective, as the README's walkthrough shows it, at the size of a real request, and names the key result, such as `KR1.1`.

### N2

Does each element of the architecture, each path through each sequence, each rule of Solution strategy, each decision of a component, and each handoff with its data, have an integration case that names it?

An element that no case reaches is one whose parts no one has seen fit together, and a case written through the skeleton before any body shows a gap between the parts while it's still cheap to mend. Steve Freeman and Nat Pryce's outside-in test-driven development, in [Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/), finds each part's roles by first writing the tests one level up.

1. *While making.* For each story's sequence, write a case for each path through it: the main flow, each branch, each step that sends work back, and each question put to the role, until every move from one step to the next lies on some path.
2. *While making.* For each rule of Solution strategy, write a case where the parts keep it, which can be run again with the part that holds the rule taken out, to see it fail, such as by the script that checks the trace.
3. *While making.* For each decision that a component alone makes, write a case that shows it, and for each handoff between parts, a case with the data it passes as Data model names it, until each kind of data lies on some case.
4. *While making.* Once the cases are written, go through each sequence arrow by arrow and branch by branch, name the case that runs each, and write a case for each arrow or branch that none runs, since the script that checks the trace finds only an element that no case names, not a branch left out.

### N3

Does each interface of the skeleton have a unit case for each class of what it takes and gives, its refusals and edges included, each naming the integration case it supports?

The interface a part offers comes from what the cases one level up need of it, and a case for each class finds the inputs that the part must treat apart before its body is written. The techniques are those of the ISTQB glossary: equivalence partitioning, boundary value analysis, and decision table testing.

1. *While making.* Divide each input and each result that an interface's contract names into classes that the part treats alike, the refused ones among them, and write one case for each class, naming the integration case it supports.
2. *While making.* Where a class ends on an ordered scale, such as a length or a count, write one case at each end and one at the nearest value of the next class.
3. *While making.* Where the contract's result depends on a combination of conditions, write one case for each combination that can occur, with the result it gives.
4. *While making.* For a part that holds a prompt, write a case where its description says it acts and one where it says it doesn't, for each kind of request it's for, and decide by code each point of the result that its record shows.

### N4

Is each case a test in the test code, with its Given, When, and Then stated, that calls the skeleton only through its interfaces and fails on the empty bodies?

A case kept as a test is the one statement of what a part must do, and a case that passes on an empty body tests nothing. Dan North's [behaviour-driven development](https://dannorth.net/introducing-bdd/) writes each scenario as Given, When, and Then.

1. *While making.* Write each case as a test in the place that Directory structure names for its level, in the form that the note of its section in the template gives, and keep the cases in the test code alone, since a list beside the code says each case twice.
2. *While making.* Run the tests and the type checker that Test strategy names, and see every case fail at an empty body, not at a fault of the test or a file that the skeleton lacks: a type that doesn't fit across a handoff is a gap that N6 lists, and a case that passes on an empty body tests nothing. Leave unrun a case that runs the real host or a model, which only the type checker reads at this point.

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
