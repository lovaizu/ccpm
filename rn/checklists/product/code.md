---
name: code
version: 0.1.0
---

# Code

Code is used by whoever runs it and whoever maintains it, a person or an AI. Whoever runs it gets
the behavior they asked for. Whoever maintains it trusts, from its tests passing, that the behavior
holds, and so changes the code at once and with confidence.

Code is written in this order, each step the ground of the next, and judged by the items below,
drawn from Google's "What to look for in a code review" (google/eng-practices, CC BY 3.0); its
tests are designed by the techniques of the ISTQB Certified Tester Foundation Level syllabus
v4.0.1, chapter 4:

1. Check the inputs: the requirements, how it is made, how it is checked and the development rules
   are all there, and settle what the code needs, among it a tool for each of statement and branch
   coverage (C0/C1), mutation testing and property-based testing in its language, chosen from what
   is current and kept up now. What is missing, such as a stable tool for one of them, goes back to
   whoever gave it.
2. Design it: split it into functions and modules by what each takes on, each taking on one thing
   alone, with each piece of knowledge in one place across the repository, what its code and tests
   already share used rather than written again; decide what each takes in and gives back, and
   where what comes from outside is checked. These are the units the tests are written for.
3. Design the tests from the requirements, before the code, by the technique that fits what each
   unit takes in and decides: for each input and output, its equivalence partitions, the invalid
   among them, one test each; for each ordered partition, 3-value boundary value analysis, each
   boundary and both its neighbors; for conditions that combine, a decision table, one test for each
   feasible rule; for what moves between states, state transition testing, every transition, the
   invalid ones tried; for each behavior over inputs of a kind, such as any text, the property
   every input of the kind holds, such as a parse giving back what was written.
4. Run the existing tests and see them pass, before changing anything.
5. Build it test first, one designed test at a time: write the test, see it fail, write the least
   code that passes it, then tidy it back to the design, such as putting what is written twice in
   one place. A behavior found needed while writing goes back to step 3 and is designed first.
6. Check it by the development rules and by how it is checked, each check, the tests, the
   coverage, the property tests and the mutation testing alike, on what the change touches before
   it is handed over, the property tests on few inputs, and on the whole in CI, the property tests
   on many, so the time each change waits on grows with the change, not with the code.
7. Before it is run many times or built on, run it once on the smallest real case, and confirm
   from what it did, its output, its logs or the records of what it ran, that it does what it is
   for.

Each item of `usability.md` applies to code, read by whoever maintains it, with its behavior as its
subject and each file a part, the tests among them; its F-1 is answered by this F-1, its B-7 by each
piece of knowledge, such as a rule, a value or a way of reading an input, written in one place
across the repository, and its B-13 by one name for each thing across the code and its tests, so a
search for the name finds every place it is used.

## Format

### F-1: Shape

Scope: each part

Does the code follow this template, in the forms its language and its development rules set?

```text
<At the top of each module>  what the module does, and why it is there
<For each function>          what it takes in, what it gives back, and when it stops,
                             as types where the language has them, otherwise as a comment
<For each test>              name: what must happen, as one sentence
                             body: Given: <the situation>, When: <what is done>,
                             Then: <what must be so>, each in plain words, as comments
```

Why: the maintainer finds what each module and function is for, and what each test checks, in the
same place in every file, written when the design and the tests were decided.

## Benefit

### B-1: Run in the environment the development rules set

Scope: whole

Can whoever runs the code run it with only the runtime, at the versions, and the libraries and
tools the development rules name?

Look at: what the code imports and calls, and what the tests are run on, against what the
development rules name, the oldest version of the runtime among them.

Why: what the code uses beyond them is missing on some user's machine, and the code fails there for
a reason the user was never told.

### B-2: One thing for each function and module

Scope: each part

Can the maintainer change one thing the code takes on by changing one function or module?

Look at: each function and module, against what it takes on; one that takes on two things fails.

Why: a part that takes on two things is changed for one and breaks the other.

### B-19: Only what is needed now

Scope: whole

Does every function, parameter, branch and option serve a behavior the requirements ask now?

Look for: code more general than its callers use, such as a parameter every caller gives the same
value, or a case for a future the requirements do not name.

Why: code for a need that may come is read, tested and kept by every maintainer meanwhile, and when
the need comes it seldom has the shape that was guessed.

### B-4: Checked before it is used

Scope: whole

When whoever runs the code gives it something wrong, such as a file, an argument or what another
program hands it, are they stopped before the code uses it?

Look at: each place the code takes in something from outside, against the first place it uses it; a
check that stops what the requirements say it must not be lies between them.

Why: a wrong input used fails far from where it came in, or does harm, such as writing outside the
folder it was meant for.

### B-5: A stop says what went wrong

Scope: whole

When the code stops, can whoever runs it tell from what it says what went wrong?

Look at: each message the code gives when it stops names the input or the condition that was wrong.

Why: a stop that says only that something failed leaves the user to read the code to learn what
they gave wrong.

### B-6: A stop says what to do

Scope: whole

When the code stops, can whoever runs it tell from what it says what to do about it?

Look at: each message the code gives when it stops names an action to take, such as a value to give
instead or how to install a tool that is missing.

Why: a user who knows what went wrong but not how to put it right is left to work out the fix.

### B-15: A stop cleared by the action it names

Scope: whole

When the code stops, can whoever runs it always go on by taking the action it names?

Look at: each stop's action is one whoever is stopped can take with what they have, and taking it
lets the check through; an action outside what they may do, such as a read another check stops, or
one after which the check still stops, fails.

Why: a stop its own action does not clear leaves the run stuck, going round or ended, and a check
there to keep the work right stops the work.

### B-20: Runs at the same time kept apart

Scope: whole

When two runs of the code go at once, such as two sessions or two test workers, does each get the
result it would get alone?

Look at: each file, port, folder or other place a run writes or holds, against whether another run
at the same time could write or hold the same one.

Why: runs that share a place they write overwrite each other's work, and the fault shows only when
they happen to meet, so a test seldom finds it.

### B-21: Each name says what it is or does

Scope: each part

Can the maintainer tell from each name of a module, function, variable and test what the thing is
or does, without reading its body?

Why: a name that says less than its thing sends the maintainer into the body at every use, and one
that says something else is believed.

### B-22: Each comment says what the code cannot

Scope: each part

Does each comment say something the code itself cannot, such as why it is so, or what a regular
expression or an algorithm does?

Look for: a comment that says again what the line under it does.

Why: a comment that repeats the code is one more thing to read and to keep true, and the reason
behind a decision, which only a comment can hold, is what the next maintainer needs to change it
safely.

### B-23: Written like the code around it

Scope: whole

Where no rule of the development rules settles a choice, is the code written as the code around it
is, in its idioms, its error handling and its layout?

Why: the maintainer reads a difference as meaning something, and looks for a reason that is not
there.

### B-7: A test for each designed test case

Scope: whole

For each behavior the requirements ask of the code, can the maintainer learn from some test that
the code does it?

Look at: the test cases the techniques of step 3 give, each equivalence partition, the invalid ones
among them, each boundary and its neighbors, each feasible rule of each decision table and each
transition, each matched to a test whose Then checks it; one left without a test fails.

Why: the tests passing give trust only in the behaviors they hold.

### B-8: A test fails when its behavior breaks

Scope: whole

When the behavior a test checks is broken in the code, does the maintainer learn of it from that
test failing?

Look at: mutation testing, which makes each small change to the code a fault could, such as a
comparison, an operator or a value replaced, and runs the tests on each; a mutant no test fails on,
a survivor, fails.

Why: a test that does not fail when its behavior breaks looks the same as one that works, and lets
a fault pass.

### B-9: A failure names the one behavior that broke

Scope: whole

When a test fails, can the maintainer tell from that failure alone which one behavior broke?

Look at: for each test, the behaviors whose fault would make it fail; a test that would fail on two
fails.

Why: a test that holds several behaviors, failing, leaves the maintainer to read its code to learn
which of them broke.

### B-10: The same result on every run

Scope: whole

Can the maintainer take each test failure as a fault, because each test gives the same result
whenever it is run, alone or with the others, in any order?

Look for: a test that reads the clock, the network, or the machine it runs on; a test that leaves
files or state behind for the next one; a test that needs another to run first. Any one fails.

Why: a test that fails on some runs and not on others teaches the maintainer to rerun it rather
than read it, and then a real failure is rerun too.

### B-11: The development rules' checks pass

Scope: whole

Do the checks the development rules name, such as the tests, the formatter, the linter and the
type checker, run with the settings kept in the repository, pass on the code and its tests?

Why: what a tool finds on every run needs no review spent on it, and a reader finds it only
sometimes.

### B-12: Every statement and branch run by an example

Scope: whole

Can the maintainer see, from the coverage of the example tests, that every statement and every
branch of the code is taken by some test that takes it on every run?

Look at: the statement coverage (C0) and the branch coverage (C1) of the tests without the property
tests, whose inputs change from run to run; any statement or branch not run fails.

Why: a line or branch no test takes may be broken without any test failing, and one taken only by
an input made at random is taken on some runs and not on others.

### B-13: Lines left out of the count say why

Scope: whole

For each line left out of the coverage count, can the maintainer tell from what is written beside it
which environment, one the tests cannot make, decides whether the line runs?

Why: a line left out without its reason cannot be told from a line left out to make the count pass,
and the next maintainer keeps the gap.

### B-16: Each check left out, the user's decision

Scope: whole

For each line, branch, input or mutant left out of the coverage, the property tests or the
mutation testing, can the maintainer tell from what is written beside it that the user decided it,
and why no behavior changes with it, such as one in a type annotation never run?

Why: leaving a check out is easier than writing the test, so whoever makes the code and leaves
them out on their own judgment ends with the checks full of gaps; one left out without the user's
decision and its reason cannot be told from one left out to make the run pass, and the next
maintainer keeps the gap.

### B-17: A behavior holds for every input of its kind

Scope: whole

For each behavior over inputs of a kind, such as any text, path or list, can the maintainer learn
from a test that it holds for the inputs no example names?

Look at: property-based testing of each such behavior, on every run of the checks, which makes many
inputs of the kind and checks a property every one must have, such as a parse giving back what was
written; with new inputs on every run, CI included, so that inputs not yet tried are met, and each
input that fails reproduced from what the failure prints, not run again, and kept as an example.

Why: examples check the inputs their writer thought of, and a fault waits in the ones they did not.

### B-18: The whole test run in seconds

Scope: whole

Can the maintainer run every test in seconds, so that the checks run on every change and mutation
testing, which runs the tests once for each mutant, ends in minutes?

Look at: the time the whole test run takes, against what the tests do; what a test sets up by
running other programs, such as a repository made by git commands for every test, where it could be
made once and copied, fails.

Why: a test run that takes minutes is run less often, and mutation testing multiplies its time by
the number of mutants, so the maintainer waits on every change, or stops running the checks.

### B-24: The documents follow the change

Scope: whole

When the code changes how its users build, test, run or release it, do the documents that tell
them so say the same as the code?

Look at: each README and guide that names a command, an option or a step the change touches.

Why: a document that names a step the code no longer takes is followed and fails, and is believed
over the code.

### B-25: Tried once, its purpose seen in what it did

Scope: whole

Before the code is run many times or built on, can whoever maintains it tell, from one run on the
smallest real case, read in its output, its logs or the records of what it ran, that it does what it
is for?

Look for: a run taken as confirmed because it started, exited with 0 or gave something back; these
show only that it ran.

Why: code that runs is not yet code that does its job; run many times at once on a fault, every run
is spent, and the faults show tangled together, while one small run shows each where it lies.
