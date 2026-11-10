# `code`

## Goal

Maintainers, people or AI agents, change what the code does and know that every behavior its specification asks for still holds, and whoever runs the code can fix a wrong input from outside.

## Inputs

- [architecture](../architecture/best-practice.md)

## Parts

- **manifest**: what the maintainer needs to set the code up on a fresh machine and run its tests: everything the code needs to run, with the versions it runs on, and how to run the tests.
- **module-opening**: for each module, a few words on what this module alone decides, at the place the maintainer meets first when they open the module.
- **interface**: each name a module offers to others, with everything a caller needs to call it without reading its body: the types it takes and gives, what it gives, what it expects of what it takes and each way it refuses.
- **body**: the code under each interface that gives the behavior.
- **tests**: tests of the specification's cases, one test for each case, so the maintainer can tell which test checks which case and which code. Each test has a name that says the behavior it checks, and shows the situation, the action, and what must be so.

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The maintainer finds the one place where a change belongs. |
| C2 | The tests show whether every behavior still holds. |
| C3 | Whoever runs the code can fix a wrong input from outside. |

## Necessary conditions

| ID | Factor | Condition | Parts |
| --- | --- | --- | --- |
| N1 | C1 | Does each module say, where the maintainer first meets it, the one thing it alone decides? | module-opening |
| N2 | C1 | Does each name that a module offers state everything a caller needs to call it without reading its body? | interface |
| N3 | C1 | Does each behavior of the code trace to a case of its specification, which is what the architecture asks of its part? | interface, body |
| N4 | C2 | Do the tests pass in any order and on every run, on a fresh machine set up from the code's setup alone? | manifest, tests |
| N5 | C2 | Does each case of the specification, its edges and refusals included, have one test whose name says the case? | tests |
| N6 | C2 | Do the tests call the code only as its callers do, through its interfaces? | interface, tests |
| N7 | C2 | Does breaking any behavior make a test fail? | body, tests |
| N8 | C3 | Does the code refuse a wrong input from outside before it acts, with a message from which whoever ran it can fix the input? | body |

## Practices

### N1

Does each module say, where the maintainer first meets it, the one thing it alone decides?

A maintainer with one behavior to change should find the one module to open without reading the bodies. David Parnas's [information hiding](https://doi.org/10.1145/361598.361623) gives each module one decision that the specification leaves to the code, most of all one that's likely to change.

1. *While deciding.* List the decisions that the specification leaves to the code. The trace: `{inputs}` read to its end.
2. *While deciding.* Give each decision to one module.
3. *While deciding.* Where a decision meets a problem that a known design pattern solves, such as Strategy or Adapter in [Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns), use the pattern by its name, since the name gives the maintainer the whole design at once. Use it only where a case of the specification needs it now, as N3 says.
4. *While making.* Have the module state its decision in a few words where the maintainer meets it first, such as at its top. If the module can't state it briefly, split the module.
5. *While making.* Take a behavior that the specification might change, and read only what the modules say they decide. Check that it points to one module. Where it doesn't, rewrite what the modules say, or move the decision.

### N2

Does each name that a module offers state everything a caller needs to call it without reading its body?

A caller who needn't read the body lets the body change behind the interface without breaking them. [Design by contract](https://www.eiffel.com/values/design-by-contract/introduction/), by Bertrand Meyer, states what a call expects, what it gives, and what stays true.

1. *While deciding.* Choose the names that other modules may use, and mark every other name as internal.
2. *While making.* Give each name the types it takes and gives, such as in its signature where the language allows.
3. *While making.* Write beside each name, such as in a doc comment, what it gives, what comes back when there's nothing to give, what it expects of what it takes, what else it changes, and each way it refuses a correct call.
4. *While making.* Leave out what the types already say.
5. *While making.* Have someone who hasn't read the body write a call from the interface alone, and run the call. Where the call fails or they had to guess, add what was missing.

### N3

Does each behavior of the code trace to a case of its specification, which is what the architecture asks of its part?

Every behavior that no one asked for is code the maintainer must carry and keep working. [You Aren't Gonna Need It](https://martinfowler.com/bliki/Yagni.html) keeps only what the cases ask for now, in the form they ask for.

1. *While deciding.* For each option, mode, and case that the code handles, name the case of the specification that asks for it. The specification is what the architecture asks of the part: the decisions its line gives the part, the rules of the principles, and each step of a sequence that the part takes or answers, with the data as the data model names it.
2. *While making.* Remove what no case asks for.

### N4

Do the tests pass in any order and on every run, on a fresh machine set up from the code's setup alone?

When a test fails, the cause should lie in the code, never in the machine or in the order of the tests. A [hermetic](https://abseil.io/resources/swe-book/html/ch11.html) test holds everything it needs to set up, run, and clear its environment.

1. *While making.* Have the code's setup name everything the code needs, with the versions it runs on.
2. *While making.* Have each test set up and clear everything it uses.
3. *While making.* For each real tool the tests run, such as git, find each thing it does on its own beyond the call, such as reading the machine's settings or starting maintenance in the background, and turn it off in the test's own settings, so that the tool does only what the test asks of it.
4. *While making.* Set the code up on a clean machine or container, from the code's setup alone, and add to the setup each missing thing that the setup or the tests found, such as a runtime.
5. *While making.* Run the tests several times, and in a shuffled order, and check that they pass on every run.

### N5

Does each case of the specification, its edges and refusals included, have one test whose name says the case?

A maintainer whose test fails should know which case it breaks. [Test-driven development](https://martinfowler.com/bliki/TestDrivenDevelopment.html) writes the tests from the specification's cases before the code.

1. *While deciding.* List every case that the specification names: the usual one, each edge, and each refusal.
2. *While making.* Write one test for each case, named for the behavior it checks. If the name needs `and`, split the test.
3. *While making.* Write each test so that its reader grasps the situation, the action, and what must be so, such as in the three parts [Given, When, and Then](https://martinfowler.com/bliki/GivenWhenThen.html), with each expected value taken from the specification, not from what the code gives.
4. *While making.* Keep each test readable on its own, with the values that its case turns on in its own body, and put in one helper only setup that many tests share, such as building the object under test, since Software Engineering at Google advises that [unit tests](https://abseil.io/resources/swe-book/html/ch12.html) be descriptive and meaningful rather than free of repetition.
5. *While making.* Keep loops and branches out of a test, as the same source advises.
6. *While making.* Give each failure a message that names the case, as the same source advises.
7. *While making.* Run each test before you write its code, and see it fail. The trace: `{tests}` run.
8. *While making.* Compare the list of cases with the tests, as a maintainer whose test failed would, and check that each case points to one test and each test's name to its case.

### N6

Do the tests call the code only as its callers do, through its interfaces?

A test that calls the code as its callers do fails only where a caller would break, so the maintainer can improve a body without fear. Software Engineering at Google calls this [testing through public interfaces](https://abseil.io/resources/swe-book/html/ch12.html).

1. *While making.* For each test, ask whether it reaches anything that a caller can't. If it does, rewrite it to use the interface.
2. *While making.* Use the real parts where they run fast and wholly inside the test, and a stand-in only for what's slow or outside it.
3. *While making.* Change a body without changing what its interface says, and run the tests. Rewrite each test that fails so that it calls the code through the interface.

### N7

Does breaking any behavior make a test fail?

A test is worth the faults it catches, so breaking a behavior must make a test fail. Coverage, [mutation testing](https://research.google/pubs/state-of-mutation-testing-at-google/), and [property-based testing](https://hypothesis.works/articles/what-is-property-based-testing/) measure how well the tests catch faults: the lines no test runs, the mutants that survive, and the inputs that a property finds the code fails on.

1. *While making.* Have each test check the result that its case asks for.
2. *While making.* Find each line or branch that no test runs, such as by measuring coverage while the tests run, and add a test for each. The trace: `{coverage}` run.
3. *While making.* Change the code in small ways with a mutation testing tool. For each change under which the tests still pass, add or fix the test of the behavior that the change breaks. The trace: `{mutation}` run.
4. *While making.* Run the code over many inputs that the specification allows, such as with property-based tests. Keep each input that the code fails on as a fixed test.
5. *While making.* Compare each count with the last, so that each change leaves fewer.

### N8

Does the code refuse a wrong input from outside before it acts, with a message from which whoever ran it can fix the input?

A fault from outside should never leave whoever ran the code stuck or their data half changed. [Fail fast](https://martinfowler.com/ieeeSoftware/failFast.pdf) checks what comes from outside, such as arguments, files, settings, and the replies of other programs, where it comes in and before the code does anything.

1. *While making.* Where the input comes in, read it into the form that the inside of the code uses, as [parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) says, and check its type, its format, and whether its value makes sense for the task.
2. *While making.* Refuse a value that the code can't read, instead of guessing it.
3. *While making.* Catch only the errors you mean to handle.
4. *While making.* Write the message so that whoever ran the code learns which program refused, what was wrong, where, and what the code accepts.
5. *While making.* Write each check so that it runs however someone runs the code, unlike an assert that someone can turn off.
6. *While making.* Give the code each wrong input that the specification names. Read each message as the person who ran the code, and check that they can fix the input from the message alone.
