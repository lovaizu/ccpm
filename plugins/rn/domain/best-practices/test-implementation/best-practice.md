# `test-implementation`

## Goal tree

- The developers learn from a test that runs the product whole, such as an E2E test, a performance test, or a benchmark of a prompt, what the product does, as each run ran as they meant and measured what they meant.
  - **C1** The test is built back from the decision that its report serves.
    - **N1** Does the report state the decision it serves, and give each value for it with the runs it's counted from and the place in each run's records? (Report)
    - **N2** Does each run keep, in a form a program reads, every record that a value of the report is counted or checked from, with what the run took? (Records)
  - **C2** Each value counts only runs that ran as meant, by checks that are themselves shown right.
    - **N3** Does a check by code show, for each run from its records, that it ran as the case means, and does the report count a value only from the runs that pass it? (Checks of a run)
    - **N4** Does each check by code, each judge, and each stand-in give the right result on kept records whose answer is known, before any run relies on it? (Checks and judges)
  - **C3** The test grows to its full size only on stages that held.
    - **N5** Did each stage, from one pilot run to the size that Test strategy sets, start only once the stage before showed each run running as meant and each value matching its records? (Stages)

## Template

[template.md](template.md)

## Inputs

- [product-vision](../product-vision/best-practice.md)
- [architecture](../architecture/best-practice.md)
- [test-design](../test-design/best-practice.md)

## Preconditions

- [test-design](../test-design/best-practice.md)
- [code](../code/best-practice.md)
- [prompt](../prompt/best-practice.md)

## Practices

### N1

Does the report state the decision it serves, and give each value for it with the runs it's counted from and the place in each run's records?

A developer decides from the report, such as whether a key result came closer, and trusts a value only where they can find in the records what it was counted from. ISTQB's test process ends in a test completion report that states the results against what the testing set out to show.

1. *While deciding.* Open the product vision, the architecture, and the test cases, and read each to its end: the key results with what a run records for each, the row of Test strategy for this test with what it measures or its criterion, and the case with its Given, When, and Then. The trace: `{inputs}` read to its end.
2. *While deciding.* Name the decision that the report serves, from the row of Test strategy, such as whether KR1.1 came closer for a benchmark, or whether a response time stays under its criterion for a quality.
3. *While deciding.* For each value the decision takes, write how it's counted from one run, from what the product vision says a run records, such as the share of runs whose order differs from the design.
4. *While making.* Make the report by code from the records: the decision, each value, the runs it's counted from, and for each counted run the place in its records, such as a file and a line, so that a developer checks each value against the record.

### N2

Does each run keep, in a form a program reads, every record that a value of the report is counted or checked from, with what the run took?

A value that no record holds can't be checked, and a run that started from another run's leftovers fails for a reason that isn't the product's. Anthropic's [demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) has each trial start from a clean environment and keep its full transcript.

1. *While deciding.* For each value of N1.3, list what a run must keep for it to be counted and checked: each event with its time, each result and output, and what the monitoring reads, such as each hook event, each command run, and the memory used.
2. *While making.* Make the harness start each run from a clean environment, such as a fresh home and a fresh copy of the repository, and keep each record of N2.1 in a folder of the run's own.
3. *While making.* Keep beside the records what the run took: the product's version, the model, the settings, and the case, so that two runs that differ show why.

### N3

Does a check by code show, for each run from its records, that it ran as the case means, and does the report count a value only from the runs that pass it?

A run that went otherwise than the case means, such as a stand-in that typed the wrong command, measures the test, not the product, and a run that only finished shows nothing of how it ran.

1. *While deciding.* From the case, list what a run that runs as meant does: each step, its input, its order, and its end, such as the stand-in typing the walkthrough's commands in order and the product's run ending by its own result.
2. *While making.* Write a check by code for each item of the list, read from the records, that names the run and the place where it went otherwise.
3. *While making.* Have the report count each value only from the runs that pass the checks, and list each other run apart with where it went otherwise.

### N4

Does each check by code, each judge, and each stand-in give the right result on kept records whose answer is known, before any run relies on it?

A check never seen failing may pass anything, and a judge or a stand-in that errs makes a value of the test, not of the product. Anthropic's evals guide prefers checks by code, gives each model judge one point, and calibrates it against people's judgment.

1. *While deciding.* Decide by code each point that the records show, such as a tool called, a file's content, or a command's output, and leave to a judge only what code can't decide, each judge with one point, its definitions, and a pass or fail result.
2. *While making.* Write each check's tests first, on the records of the pilot run that N5.2 keeps and on a copy of them broken in the way the check must catch, and see each test fail before you write the check.
3. *While making.* Where a judge has no messages that the developer has marked, end with `asks`, handing them the messages of its point from the pilot records, each with the mark you'd give it, since only their marks say what passes. Use the judge only once it gives each marked message their mark.
4. *While making.* For each stand-in or double that the test runs in place of a person or of something outside the product, read what it did in the pilot records, and check that it acts on its intent and on what it's given alone. Check too that it gives only what the real thing gives, by the real thing's documentation or a recorded run of it.

### N5

Did each stage, from one pilot run to the size that Test strategy sets, start only once the stage before showed each run running as meant and each value matching its records?

A large run that goes wrong mixes the test's faults with the product's, and costs a whole run to find either. Load testers start with a smoke test that checks the script works under minimal load, then step up the load, as [k6's test types](https://grafana.com/docs/k6/latest/testing-guides/test-types/) do.

1. *While deciding.* Set the stages, each larger than the one before: one run of one case, then each case once, then the number of runs or the load that Test strategy sets, such as a performance test's steps of load.
2. *While deciding.* Where Test strategy gives the rule for the number of runs in place of a number, as it does before the product runs, take three runs of each case as the last stage, the fewest in which one run that differs from the others shows. Add runs only to a case whose runs differ, until one more changes no case's count, and write the number reached in Test strategy.
3. *While making.* Run the first stage, and keep its records as the pilot records that N4 tests the checks on.
4. *While making.* Open the records of each stage, and check by N3 and N4 that each run ran as meant, and that each value of the report matches what you count by reading the records yourself.
5. *While making.* Where a stage doesn't hold, look first at the test's own parts, the harness, the checks, the judges, and the stand-ins, mend the one at fault, and run the stage again, changing one thing between two runs, the test or the product, never both. Take a stage where nearly every run fails as a fault of the test until its records show otherwise.
6. *While making.* Start the next stage only once the stage before held, and write each stage in Stages, with its size and the records that showed it held.
