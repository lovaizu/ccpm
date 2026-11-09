# `refactor-code`

## Goal

Maintainers, people or AI agents who come to the code at any time, change it quickly without breaking another behavior.

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | Every caller gets the same behavior after a change of structure. |
| C2 | The maintainer understands each part in one reading. |
| C3 | The maintainer finds the one place where a change belongs. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | After a change of structure, does each caller, whether a person, a script, or other code, get every behavior it got before? | the whole |
| N2 | C2 | Does each line, whether code or a comment, give the maintainer something they need? | the whole |
| N3 | C2 | Does each name say what it holds or does, without its definition? | the whole |
| N4 | C2 | Does each thing have one name, and does each name refer to one thing? | the whole |
| N5 | C2 | Can the maintainer say in one sentence what each function does after one reading from the top? | the whole |
| N6 | C2 | Where code looks wrong or roundabout, does it say why right there? | the whole |
| N7 | C3 | Does the code write each rule or design decision once, in the module that has that job? | the whole |
| N8 | C3 | Does the code do each kind of thing the same way throughout, with a reason beside each difference? | the whole |

## Practices

### N1

After a change of structure, does each caller, whether a person, a script, or other code, get every behavior it got before?

**Thinking**

A change of structure is safe only if no caller can tell it happened. Martin Fowler's [refactoring](https://refactoring.com) changes the structure in small steps, each of which keeps every behavior, checked by the tests from before the change. Decide each step by asking whether the tests can tell you it kept every behavior. If a behavior that the change reaches has no test, write one first. If a step is too big to check, make a smaller one.

**Steps**

1. Run the tests before any change, and begin only when every one passes. The trace: `{tests}` run.
2. Where a behavior that the change reaches has no test, write a test of what the code does now, and see it pass.
3. After each small change of structure, such as a rename or a moved function, run the tests. Where a test fails, undo the change, and make a smaller one.
4. Leave each test's expected result as it was, and change a test's call only where the change renamed a name it uses.
5. Keep a behavior that looks wrong, along with its test. Report it as a point about what the code does, instead of changing it here.

### N2

Does each line, whether code or a comment, give the maintainer something they need?

**Thinking**

Every line costs the maintainer reading time. For each line, ask what the maintainer would lose without it. Remove what gives them nothing, since version control keeps it. Fold into its caller each function or layer that only passes a call on, and drop each parameter to which every caller gives the same value. Keep a comment that says what the code can't say plainly, such as what a regular expression matches.

### N3

Does each name say what it holds or does, without its definition?

**Thinking**

A name that says what it holds lets the maintainer read each line without going to a definition. For each name, write in a few words what it holds or does without looking at its definition, then compare with the definition, and rename it where the two differ. Make a name say more the farther from its definition the maintainer reads it.

### N4

Does each thing have one name, and does each name refer to one thing?

**Thinking**

A maintainer who meets two names takes them for two things, and one name used for two things merges them. List the things the code handles, and the names the code gives each. For each thing, keep the word its users already use, such as the one in its documents. If two names refer to one thing, keep one. If one name refers to two things, give one of them another name.

### N5

Can the maintainer say in one sentence what each function does after one reading from the top?

**Thinking**

A function that does one thing at one level, and takes what it uses as inputs, asks its reader to hold only what it says. Read each function, test functions included, once from the top, and write in one sentence what it does. If the sentence needs `and`, or you had to read another body, split the function, or make it take what it reached for as an input. A long function reads as calls to steps, each named for what it does. Join back two functions that the reader can't understand apart, and write a clever construct in its plain form.

### N6

Where code looks wrong or roundabout, does it say why right there?

**Thinking**

A maintainer who doesn't know why odd code is so may undo what it's there for. Read each line as a maintainer who knows the language but not the purpose, and mark code that looks wrong, roundabout, or more than it needs. For each, first make the code say it plainly where it can. Where it can't, state the reason right there, such as a limit outside the code or a way tried and dropped.

**Steps**

1. Check each comment against the code beside it, and correct or remove one that no longer holds.

### N7

Does the code write each rule or design decision once, in the module that has that job?

**Thinking**

A rule written in several places changes in some of them and not the others. Write each rule or design decision once, in the module that has that job, and leave apart things that only look alike but differ in meaning. For each rule or decision the code holds, such as a limit, a format, or a path, list every place that writes it, and keep one.

**Steps**

1. Where a shared function takes flags so that each caller gets its own path, split it into one function for each rule.
2. Where code reaches into another module's insides, have it use what that module offers its callers.
3. Where the code truly can't keep a rule in one place, say at each place where the others are, such as in a comment beside it.
4. Pick one rule, imagine that it changed, and count the places that would change. Change the code until that count is one.

### N8

Does the code do each kind of thing the same way throughout, with a reason beside each difference?

**Thinking**

When the code does each kind of thing one way, a difference means a real difference. List the kinds of thing the code does in many places, such as reporting an error, checking an input, reading a file, or laying out a module or a test. For each kind, gather each way the code does it, and keep the one the code already uses most, the nearest code first, unless a better way replaces it everywhere. Where a place needs another way, say why beside it, such as in a comment.
