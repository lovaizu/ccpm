# code

## Goal

The maintainer is a person or an AI who takes the code over. The maintainer changes what the code does. They know that whoever runs the code still gets each behavior its specification asks for. They also know that whoever runs it learns how to put right anything wrong that comes from outside.

## Inputs

- [architecture](../architecture/best-practice.md)

## Parts

- **manifest**: What the maintainer needs to set the code up on a fresh machine and run its tests: everything the code needs to run, with the versions it runs on, and how to run the tests.
- **module-opening**: For each module, a few words on what this module alone decides, at the place the maintainer meets first when they open the module.
- **interface**: Each name a module offers to others, with everything a caller needs to call it without reading its body: the types it takes and gives, what it gives, what it expects of what it takes and each way it refuses.
- **body**: The code under each interface that gives the behavior.
- **tests**: Tests of the specification's cases, one test for each case, so the maintainer can tell which test checks which case and which code. Each test has a name that says the behavior it checks, and shows the situation, what is done and what must be so.

## Intents

- **Q1** (manifest, tests): When the maintainer sets the code up on a fresh machine from only what the code gives for its setup, and runs the tests again and in any order, do they see the tests pass each time, so that a failing test points at the code and never at the machine or the order?
- **Q2** (module-opening): With one behavior to change, can the maintainer tell which module to open from what each module says it alone decides, without reading the modules' bodies, so that they change the behavior in one place?
- **Q3** (interface): When the maintainer calls a name that another module offers, can they write a call that works from the name's interface alone, without reading its body, so that the body can change behind the interface without breaking its callers?
- **Q4** (interface, body): For each behavior the code has, can the maintainer name the case of the specification that needs it, so that the code holds no behavior that no one asked for?
- **Q5** (body): When something the code takes from outside is wrong, can whoever ran the code put it right from only what the code tells them, with nothing left half done, so that a fault from outside never leaves them stuck or their data half changed?
- **Q6** (tests): For each case the specification names, its edges and refusals included, can the maintainer point to the one test that checks it, and tell the case from that test's name, so that they know which case a failing test breaks?
- **Q7** (interface, tests): When the maintainer changes a body and its callers still get what its interface says, do the tests still pass, so that they can improve a body without fear?
- **Q8** (body, tests): When the maintainer breaks the behavior a test checks, does that test fail, so that a broken behavior never goes unnoticed?
- **Q9** (the whole): With only the code and its specification, can the maintainer make a change the specification asks for, and know from the tests that every other behavior still holds?

## Practices

### Q1: When the maintainer sets the code up on a fresh machine from only what the code gives for its setup, and runs the tests again and in any order, do they see the tests pass each time, so that a failing test points at the code and never at the machine or the order?

**Thinking**: What the code gives for its setup names everything the code needs. Each test sets up and clears everything it uses, and a real tool it runs does only what the test asks of it. A test's result then rests on the code alone, not on the machine or on when a tool's own work runs.

**Steps**

1. For each real tool the tests run, such as git, find each thing it does on its own beyond the call, such as reading the machine's settings or starting maintenance in the background, and turn it off in the test's own settings.
2. Set the code up on a clean machine or container, from what the code gives for its setup alone.
3. Add to what the setup reads each thing the setup or the tests found missing, such as a runtime or a library, with the versions the code runs on.
4. Run the tests several times, and in a shuffled order.

### Q2: With one behavior to change, can the maintainer tell which module to open from what each module says it alone decides, without reading the modules' bodies, so that they change the behavior in one place?

**Thinking**: Each module alone decides one thing that the specification leaves to the code. The module says that thing briefly where the maintainer meets it first, such as at its top.

**Steps**

1. Where the module cannot say that thing briefly, split the module.
2. Take a behavior that the specification might change, and read only what the modules say they decide. Check that what they say points to one module. Where it does not, rewrite what the modules say, or move the decision.

### Q3: When the maintainer calls a name that another module offers, can they write a call that works from the name's interface alone, without reading its body, so that the body can change behind the interface without breaking its callers?

**Thinking**: The interface tells a caller everything they need to make the call. The caller then need not read the body, and the body can change behind the interface.

**Steps**

1. Choose the names other modules may use, and mark every other name as internal.
2. Say for each name the types it takes and gives, such as in its signature where the language allows.
3. Write beside it, such as in a doc comment, what it gives, what comes back when there is nothing to give, what it expects of what it takes, what else it changes, and each way it refuses a right call.
4. Leave out of that what the types already say.
5. Have someone who has not read the body write a call from the interface alone, and run the call. Where the call fails or they had to guess, add what was missing.

### Q4: For each behavior the code has, can the maintainer name the case of the specification that needs it, so that the code holds no behavior that no one asked for?

**Thinking**: The code gives only the behaviors the specification asks for, in the form its cases ask for now. The maintainer then carries nothing that no one needs.

**Steps**

1. For each option, mode and case the code handles, name the case of the specification that asks for it.

### Q5: When something the code takes from outside is wrong, can whoever ran the code put it right from only what the code tells them, with nothing left half done, so that a fault from outside never leaves them stuck or their data half changed?

**Thinking**: The code checks what comes from outside, such as arguments, files, settings and the replies of other programs, where it comes in and before the code does anything. When the code refuses an input, its message tells whoever ran the code which program refused, what was wrong, where, and what the code accepts.

**Steps**

1. At that place, read the input into the form the inside of the code uses. Check its type and format, and whether its value makes sense for what the code is to do.
2. Refuse a value that the code cannot read, rather than guess it. Catch only the error you mean to handle.
3. Write each check so that it runs however the code is run. Do not write it as a check that can be turned off, such as an assert.
4. Give the code each wrong input that the specification names. Read each message as the one who ran the code, and check that they can put the input right from the message alone.

### Q6: For each case the specification names, its edges and refusals included, can the maintainer point to the one test that checks it, and tell the case from that test's name, so that they know which case a failing test breaks?

**Thinking**: The tests come from the specification's cases, and they come before the code. Each test checks one behavior, so it says which case it checks.

**Steps**

1. List every case the specification names: the usual one, each edge and each refusal.
2. Name each test for the behavior it checks. Where the name needs "and", split the test.
3. Write each test so its reader sees the situation, what is done and what must be so, such as in three parts: Given, When and Then.
4. Write each expected value from the specification, not from what the code gives.
5. Run each test before you write its code, and see it fail.
6. Compare the list of cases with the tests, and check that each case points to one test.

### Q7: When the maintainer changes a body and its callers still get what its interface says, do the tests still pass, so that they can improve a body without fear?

**Thinking**: The tests call the code as its callers do, so they fail only where a caller would break.

**Steps**

1. Use the real parts where they run fast and wholly inside the test, and a stand-in only for what is slow or outside it.
2. Change a body without changing what its interface says, and run the tests. Rewrite each test that fails so that it calls the code through the interface.

### Q8: When the maintainer breaks the behavior a test checks, does that test fail, so that a broken behavior never goes unnoticed?

**Thinking**: A test is worth the faults it catches. So each test checks the result that its case asks for, and a broken behavior makes the test fail.

**Steps**

1. Find each line or branch no test runs, such as by counting them while the tests run, and add a test for each.
2. Change the code in small ways, such as with a mutation testing tool. For each change under which the tests still pass, add or mend the test of the behavior that the change breaks.
3. Run the code over many inputs that the specification allows, such as with property-based tests. Keep each input that the code fails on as a fixed test.

### Q9: With only the code and its specification, can the maintainer make a change the specification asks for, and know from the tests that every other behavior still holds?

**Thinking**: Only a change that someone new to the code makes shows whether the code lets them change it and trust the result.

**Steps**

1. Have someone who has not seen the code, a person or an AI, set it up and make one change the specification asks for, with only the code and its specification.
2. Note each body they read to find the place or to write a call, and each time they could not tell whether another behavior broke.
3. Have them run the changed code with a wrong input, and note where its message did not tell them how to put it right.
4. Trace each note to the part whose question it fails, and mend that part.
