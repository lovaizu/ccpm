---
name: code
version: 0.1.0
---

# Code

Code is run by its users and changed by whoever maintains it; its tests are read and run by that
maintainer. Code and its tests let the maintainer:

- trust, from the tests passing, that the code does what its README and its design ask;
- tell from each test, read alone, what the code must do and in what situation;
- see that every branch of the code is run by a test, so a missing test and code no test needs
  both show;
- change the code and learn at once, by running the tests or from any push, whether it still does
  what it must;
- change a behavior by changing the one place it is written;
- read any part of the code without first learning the habits of whoever wrote it;
- trust that what a tool can find without running the code, such as a style kept in no other file,
  a misused part of the language or a wrong type, is already found.

And they let whoever runs the code:

- run it with only what its README says it needs;
- be stopped before anything they gave it wrong is used;
- tell, when it stops, what went wrong and what to do about it.

What the code must do is set by its README and its design; this checklist judges the code and its
tests against them, from the code, the tests and their results.

## Benefit

### B-1: Tests hold what the code must do

Can the maintainer trust, from each test passing, that the code does a behavior the README or the
design asks of it?

Look at: for each test, the sentence of the README or the design that asks the behavior it checks;
a test with no such sentence fails.

Why: a test written after the code is fitted to what the code does, so it passes a fault the code
was written with; a test written first, from what the code must do, holds the code to it.

### B-2: Each test can fail

When the behavior a test checks is broken in the code, does the maintainer learn of it from that
test failing?

Look at: break the line the test is about, run the test, see whether it fails, and put the line back.

Why: a test never seen failing may check nothing, and one that checks nothing looks the same as one
that works.

### B-3: Both sides of each check

For each check the code makes on what it receives, can the maintainer find a test where the check
stops the input and one where it lets the input through?

Why: a check tested only on what it lets through looks the same as no check at all, and one tested
only on what it stops may stop everything.

### B-4: What each test checks, told in plain words

From each test read alone, can the maintainer tell, in words that name nothing of the code, the
situation, what is done in it, and what must then be so?

Look at: the test's Given, When and Then; one that names a function, a variable or another part of
the code fails.

Why: a maintainer who changes the code decides from the test whether a failure is a fault in the
code or a behavior that was meant to change; a test whose intent must be read out of its code is
kept or deleted by guess.

### B-5: Each Then checked as said

Can the maintainer trust that the code under each Then checks what its words say, all of it and no
more?

Look at: each thing the Then's words name, matched to a check under it, and each check under it,
matched to a thing its words name; a thing or a check left without a match fails.

Why: a Then whose code checks less than its words lets a fault pass under a test that reads as if it
caught it; one that checks more fails on a change the test never meant to stop.

### B-6: Every branch run

Can the maintainer see, from the coverage report of the whole test run, that every branch of the
code is taken by some test?

Look at: the report, counting branches as well as lines, lists no branch and no line as not run.

Why: a branch no test takes may be broken without any test failing, and a missing test shows as a
branch not taken.

### B-7: Nothing no test needs

Can the maintainer trust that every line of the code is there for a behavior some test checks?

Look at: remove each line, run the tests, and put it back; a line whose removal fails no test fails.

Why: a line no test needs is either a missing test or code with no purpose, and both are kept by
every later maintainer without knowing why.

### B-8: Lines left out of the count say why

For each line left out of the coverage count, can the maintainer tell from what is written beside it
which environment, one the tests cannot make, decides whether the line runs?

Why: a line left out without its reason cannot be told from a line left out to make the count pass,
and the next maintainer keeps the gap.

### B-9: Each failure learned from every push

Does the maintainer learn, from every push and without running anything by hand, of each test that
fails and each branch no test takes?

Look at: the repository's automated runs, which on every push run the whole test suite and the
coverage count, and fail on a test that fails or a branch not taken.

Why: a check left to be run by hand is skipped, and a skipped check goes unnoticed until the fault
reaches a user.

### B-10: The same result on every run

Can the maintainer take each test failure as a fault, because each test gives the same result
whenever it is run, alone or with the others, in any order?

Look for: a test that reads the clock, the network, or the machine it runs on; a test that leaves
files or state behind for the next one; a test that needs another to run first. Any one fails.

Why: a test that fails on some runs and not on others teaches the maintainer to rerun it rather than
read it, and then a real failure is rerun too.

### B-11: Run with only what the README names

Can whoever runs the code run it with only the runtime, libraries and tools its README names?

Look at: what the code imports and calls, against what the README names.

Why: what the code uses beyond them is missing on some user's machine, and the code fails there for
a reason the user was never told.

### B-12: Run on the oldest version it supports

Can users on the oldest version of the runtime the README says the code supports run it?

Look at: the tests, run on that version by the repository's automated runs, passing.

Why: code written on a newer version uses what the older one lacks, and fails for the users on it.

### B-13: Stopped before a wrong input is used

When whoever runs the code gives it something wrong, such as a file, an argument or what another
program hands it, are they stopped before the code uses it?

Look at: each place the code takes in something from outside, against the first place it uses it; a
check that stops a wrong one lies between them.

Why: a wrong input used fails far from where it came in, or does harm, such as writing outside the
folder it was meant for, and the user cannot tell from the failure what they gave wrong.

### B-14: A stop says what to do

When the code stops, can whoever runs it tell from what it says what went wrong and what to do about
it?

Look at: each message the code gives when it stops names the input or the condition that was wrong,
and an action to take, such as a value to give instead or how to install a tool that is missing.

Why: a stop that says only that something failed leaves the user to read the code to learn what
they must change.

### B-15: The static checks pass

Can the maintainer trust that what a tool finds without running the code is already found?

Look at: every check the project names that a tool makes without running the code, such as a linter
and, where the language has one, a type checker, run with the settings kept in the repository,
reports nothing on the code and its tests.

Why: a style checked by a tool is the same in every file, so the maintainer reads each part without
learning its writer's habits; a misused part of the language or a wrong type found by a tool needs
no test written for it and no review spent on it.

### B-16: One name for one thing

Can the maintainer find every place a thing is used by searching for its name?

Look at: each thing the code, its tests and its documents name, such as a function, a field, a file
or an idea, called by one name in all of them; a thing called by two names fails.

Why: a maintainer who meets two names takes them for two things, and a search for one finds only
half of where the thing is used.

### B-17: Comments say why

Can the maintainer learn from each comment why the code is as it is?

Look at: each comment other than a test's Given, When and Then; one whose words can be read back from
the code beside it fails.

Why: a comment that repeats the code is one more thing to keep in step with it, and drifts; the why
is the one thing the code cannot say.

### B-18: Each piece of logic in one place

Can the maintainer change a behavior by changing the one place it is written?

Look at: the code for the same lines, or the same lines with only names changed, in two places; any
such pair fails.

Why: logic written twice is changed in one place and left in the other, and the two drift apart
without any test failing.

### B-19: The tests run by the commands given

Can the maintainer run the whole test suite, and the coverage count, by the commands the README for
those who build the code gives?

Look at: each command run as written, in a fresh copy of the repository, runs every test and prints
the coverage count.

Why: a maintainer who must work out how to run the tests runs them less often, or runs only some.

## Usability

None: each thing that makes code and its tests easy to work on is one the opening names the
maintainer or whoever runs the code gets from them, so its item is in Benefit.

## Format

### F-1: Shape of each test

Does each test follow this shape, in the comment form of the code's language?

```python
def test_<what must happen, as one sentence>(self):
    # Given: <the situation>
    # When: <what is done>
    # Then: <what must be so>
```

- The name says what must happen, so a failing test's name alone says what broke.
- A test that tries the same behavior on several inputs keeps one Given, When and Then, and runs
  each input as its own subtest, so each failing input is named.

Why: the maintainer finds the intent of every test in the same place, and a tool listing the tests
lists what the code must do.
