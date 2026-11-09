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

**Thinking**

A maintainer with one behavior to change should find the one module to open without reading the bodies. David Parnas's [information hiding](https://doi.org/10.1145/361598.361623) gives each module one decision that the specification leaves to the code, most of all one that's likely to change. Decide the modules in order. First, list the decisions that the specification leaves to the code. Second, give each decision to one module. Third, have the module state its decision in a few words where the maintainer meets it first, such as at its top. If the module can't state it briefly, split the module. Where a decision meets a problem that a known design pattern solves, such as Strategy or Adapter in [Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns), use the pattern by its name, and only where a case of the specification needs it now, as N3 says. The name gives the maintainer the whole design at once.

**Steps**

1. Take a behavior that the specification might change, and read only what the modules say they decide. Check that it points to one module. Where it doesn't, rewrite what the modules say, or move the decision.

### N2

Does each name that a module offers state everything a caller needs to call it without reading its body?

**Thinking**

A caller who needn't read the body lets the body change behind the interface without breaking them. [Design by contract](https://www.eiffel.com/values/design-by-contract/introduction/), by Bertrand Meyer, states what a call expects, what it gives, and what stays true. Decide the interface in order. First, choose the names that other modules may use, and mark every other name as internal. Second, give each name the types it takes and gives, such as in its signature where the language allows. Third, write beside it, such as in a doc comment, what it gives, what comes back when there's nothing to give, what it expects of what it takes, what else it changes, and each way it refuses a correct call. Leave out what the types already say.

**Steps**

1. Have someone who hasn't read the body write a call from the interface alone, and run the call. Where the call fails or they had to guess, add what was missing.

### N3

Does each behavior of the code trace to a case of its specification, which is what the architecture asks of its part?

**Thinking**

Every behavior that no one asked for is code the maintainer must carry and keep working. [You Aren't Gonna Need It](https://martinfowler.com/bliki/Yagni.html) keeps only what the cases ask for now, in the form they ask for. The specification is what the architecture asks of the part: the decisions its line gives the part, the rules of the principles, and each step of a sequence that the part takes or answers, with the data as the data model names it. For each option, mode, and case that the code handles, name the case of the specification that asks for it. Remove what no case asks for.

### N4

Do the tests pass in any order and on every run, on a fresh machine set up from the code's setup alone?

**Thinking**

When a test fails, the cause should lie in the code. Neither the machine nor the order of the tests should cause it. A [hermetic](https://abseil.io/resources/swe-book/html/ch11.html) test holds everything it needs to set up, run, and clear its environment. So the code's setup names everything the code needs, with the versions it runs on, and each test sets up and clears everything it uses. A real tool that a test runs does only what the test asks of it.

**Steps**

1. For each real tool the tests run, such as git, find each thing it does on its own beyond the call, such as reading the machine's settings or starting maintenance in the background, and turn it off in the test's own settings.
2. Set the code up on a clean machine or container, from the code's setup alone, and add to the setup each missing thing that the setup or the tests found, such as a runtime.
3. Run the tests several times, and in a shuffled order.

### N5

Does each case of the specification, its edges and refusals included, have one test whose name says the case?

**Thinking**

A maintainer whose test fails should know which case it breaks. [Test-driven development](https://martinfowler.com/bliki/TestDrivenDevelopment.html) writes the tests from the specification's cases before the code. Decide the tests in order. First, list every case that the specification names: the usual one, each edge, and each refusal. Second, write one test for each case, named for the behavior it checks. If the name needs `and`, split the test. Third, write each test so that its reader grasps the situation, the action, and what must be so, such as in the three parts [Given, When, and Then](https://martinfowler.com/bliki/GivenWhenThen.html), with each expected value taken from the specification, not from what the code gives. Hold the test code to the same design as the code it tests: put what many tests share in one place, keep loops and branches out of a test, and give each failure a message that names the case, as Software Engineering at Google advises for [unit tests](https://abseil.io/resources/swe-book/html/ch12.html).

**Steps**

1. List every case that the specification names. The trace: `{inputs}` read to its end.
2. Run each test before you write its code, and see it fail. The trace: `{tests}` run.
3. Compare the list of cases with the tests, and check that each case points to one test.

### N6

Do the tests call the code only as its callers do, through its interfaces?

**Thinking**

A test that calls the code as its callers do fails only where a caller would break, so the maintainer can improve a body without fear. Software Engineering at Google calls this testing through public interfaces. For each test, ask whether it reaches anything that a caller can't. If it does, rewrite it to use the interface. Use the real parts where they run fast and wholly inside the test, and a stand-in only for what's slow or outside it.

**Steps**

1. Change a body without changing what its interface says, and run the tests. Rewrite each test that fails so that it calls the code through the interface.

### N7

Does breaking any behavior make a test fail?

**Thinking**

A test is worth the faults it catches, so each test checks the result its case asks for, and a broken behavior makes it fail. Machines can measure how well the tests catch faults: the lines no test runs, the mutants that survive, and the inputs that a property finds the code fails on. Use them to find the tests that are missing, and compare each count with the last, so that each change leaves fewer.

**Steps**

1. Find each line or branch that no test runs, such as by measuring coverage while the tests run, and add a test for each. The trace: `{coverage}` run.
2. Change the code in small ways with a [mutation testing](https://research.google/pubs/state-of-mutation-testing-at-google/) tool. For each change under which the tests still pass, add or fix the test of the behavior that the change breaks. The trace: `{mutation}` run.
3. Run the code over many inputs that the specification allows, such as with [property-based tests](https://hypothesis.works/articles/what-is-property-based-testing/). Keep each input that the code fails on as a fixed test.

### N8

Does the code refuse a wrong input from outside before it acts, with a message from which whoever ran it can fix the input?

**Thinking**

A fault from outside should never leave whoever ran the code stuck or their data half changed. [Fail fast](https://martinfowler.com/ieeeSoftware/failFast.pdf) checks what comes from outside, such as arguments, files, settings, and the replies of other programs, where it comes in and before the code does anything. Decide the checks in order. First, at that place, read the input into the form that the inside of the code uses, as [parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) says, and check its type, its format, and whether its value makes sense for the task. Second, refuse a value that the code can't read, instead of guessing it, and catch only the errors you mean to handle. Third, write the message so that whoever ran the code learns which program refused, what was wrong, where, and what the code accepts. Write each check so that it runs however someone runs the code, unlike an assert that someone can turn off.

**Steps**

1. Give the code each wrong input that the specification names. Read each message as the person who ran the code, and check that they can fix the input from the message alone.
