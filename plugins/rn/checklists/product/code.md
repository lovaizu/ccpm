# Code

Code is used by whoever runs it and by whoever maintains it, a person or an AI. Whoever runs it gets
the behavior the requirements ask, and learns from each stop how to go on. Whoever maintains it
tells what each part does where it is written, changes one thing in one place, and trusts from its
checks passing that every behavior still holds.

Code serves them through two designs. The code is split into functions and modules by what each
takes on, and what comes from outside is checked where it comes in. Its tests are designed from the
requirements, by the techniques of the ISTQB Certified Tester Foundation Level syllabus v4.0.1,
chapter 4, so each fails when the behavior it holds breaks. How heavily each part is checked beyond
its tests, such as by property tests or mutation testing, is set by the architecture. The
development rules are the project's own rules for its code: the runtime and its versions, the
libraries and tools allowed, and the checks every change passes. The questions on the code are drawn
from Google's "What to look for in a code review" (google/eng-practices, CC BY 3.0). Code has no set
shape beyond what its language and the development rules give, so the format is the tests' alone.
Each test takes the shape of a case of the test design, so the design is the skeleton of the final
test code, and the maintainer finds what each test checks in the same place in every test.

## Format

```text
<For each test>  name: what must happen, as one sentence
                 body: Given: <the situation>, When: <what is done>,
                       Then: <what must be so>, each in plain words, as comments
```

Whoever writes the tests writes the cases and the data of the test design straight into the test
code in this form.

## Questions

### Q-1: The same behavior on any machine

Does the code give the behavior the requirements ask on a machine with only what the development
rules name, on the oldest runtime they name?

Why: what the code uses beyond the development rules is missing on some user's machine, and the code
fails there for a reason the user was never told.

### Q-2: A stop cleared by what it says

When the code stops, can whoever runs it go on by doing what the stop says?

Why: a stop that says only that something failed leaves the user to read the code. Each stop names
the input or condition that was wrong and an action the user can take with what they have, such as a
value to give instead. A stop that its own action does not clear leaves the run stuck.

### Q-3: Each input checked where it comes in

Is each thing taken in from outside, such as a file, an argument or another program's output,
checked where it comes in, before it is used?

Why: a wrong input that is used fails far from where it came in, or does harm, such as writing
outside the folder it was meant for.

### Q-4: What each part does, told where it is written

Can the maintainer tell what each module, function and test does, and what each name in it stands
for, without reading its body or its callers?

Why: a part its own lines do not tell sends the maintainer into its body and callers at every use. A
name or comment that says something else is believed. The reason behind a decision, and what a
regular expression or an algorithm does, is what the code alone does not show. A comment about how
the work went turns wrong as the code changes.

### Q-5: Only what a behavior needs now

Does each function, parameter, branch, option and comment serve a behavior the requirements ask now?

Why: each part is read, tested and kept true on every change, and when a guessed need comes, it
seldom has the shape that was guessed. A parameter its callers never vary, or a comment that says
what the line under it says, serves nothing.

### Q-6: One change in one place

Can the maintainer change one thing the code takes on in one place, with no other place left that
still holds the old one?

Why: a part that takes on two things is changed for one and breaks the other. Knowledge such as a
rule or a value written twice is fixed in one place and left wrong in the other. A thing with two
names is missed by a search for one of them. A file a run makes, such as Python's `__pycache__/`,
kept in the repository is a stale copy after the next change.

### Q-7: Every case of the requirements tested

Do the test cases cover the requirements: every case of each behavior they ask, each with its
expected value taken from the requirements? The cases are each group of inputs the behavior treats
alike, each edge between two groups, each combination of conditions and each change of state.

Why: a behavior the code leaves out cannot be broken in the code, so only cases listed from the
requirements show it missing. Faults gather at the edges, such as `<` written for `<=`, and in the
combinations and the changes of state. A test whose expected value was taken from the code it checks
passes whatever the code does.

### Q-8: Every test able to fail

With the cases covered, does every test fail when the behavior it checks is broken in the code?

Why: a test that cannot fail looks the same as one that works, and passing tests give trust only in
the behaviors they would fail on.

### Q-9: Each further check the architecture gives

Does each part pass each further check the architecture gives it, such as property tests or
mutation testing, as far as the architecture says?

Why: the architecture weighed each such check against what a failure of the part would cost the
user, so one left out leaves the part as lightly checked as the rest, against what was approved.

### Q-10: Each gap in a check named

Is each line, branch, input or surviving mutant left out of a check named beside it or in the
check's settings, with why?

Why: a gap with no reason beside it cannot be told from one left to make the run pass, so the next
maintainer keeps it.

### Q-11: A failure taken as one fault

When a check fails after a change, can the maintainer take it as a fault of that change, in the one
behavior the failing test names?

Why: a test that holds several behaviors leaves the maintainer to read it to learn which broke. A
test that fails on some runs and not others, such as one that reads the clock or needs another test
to run first, teaches them to rerun it, and then a real failure is rerun too. A check already
failing hides the failure a change brings.

### Q-12: Every check run on every change

Can the maintainer run every check on every change without waiting on it?

Why: a test run that takes minutes is run less often, and mutation testing runs the tests once for
each mutant, so its time grows with theirs.

### Q-13: The same behavior beside another run

Does the code give the behavior the requirements ask while another run of it goes on at the same
time?

Why: runs that write or hold one place, such as a file or a port, overwrite each other's work, and
the fault shows only when they happen to meet, so a test seldom finds it.

### Q-14: What a machine can see, shown on every change

Does the command that checks the work run a formatter, a linter and a type checker, and fail on what
they find?

Why: a tool finds the same thing every time and at once, where a maintainer reading for it finds
some of it, and what no tool shows is found on some changes only.
