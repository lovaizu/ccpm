---
name: code
version: 0.1.0
---

# Code

Code is used by whoever runs it and whoever maintains it, a person or an AI. Whoever runs it gets
the behavior they asked for. Whoever maintains it trusts, from its tests passing, that the behavior
holds, and so changes the code at once and with confidence.

Code is written in this order, each step the ground of the next:

1. Check the inputs: the requirements, how it is made, how it is checked and the development rules
   are all there, and settle what the code needs. What is missing goes back to whoever gave it.
2. Design it: split it into functions and modules by what each takes on, each taking on one thing
   alone, with each piece of knowledge in one place; decide what each takes in and gives back, and
   where what comes from outside is checked. These are the units the tests are written for.
3. Run the existing tests and see them pass, before changing anything.
4. Build it test first: for each behavior, write a test, see it fail, write the least code that
   passes it, then tidy it back to the design, such as putting what is written twice in one place.
5. Check it by the development rules and by how it is checked.

## Format

### F-1: Shape

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

Can whoever runs the code run it with only the runtime, at the versions, and the libraries and
tools the development rules name?

Look at: what the code imports and calls, and what the tests are run on, against what the
development rules name, the oldest version of the runtime among them.

Why: what the code uses beyond them is missing on some user's machine, and the code fails there for
a reason the user was never told.

### B-2: One thing for each function and module

Can the maintainer change one thing the code takes on by changing one function or module?

Look at: each function and module, against what it takes on; one that takes on two things fails.

Why: a part that takes on two things is changed for one and breaks the other.

### B-3: Each piece of knowledge in one place

Can the maintainer change a piece of knowledge, such as a rule or a value, by changing the one
place it is written?

Look at: the same logic or value written in two places, or the same lines with only names changed;
any such pair fails.

Why: what is written twice is changed in one place and left in the other, and the two drift apart
without any test failing.

### B-4: Checked before it is used

When whoever runs the code gives it something wrong, such as a file, an argument or what another
program hands it, are they stopped before the code uses it?

Look at: each place the code takes in something from outside, against the first place it uses it; a
check that stops what the requirements say it must not be lies between them.

Why: a wrong input used fails far from where it came in, or does harm, such as writing outside the
folder it was meant for.

### B-5: A stop says what went wrong

When the code stops, can whoever runs it tell from what it says what went wrong?

Look at: each message the code gives when it stops names the input or the condition that was wrong.

Why: a stop that says only that something failed leaves the user to read the code to learn what
they gave wrong.

### B-6: A stop says what to do

When the code stops, can whoever runs it tell from what it says what to do about it?

Look at: each message the code gives when it stops names an action to take, such as a value to give
instead or how to install a tool that is missing.

Why: a user who knows what went wrong but not how to put it right is left to work out the fix.

### B-7: A test for each behavior asked

For each behavior the requirements ask of the code, can the maintainer learn from some test that
the code does it?

Look at: each such behavior, among them each check on what the code takes in, matched to a test
whose Then checks it; a behavior left without one fails.

Why: the tests passing give trust only in the behaviors they hold.

### B-8: A test fails when its behavior breaks

When the behavior a test checks is broken in the code, does the maintainer learn of it from that
test failing?

Look at: break the line the test is about, run the test, see whether it fails, and put the line
back.

Why: a test that does not fail when its behavior breaks looks the same as one that works, and lets
a fault pass.

### B-9: A failure names the one behavior that broke

When a test fails, can the maintainer tell from that failure alone which one behavior broke?

Look at: for each test, the behaviors whose fault would make it fail; a test that would fail on two
fails.

Why: a test that holds several behaviors, failing, leaves the maintainer to read its code to learn
which of them broke.

### B-10: The same result on every run

Can the maintainer take each test failure as a fault, because each test gives the same result
whenever it is run, alone or with the others, in any order?

Look for: a test that reads the clock, the network, or the machine it runs on; a test that leaves
files or state behind for the next one; a test that needs another to run first. Any one fails.

Why: a test that fails on some runs and not on others teaches the maintainer to rerun it rather
than read it, and then a real failure is rerun too.

### B-11: The development rules' checks pass

Do the checks the development rules name, such as the tests, the formatter, the linter and the
type checker, run with the settings kept in the repository, pass on the code and its tests?

Why: what a tool finds on every run needs no review spent on it, and a reader finds it only
sometimes.

### B-12: Every line and branch run

Can the maintainer see, from the coverage of the whole test run, that every line and every branch
of the code is taken by some test?

Look at: the coverage report, counting branches as well as lines, lists none as not run.

Why: a line or branch no test takes may be broken without any test failing.

### B-13: Lines left out of the count say why

For each line left out of the coverage count, can the maintainer tell from what is written beside it
which environment, one the tests cannot make, decides whether the line runs?

Why: a line left out without its reason cannot be told from a line left out to make the count pass,
and the next maintainer keeps the gap.

### B-14: One name for one thing

Can the maintainer find every place a thing is used by searching for its name?

Look at: each thing the code, its tests and its documents name, such as a function, a field, a file
or an idea, called by one name in all of them; a thing called by two names fails.

Why: a maintainer who meets two names takes them for two things, and a search for one finds only
half of where the thing is used.

## Usability

None: each thing that makes code easy to run or change is one the opening names its user gets from
it, so its item is in Benefit.
