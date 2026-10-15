---
name: code
version: 0.1.0
---

# Code

Code is run and maintained. It gives the behavior expected of it, shows that it does, and reads
easily for its maintainer, who understands it and changes it at once and with confidence.

What the code must do is set by its README, its design and what calls it, such as the steps of a
prompt that runs it, here called its sources; this checklist judges the code and its tests against
them, from the code, the tests and their results.

## Benefit

### B-1: Tests hold what the code must do

Can the maintainer trust, from each test passing, that the code does a behavior its sources ask of
it?

Look at: for each test, the sentence of its sources that asks the behavior its Then checks, quoted;
a test for which no sentence can be quoted fails.

Why: a test written after the code is fitted to what the code does, so it passes a fault the code
was written with; a test written first, from what the code must do, holds the code to it.

### B-2: Each test can fail

When the behavior a test checks is broken in the code, does the maintainer learn of it from that
test failing?

Look at: break the line the test is about, run the test, see whether it fails, and put the line back.

Why: a test never seen failing may check nothing, and one that checks nothing looks the same as one
that works.

### B-3: A check tested on what it stops

For each check the code makes on what it receives, can the maintainer learn from a test that the
check stops an input it must stop?

Look at: for each such check, each way an input may lack what its sources say it
holds, such as a text with no words where they say what it asks, or hold what they say it must not,
in each form that takes, such as each form an ID may take; and a test that gives it one of each
and sees it stopped.

Why: a check tested only on what it lets through looks the same as no check at all, and one tested
on one form of what it must stop lets the other forms through.

### B-4: A check tested on what it lets through

For each check the code makes on what it receives, can the maintainer learn from a test that the
check lets through an input it must let through?

Look at: for each such check, a test that gives it an input it must let through and sees it used,
among them the input one change away from one it must stop, such as a value one short of a limit, or
a name that holds a stopped one as its first letters.

Why: a check tested only on what it stops may stop everything, and one tested only on inputs far
from what it stops may stop its neighbors.

### B-5: What each test checks, told in plain words

From each test read alone, can the maintainer tell what it checks without reading its code?

Look at: the test's Given, When and Then; one that names a function, a variable or another part of
the code fails.

Why: a maintainer who changes the code decides from the test whether a failure is a fault in the
code or a behavior that was meant to change; a test whose intent must be read out of its code is
kept or deleted by guess.

### B-6: Each Then checked in full

Can the maintainer trust that the code under each Then checks everything its words say?

Look at: each thing the Then's words name, matched to a check under it; a thing left without a
check fails.

Why: a Then whose code checks less than its words lets a fault pass under a test that reads as if it
caught it.

### B-7: Each check named by its Then

Can the maintainer change what a Then does not name without that test failing?

Look at: each check under the Then, matched to a thing its words name; a check left without one
fails.

Why: a check the words do not name fails on a change the test never meant to stop, and the
maintainer cannot tell from the test whether the change broke what it must do.

### B-8: Every branch run

Can the maintainer see, from the coverage report of the whole test run, that every branch of the
code is taken by some test?

Look at: the report, counting branches as well as lines, lists no branch and no line as not run.

Why: a branch no test takes may be broken without any test failing, and a missing test shows as a
branch not taken.

### B-9: Each line needed by a test

Can the maintainer trust that every line of the code is there for a behavior some test checks?

Look at: each line, and each condition a line holds, such as one of two conditions joined by `and`
or a bound on where a match may end, matched to the behavior a test's Then names that would break
without it; a line or a condition matched to none fails. Whether a line runs at all is the
coverage count's to tell, not this item's.

Why: a line no test needs is either a missing test or code with no purpose, and both are kept by
every later maintainer without knowing why.

### B-10: Lines left out of the count say why

For each line left out of the coverage count, can the maintainer tell from what is written beside it
which environment, one the tests cannot make, decides whether the line runs?

Why: a line left out without its reason cannot be told from a line left out to make the count pass,
and the next maintainer keeps the gap.

### B-11: A failing test learned from every push

Does the maintainer learn, from every push and without running anything by hand, of each test that
fails?

Look at: the repository's automated runs, which on every push run the whole test suite and fail on
a test that fails.

Why: a test left to be run by hand is skipped, and a skipped test lets a fault reach a user
unnoticed.

### B-12: A branch not run learned from every push

Does the maintainer learn, from every push and without running anything by hand, of each branch no
test takes?

Look at: the repository's automated runs, which on every push run the coverage count, counting
branches as well as lines, and fail on a branch or a line not run.

Why: a coverage count left to be run by hand is skipped, and a branch no test takes goes unnoticed
until its fault reaches a user.

### B-13: The same result on every run

Can the maintainer take each test failure as a fault, because each test gives the same result
whenever it is run, alone or with the others, in any order?

Look for: a test that reads the clock, the network, or the machine it runs on; a test that leaves
files or state behind for the next one; a test that needs another to run first. Any one fails.

Why: a test that fails on some runs and not on others teaches the maintainer to rerun it rather than
read it, and then a real failure is rerun too.

### B-14: Run with only what the README names

Can whoever runs the code run it with only the runtime, libraries and tools its README names?

Look at: what the code imports and calls, against what the README names.

Why: what the code uses beyond them is missing on some user's machine, and the code fails there for
a reason the user was never told.

### B-15: Run on the oldest version it supports

Can users on the oldest version of the runtime the README says the code supports run it?

Look at: the tests, run on that version by the repository's automated runs, passing.

Why: code written on a newer version uses what the older one lacks, and fails for the users on it.

### B-16: Stopped before a wrong input is used

When whoever runs the code gives it something wrong, such as a file, an argument or what another
program hands it, are they stopped before the code uses it?

Look at: each place the code takes in something from outside, against the first place it uses it; a
check that stops one lacking what its sources say it holds, or holding what they say
it must not, lies between them.

Why: a wrong input used fails far from where it came in, or does harm, such as writing outside the
folder it was meant for, and the user cannot tell from the failure what they gave wrong.

### B-17: A stop says what went wrong

When the code stops, can whoever runs it tell from what it says what went wrong?

Look at: each message the code gives when it stops names the input or the condition that was wrong.

Why: a stop that says only that something failed leaves the user to read the code to learn what
they gave wrong.

### B-18: A stop says what to do

When the code stops, can whoever runs it tell from what it says what to do about it?

Look at: each message the code gives when it stops names an action to take, such as a value to give
instead or how to install a tool that is missing.

Why: a user who knows what went wrong but not how to put it right is left to work out the fix from
the code.

### B-19: Slips found by a tool

Can the maintainer trust that what a tool finds without running the code, such as a misused part of
the language or a wrong type, is already found?

Look at: every check the project names that finds such slips without running the code, such as a
linter's rules for faults and, where the language has one, a type checker, run with the settings
kept in the repository, reports nothing on the code and its tests.

Why: a slip a tool finds on every run needs no test written for it and no review spent on it, and a
reader finds it only sometimes.

### B-20: One name for one thing

Can the maintainer find every place a thing is used by searching for its name?

Look at: each thing the code, its tests and its documents name, such as a function, a field, a file
or an idea, called by one name in all of them; a thing called by two names fails.

Why: a maintainer who meets two names takes them for two things, and a search for one finds only
half of where the thing is used.

### B-21: Comments say why

Can the maintainer learn from each comment why the code is as it is?

Look at: each comment other than a test's Given, When and Then; one whose words can be read back from
the code beside it fails.

Why: a comment that repeats the code is one more thing to keep in step with it, and drifts; the why
is the one thing the code cannot say.

### B-22: Each piece of logic in one place

Can the maintainer change a behavior by changing the one place it is written?

Look at: the code for the same lines, or the same lines with only names changed, in two places; any
such pair fails.

Why: logic written twice is changed in one place and left in the other, and the two drift apart
without any test failing.

### B-23: The tests run by the command given

Can the maintainer run the whole test suite by the command the README for those who build the code
gives?

Look at: the command run as written, in a fresh copy of the repository, runs every test.

Why: a maintainer who must work out how to run the tests runs them less often, or runs only some.

### B-24: The coverage count run by the command given

Can the maintainer get the coverage count by the command the README for those who build the code
gives?

Look at: the command run as written, in a fresh copy of the repository, prints the coverage count of
lines and branches over the whole test suite.

Why: a maintainer who must work out how to count coverage counts it less often, and a branch no test
takes is found late.

### B-25: A failure names the behavior that broke

When a test fails, can the maintainer tell from that failure alone which one behavior broke?

Look at: for each test, the behaviors whose fault would make its checks fail, each matched to the
sentence of its sources that asks it; a test whose checks would fail on behaviors
asked by two sentences fails.

Why: a test that holds several behaviors, failing, leaves the maintainer to read its code to learn
which of them broke.

### B-26: Each behavior tested on its own code

Can the maintainer test each behavior without running the code that only another behavior needs?

Look at: for each test, the code it runs against the code its Then rests on; a part of the code
that runs only to reach the behavior, and that a test of another behavior is about, fails, such as
a test of how one input is checked that runs the whole program to reach that check, or a test of
the order the parts run in that does each part's own work where a stand-in would show the order.

Why: a test that runs another behavior's code fails when that behavior breaks, so its failure no
longer says which broke, and every run pays the time that code takes.

### B-29: The least input and setup that shows it

From each test's input and setup, can the maintainer tell what the behavior rests on, because
nothing in them could be left out with the behavior still shown?

Look at: leave out each part of the test's input and setup, run the test, and put the part back; a
part whose leaving out still has the test pass with its Then true fails.

Why: input and setup beyond what the behavior needs hide which part of them the behavior rests on,
and every run pays to make them.

### B-30: Each behavior asked has a test

For each sentence of its sources that asks a behavior of the code, can the maintainer
learn from some test that the code does it?

Look at: each such sentence, matched to a test whose Then checks the behavior it asks; a sentence
left without one fails, whichever file holds the code that does it.

Why: the tests passing give trust only in the behaviors they hold, and a test chosen from the lines
not yet run holds the lines, not what the design asks of them.

## Usability

None: each item that is not a set shape is one without which the maintainer or whoever runs the
code loses something the opening names they get, so it is in Benefit.

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

### F-2: One style in every file

Do the code and its tests follow the layout style the project names, so that the tool that checks
it, such as a linter's style rules or a formatter, run with the settings kept in the repository,
reports nothing?

Why: a style checked by a tool is the same in every file, so the maintainer reads each part without
stopping at how it is written, and no review spends time on it.
