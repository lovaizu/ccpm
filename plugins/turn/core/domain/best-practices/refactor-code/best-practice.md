# refactor-code

## Goal

The maintainer is a person or an AI who comes to change the code at any time after it is written. The maintainer changes the code quickly without breaking another behavior. They understand each part on one reading, and they find the one place where the change belongs.

## Intents

- **Q1** (the whole): After the code's structure changes, does each caller get every behavior it got before, whether the caller is a person, a script or other code?
- **Q2** (the whole): Whatever line the maintainer reads, code or comment, would they lose something they need if it were gone?
- **Q3** (the whole): When the maintainer reads any name in the code, can they say what it holds or does without going to where it is defined?
- **Q4** (the whole): Each time the maintainer meets a name, can they tell rightly whether it names a thing they have already met, and which one?
- **Q5** (the whole): With one rule or one design decision to change, can the maintainer find the one place that holds it and make the whole change there?
- **Q6** (the whole): When the maintainer reads any function once from the top, with nothing from outside it but the names it uses, can they say in one sentence what it does?
- **Q7** (the whole): When the maintainer moves from one module to another, do they find each kind of thing done the same way, so that each difference they meet is one the code needs?
- **Q8** (the whole): Where code looks wrong or roundabout, can the maintainer learn right there why it is so, before they change it?

## Practices

### Q1: After the code's structure changes, does each caller get every behavior it got before, whether the caller is a person, a script or other code?

**Thinking**: The structure changes in small steps, and each step keeps every behavior. The tests from before the change check each step. No step changes a behavior.

**Steps**

1. Run the tests before any change, and begin only when every one passes.
2. Where a behavior the change will touch has no test, write a test of what the code does now, and see it pass.
3. After each small change of structure, such as a rename or a moved function, run the tests. Where a test fails, undo the change and make a smaller one.
4. Leave each test's expected result as it was, and change a test's call only where a name it uses was renamed.
5. Where a behavior looks wrong, keep the behavior and its test. Return it as a point about what the code does, rather than change it here.

### Q2: Whatever line the maintainer reads, code or comment, would they lose something they need if it were gone?

**Thinking**: Each line earns its place by what the maintainer would lose without it. What gives the maintainer nothing comes out, and version control keeps it.

**Steps**

1. Fold into its caller each function or layer that only passes a call on. Drop each parameter to which every caller gives the same value, and use that value inside.
2. Keep a comment that says what the code cannot say plainly, such as what a regular expression matches.

### Q3: When the maintainer reads any name in the code, can they say what it holds or does without going to where it is defined?

**Thinking**: A name says in whole words what it holds or does, so the maintainer reads each line without going to a definition.

**Steps**

1. For each name, write in a few words what it holds or does, without looking at its definition. Then look at the definition, and flag the name where the two differ.
2. Make a name say more the farther from its definition it is read.

### Q4: Each time the maintainer meets a name, can they tell rightly whether it names a thing they have already met, and which one?

**Thinking**: Each thing has one name, the word its users and documents already use for it, and each name names one thing.

**Steps**

1. List the things the code handles, and for each the names the code gives it.

### Q5: With one rule or one design decision to change, can the maintainer find the one place that holds it and make the whole change there?

**Thinking**: The code writes each rule or design decision once, in the module whose job it is. The code does not tie together things unrelated in meaning, however alike they look.

**Steps**

1. For each rule or decision the code holds, such as a limit, a format or a path, list every place that writes it.
2. Where a shared function takes flags so that each caller gets its own path, split it into one function for each rule.
3. Where code reaches into another module's insides, have it use what that module offers its callers.
4. Where the code truly cannot keep a rule in one place, say at each place where the other places are, such as in a comment beside it.
5. Pick one rule, imagine that it changed, and count the places that would change. Mend the code until that count is one.

### Q6: When the maintainer reads any function once from the top, with nothing from outside it but the names it uses, can they say in one sentence what it does?

**Thinking**: A function does one thing at one level, and takes what it uses as its inputs. Its reader then holds in mind only what the function says. A long function reads as calls to steps, each named for what it does.

**Steps**

1. Read each function, test functions included, once from the top, and write in one sentence what it does.
2. Flag a function whose sentence needs an "and", or for which the reader had to read another body.
3. Join back two functions that cannot be understood apart.
4. Write a clever construct in its plain form.

### Q7: When the maintainer moves from one module to another, do they find each kind of thing done the same way, so that each difference they meet is one the code needs?

**Thinking**: The code does each kind of thing one way throughout. That way is the one the code already has, the nearest code first, unless a better way replaces it everywhere. A difference then means a real difference.

**Steps**

1. List the kinds of thing the code does in many places, such as reporting an error, checking an input, reading a file, or laying out a module or a test.
2. For each kind, gather each way the code does it.
3. Where a place needs another way, say why beside it, such as in a comment.

### Q8: Where code looks wrong or roundabout, can the maintainer learn right there why it is so, before they change it?

**Thinking**: Where the code cannot say why it is so, the reason stands where the maintainer meets the code, such as a limit outside the code or a way tried and dropped.

**Steps**

1. Read each line as a maintainer who knows the language but not the purpose, and flag code that looks wrong, roundabout or more than it needs.
2. For each, first make the code say it plainly, where it can.
3. Check each comment against the code beside it, and correct or remove one that no longer holds.
