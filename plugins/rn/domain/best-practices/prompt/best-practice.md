# `prompt`

## Goal tree

- An AI agent that gets the prompt for a request it's meant for does the task as the writer means, with only what its run gives it, on every run, and in cases the writer didn't foresee.
  - **C1** The host runs the prompt for exactly the requests it's for.
    - **N1** Do the name and the description let the host choose the prompt for each request it's for, and pass it over for a near request it isn't for? (Description)
    - **N2** Does the body do exactly the task that the description says, which the architecture gives the prompt's component? (Description, Goal)
  - **C2** The AI knows what the task is for, and has every fact it needs.
    - **N3** Does the goal say what the task is for, and how the AI checks that it has reached it? (Goal)
    - **N4** Does the prompt give every fact that the AI can't find or know on its own, and say where the rest lies? (Context)
  - **C3** The AI's steps lead to the task's purpose, also in cases that the writer didn't foresee.
    - **N5** Does each step lead toward what the goal says the task is for, with the last step reaching it? (Goal, Steps)
    - **N6** Does each rule give the reason from which the AI decides a case that the rule doesn't name? (Steps)
    - **N7** Does the prompt name the choices that are the user's, and how the AI hands them to the user? (Goal)
    - **N8** Does every line change what the AI does toward the task? (the whole)
  - **C4** What must hold holds on every run, whatever the AI's variance.
    - **N9** Does a program do each step that has one right result? (Steps)
    - **N10** Can the AI take every action that the steps call for with the tools it may use? (Tools, Steps)
    - **N11** Does the host refuse each action that lies outside the task? (Tools)
    - **N12** Does a hook hold each rule that must hold on every run, with a test of the hook both where the AI keeps the rule and where it breaks it? (Steps)
  - **C5** The caller can act on what the AI hands back.
    - **N13** Can the caller act on what comes back, in the form that the architecture's sequences hand on, without asking the AI anything further? (Steps, Output)
    - **N14** Can the person decide from the first lines of each message that the AI writes to them? (Output)
    - **N15** Does each claim that the AI reports rest on a check it ran on the real thing, with what it didn't check stated? (Output)
  - **C6** The writer knows from tests that the prompt works on every run and in real use.
    - **N16** Do the prompt's unit tests, each case run k times on the model its users run, and the end-to-end (E2E) tests of the product it's part of show the AI reaching the result on every run? (the whole)
    - **N17** Can the maintainer tell from a failed test's record whether the prompt or the test went wrong? (the whole)

## Template

[template.md](template.md)

## Inputs

- [architecture](../architecture/best-practice.md)

## Preconditions

- [architecture](../architecture/best-practice.md)

## Practices

### N1

Do the name and the description let the host choose the prompt for each request it's for, and pass it over for a near request it isn't for?

To pick a prompt for a request, the host reads only the name and the description of each of many prompts, so the prompt runs only where those two lead the host. Prompt writers write such a description as the [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) do: what the prompt does, then when to use it, in the third person and in the words users ask in.

1. *While deciding.* Open the architecture, and find the component that the prompt carries out: its line in Components, and its file in Directory structure, such as `agents/planner.md`. This best practice calls it the prompt's component, and the person of a user story the story's role, as the architecture does. The trace: `{inputs}` read to its end.
2. *While deciding.* Open the user stories whose sequences the prompt's component takes part in, and write down several requests that the prompt is for, each in a user's own words, from the way the story's role meets the product, such as `turn issue 12 into a plan`.
3. *While deciding.* Write down several near requests that the prompt isn't for, each from a user story that another component carries, in a user's own words.
4. *While making.* Write the prompt's name: the name of its file in Directory structure without the extension, such as `planner` for `agents/planner.md`. Where Directory structure gives no file, name it by what it does, in lowercase words joined by hyphens, such as `processing-pdfs`.
5. *While making.* Write the description in the third person: first what the prompt does, then `Use when` with the requests and situations of the first list, the main use first, such as `Extracts text and tables from PDF files. Use when the user mentions PDFs, forms, or document extraction.`
6. *While making.* Open the `name` and the `description` in the frontmatter of each other skill and agent of the product, in the folders that the architecture's Directory structure gives them. Where a prompt's file isn't written yet, take its component's line in Components in place of its description, since that line says what the prompt is to do.
7. *While making.* For each near request that names one of the host's own prompts, such as a built-in command or a bundled skill, open its description where the host lists them, such as the [commands reference](https://code.claude.com/docs/en/commands) of Claude Code.
8. *While making.* Where a near request fits the prompt's description as well as another's, add what sets the prompt apart, such as the kind of input it takes.
9. *While making.* Read only the name and the description, as the host does, and check that each request on the first list leads to the prompt and none on the second does.

### N2

Does the body do exactly the task that the description says, which the architecture gives the prompt's component?

The caller gets what the description promised, and the product gets what the architecture gives the prompt's component, only if the body does that same task.

1. *While deciding.* Take the task from the architecture: the line in Components that N1.1 found for the prompt's component, which says what the component alone decides, and each arrow from or to the component in Sequences, which says each step it takes and the data it hands on.
2. *While making.* Hold the description and the body each against the task that N2.1 took. Where the description says what the task holds and the body doesn't do it, add it to the body. Where the description says what lies outside the task, cut it from the description, and where the body does what lies outside the task, cut it from the body.

### N3

Does the goal say what the task is for, and how the AI checks that it has reached it?

The AI stops when its work looks done, so the prompt must say what the result is for, and give a check that separates done from looking done, as Claude Code's [best practices](https://code.claude.com/docs/en/best-practices#give-claude-a-check-to-run) give the AI something to run that comes back pass or fail.

1. *While deciding.* Write what the task is for in one sentence: whom the result serves, the story's role of each user story whose sequence the prompt's component takes part in, and what they gain by it, the story's benefit, such as `so that the developer gets a plan they can approve in one reading`.
2. *While deciding.* List what holds once the AI has done the task: each thing it hands on at its last arrow in Sequences, and each file or state it leaves, such as a plan written in its form.
3. *While deciding.* For each thing on the list, decide the check that shows it holds: a command that comes back pass or fail where the product has one, such as a schema check or a test, since its result doesn't rest on the AI's reading, or else what to open and what to compare it with, such as the plan against the request.
4. *While deciding.* Decide when the AI stops: once every check passes, or at a blocker it can't pass, which it hands back with what it found.

### N4

Does the prompt give every fact that the AI can't find or know on its own, and say where the rest lies?

The AI is able but new to this place, and gets nothing of the conversation that started it, so a fact the prompt leaves out becomes a guess, and a fact the AI would find anyway takes its attention from the rest.

1. *While deciding.* For each step, list the facts it needs. Take its inputs and where they lie from the arrows to the prompt's component in the architecture's Sequences and from its Directory structure, and the terms it uses from the data model. Take the rules of the place from the architecture's Principles and the rules they build on, such as the one folder a component writes in.
2. *While deciding.* Add each decision of your cut that the steps turn on and the architecture doesn't hold, such as a limit that the user set on what the prompt may change. Where a step needs a fact that neither the architecture, your cut, nor the repository gives, such as which branch the prompt may push to, end with `asks`, naming the fact and your recommendation, since a fact only the user holds becomes a guess when the prompt leaves it out.
3. *While deciding.* For each fact, ask the two questions of Claude Code's [best practices](https://code.claude.com/docs/en/best-practices#tell-claude-what-it-cant-see): could the AI find it by reading what its run gives it, and would it go and look? Where both answers are yes, leave the fact out. Where it could find it but wouldn't look, say where it lies, such as `The plan takes the form of plan.schema.json`. Where it couldn't find it, give the fact.

### N5

Does each step lead toward what the goal says the task is for, with the last step reaching it?

An AI that knows what each step's result is for chooses how to reach it, and follows the purpose where a step doesn't fit the case.

1. *While deciding.* Go through the steps that the arrows of the prompt's component in the architecture's Sequences give it, and ask of each whether an AI that holds the goal, as N3.1 wrote it, would know how to reach the step's result. Write a step only where it wouldn't, such as a check to run or a form to keep, and leave the rest to the AI.
2. *While deciding.* Give each step the result it leaves and what that result is for, such as `Run check.sh. Its exit code 0 is the check that the goal names.`
3. *While making.* Write the steps in the order their results must hold, such as in a numbered list.
4. *While making.* Check that a later step or the goal uses each step's result, and cut a step whose result nothing uses.
5. *While making.* Check that the last step leaves what the goal says the task is for.

### N6

Does each rule give the reason from which the AI decides a case that the rule doesn't name?

A rule that says what it's for lets the AI apply it where the writer meant it, and judge a case that no rule names, as Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance) say: the AI generalizes from the reason.

1. *While making.* Write each rule as what to do, in plain words, with its reason, such as `Your response is read aloud by a text-to-speech engine, so never use ellipses, which it can't pronounce` in place of `NEVER use ellipses`.
2. *While making.* Where a rule says always or never, say what the AI does when it can't keep the rule, such as `Never push to main. Where a push is needed, hand it back as a question.`
3. *While making.* In place of a list of edge cases, give the way of judging and a few examples that are like the real requests and unlike one another.
4. *While making.* Use no capitals or warnings for emphasis, since they make the AI apply the rule too widely.
5. *While making.* Think of a case that the rule doesn't name, read only the rule and its reason, and check that they lead where the writer would go. Where they don't, fix the reason.

### N7

Does the prompt name the choices that are the user's, and how the AI hands them to the user?

The user's purpose and intent stay the user's only if the AI hands them the choices that are theirs.

1. *While deciding.* Go through the steps, and each branch and each question put to the story's role in the architecture's Sequences, and mark each choice that's the user's: each action that's hard to undo, touches what others share, or destroys something, as the list in Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#balancing-autonomy-and-safety) gives, such as a force push, a comment on a pull request, or deleting a branch, and each choice between options that serve the purpose equally, where the AI has no ground to pick one. Leave every other choice to the AI.
2. *While making.* Name each of the user's choices in the step where it comes, with how it reaches the user. A prompt that runs as a subagent can't talk to the person, so it ends with the result that Sequences give for a question to its caller, with the point, the options, and its recommendation, such as `End with asks, naming the branch to push and your recommendation.` A prompt that runs in the main conversation asks the person in a message, as N14 says, one choice at a time.

### N8

Does every line change what the AI does toward the task?

Every line takes some of the AI's attention from the lines that matter, so prompt writers keep detail that the AI needs only in some runs in a file that it reads only then, as the [progressive disclosure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) of the skill authoring best practices does.

1. *While making.* For each line, ask whether removing it would change what the AI does. If not, cut it, such as `Read the files carefully`, which the AI does without the line.
2. *While making.* Move detail that the AI needs only in some runs to a file that the prompt links directly, and say in the prompt when to read it.

### N9

Does a program do each step that has one right result?

The AI's judgment varies from run to run, which suits a step with many good ways and fails a step with one right result, so the skill authoring best practices give such a step to a [utility script](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) that the AI runs.

1. *While deciding.* Read each step and ask whether it has one right result, such as a check or a file's form. For each that does, look in the architecture's Components for a program that gives that result, such as the product's own check, and take its path from Directory structure.
2. *While making.* Have each such step run its program by that path. Where Components holds no program for it and the deliverable is a folder that holds scripts, such as a skill's, write one there that gives the result on every run and handles its own errors, such as `scripts/validate.py`. Where the deliverable can't hold it, end with `asks`, naming the step and the program it needs, since a part that the architecture lacks is a decision of the architecture.

### N10

Can the AI take every action that the steps call for with the tools it may use?

Without the tool that an action needs, the AI can't take the step, however well the writer writes it.

1. *While deciding.* For each step, list each action it takes and the tool that takes it, including a script's command, such as `Bash(sh dev/scripts/check.sh)` for a step that runs the checks.
2. *While deciding.* Check each tool against the list that the prompt allows, such as the `tools` field of an agent's frontmatter. Where a step needs a tool that isn't on it, allow the tool if the action lies inside the task and N11 can keep the tool to the task. Otherwise, change the step so that it needs no such tool, such as having a script that the step runs fetch what the step needs.

### N11

Does the host refuse each action that lies outside the task?

A rule in words holds only while the AI follows it, so a slip of the AI can harm what lies outside the task unless the host refuses the action.

1. *While deciding.* Allow only the tools that N10's list needs, in the list that the host reads, such as the `tools` field of an agent's frontmatter.
2. *While deciding.* Where a tool it needs can also act outside the task, such as writing where the task only reads, add a rule that the host enforces: a deny rule where a permission pattern names the action, such as `Edit(./docs/**)`, in `permissions.deny` of the settings file that the architecture's Directory structure gives the host, such as `.claude/settings.json`, or else a hook, as N12 says. A prompt that ships in a plugin holds such a rule by a hook, since a plugin's files carry no permission rules.

### N12

Does a hook hold each rule that must hold on every run, with a test of the hook both where the AI keeps the rule and where it breaks it?

The AI keeps a rule on most runs, not on every run, while a rule that the host enforces holds on every run, as Claude Code's [best practices](https://code.claude.com/docs/en/best-practices#enforce-the-rules-that-cant-have-exceptions) hold a rule that can't have exceptions with a hook or a deny rule.

1. *While deciding.* List each rule of the steps that has no exception, where a single break would fail the users, such as a file that the AI must not write, and for each, a call where the AI keeps it and a call where it breaks it. Leave a rule with exceptions, such as a preference for a style, to the prompt's words.
2. *While deciding.* Hold each such rule with a deny rule where it limits what the AI may read, write, or run, and a permission pattern names it, such as `Read(./.env)`, since a deny rule holds in every permission mode. Write it in the settings file of N11.2. Hold it with a command [hook](https://code.claude.com/docs/en/hooks) where it's a step that must happen, where it turns on more than a pattern names, such as a write allowed only into the run's own file, or where the prompt ships in a plugin, as N11.2 says.
3. *While making.* For each rule that a hook holds, look in the architecture's Components for a hook that holds such rules, such as a guard, and add the rule to it by the path Directory structure gives. Where Components holds none and the deliverable is a folder that holds a hooks file, such as a plugin's `hooks/hooks.json`, write the hook there. Where the deliverable can't hold it, end with `asks`, naming the rule and the hook it needs, as for a program in N9.2.
4. *While making.* Test the hook on each case alone, with code in the AI's place: pipe the JSON that the host sends for the call into the hook's command, as the [hooks guide](https://code.claude.com/docs/en/hooks-guide) does, and check its exit code or the decision it prints, such as `echo '{"tool_name":"Write","tool_input":{"file_path":"src/gen/a.py"}}' | ./guard.sh` giving 2, which blocks the call, and 0 for a path the AI may write. Such a test runs in seconds without the model.

### N13

Can the caller act on what comes back, in the form that the architecture's sequences hand on, without asking the AI anything further?

The caller gets only what comes back, so a result that needs a follow-up question costs a round trip, and a result in a form the caller doesn't read stops the sequence there.

1. *While deciding.* Open each sequence that the prompt's component takes part in, and name the caller: the one whose arrow starts the component and who gets its answer. Write what the caller does with the result at its next arrow.
2. *While deciding.* Take what comes back from the arrow where the component answers the caller, with the data as the data model names it.
3. *While deciding.* List what the caller needs for its next move: the result, what the AI did, and what it didn't do and why.
4. *While deciding.* Choose the form by who reads it: a fixed form, such as JSON, where a script reads it, and short plain words where a person does.
5. *While making.* Check that a step makes each thing that the output names.

### N14

Can the person decide from the first lines of each message that the AI writes to them?

The person approves from the conclusion and its grounds, and reads further only where these leave them unsure. The [inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/) puts the conclusion first.

1. *While deciding.* From N7.1 and N13.4, list each message that the prompt has its AI write to a person: each of the user's choices that it asks in the main conversation, and each result that a person reads. Where it writes none, such as a subagent whose result a script reads, leave the prompt as it is.
2. *While making.* In the prompt's Output section, write the order of each message, with its reason: first the context and the conclusion, what the message asks or reports and why, then the grounds, then the purpose and what it should be, and the rest only once the person asks, since the person decides from the first lines.
3. *While making.* In the Output section, write the form of each message: a few plain sentences with no headings or labels, in short paragraphs of one point each.
4. *While making.* In the Output section, write the terms that the person uses, taken from the user stories and the README, and that the AI says a term of its own in everyday words or leaves it out.
5. *While making.* In the Output section, write that each message asks for one decision, alone on its last line, with one recommendation, such as `End with the one choice you need, and the option you recommend.`
6. *While making.* In the Output section, write what the AI adds where the person asks for more: the current state, with the place it rests on, and the gap between that and what it should be.

### N15

Does each claim that the AI reports rest on a check it ran on the real thing, with what it didn't check stated?

The caller can't tell a claim that the AI checked from one it guessed, and acts on both alike, so Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#minimizing-hallucinations-in-agentic-coding) have the AI open what a claim rests on before it makes the claim.

1. *While deciding.* From N13.3's list, take each claim that the AI reports, and name the check on the real thing that it rests on: the file to read, the command to run, or the record to open, a command that comes back pass or fail where the product has one, such as check.sh's exit code for `the checks pass`.
2. *While making.* In the step that makes each claim, write its check from N15.1 for the AI to run before it reports the claim, with the reason, such as `Run check.sh before you report that the checks pass, since the caller acts on the report as checked.` Write that no claim rests on memory, a guess, or another agent's summary.
3. *While making.* Where a check is a command, write that the AI judges it by its pass or fail result, such as the exit code, not by a few lines of its output.
4. *While making.* Where the AI reports on another agent's work, write that it opens the records and files that the agent names, and judges them against the task's purpose, not from the agent's summary.
5. *While making.* Where a claim names several items, such as every file changed, write that the AI checks each one, not a sample.
6. *While making.* In the Output section, write that the AI states what it checked, what it didn't, and why, so that the report never reads as covering more than it did.

### N16

Do the prompt's unit tests, each case run k times on the model its users run, and the end-to-end (E2E) tests of the product it's part of show the AI reaching the result on every run?

The writer knows a prompt only by what the AI does with it, where the AI's variance and the faults of the design show, so Anthropic's [demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) runs each task k times and counts it passed only where all k runs succeed, its pass^k.

1. *While making.* Run each case of the prompt once, in the folders that the architecture's Test strategy names for its test cases, on the model its users run, with the test's parts as they stand, and keep the record of the run beside the case, such as the JSON lines that `claude -p --output-format stream-json --verbose` writes. Nothing relies on its result yet: it's the first record, on which N17 checks the test's parts. The trace: `{case}` run.
2. *While making.* Once each part of the test gives the right result on the kept records, as N17.2 to N17.7 check it, run each case k times on the model its users run, with the k that Test strategy sets. A rule that must hold on every run rests on a hook, as N12 says, so the unit tests try the rest. The trace: `{tests}` run.
3. *While making.* Open the record of each run, and check from what the AI did, not from its last message, that every run reached the result.
4. *While making.* Where a run didn't reach the result, find the cause in its record, as N17 says, change the prompt only for a cause in the prompt, and run the case k times again.
5. *While making.* Open the E2E tests in the architecture's Test strategy: the command that its Tools line names, where its Passes when line says the result shows, such as a key result taken from the record of each run, and when its Runs line says they run, such as once every unit test and every integration test pass.
6. *While making.* Where every part that the E2E cases run has its body and the Runs line lets you start them, run the E2E tests by that command, and check from the result that Passes when names that the prompt, among the other parts, reaches the result on requests as big as real ones, since a unit test meets only the cases that its writer set up.
7. *While making.* Where a part that the E2E cases run is still a skeleton, such as one whose tests expect it to fail, or the Runs line leaves their start to someone else, such as the developer, leave them unrun, and say in your last message that they're unrun, why, and who runs them, since the caller takes what you don't name as checked.

### N17

Can the maintainer tell from a failed test's record whether the prompt or the test went wrong?

A test's own parts, its set-up, its doubles, its judges, and its checks, are code and prompts of their own, and can fail like the prompt. Anthropic's [demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) is how eval writers keep the two apart: they grade by code where they can, check a model grader against people's judgment, and read the records to tell a failure of the agent from a failure of the test.

1. *While deciding.* Open the Then of each test case of the prompt, in the folders that the architecture's Test strategy names, and for each point it names, ask whether the record of a run would show it, such as a tool called, a file's content, or a command's output. Decide by code each point that the record shows, and leave to a judge only what code can't decide, such as whether a plan reads as the request means.
2. *While making.* Build each check by code alone, test first, and run it on the first records that N16.1 kept, before any whole run relies on it, so that a whole run only confirms, and a failure in it points to the prompt.
3. *While making.* Give each judge one point, its definitions, and a pass or fail result.
4. *While making.* Where a judge has no messages that the maintainer has marked, end with `asks`, handing the maintainer the messages of its point from the first records, each with the mark you'd give it, since only the maintainer's marks say what passes. Their marks come back as the person's words when you're resumed.
5. *While making.* Run each judge on the marked messages, and use it only once it gives each message the maintainer's mark.
6. *While making.* Give the stand-in for the person only their intent, which the test case gives and the prompt never gets, and the whole of each message it answers.
7. *While making.* Read the stand-in's answers in the conversations of the first records, and check that each answer comes from the intent alone and invents nothing.
8. *While making.* Between two runs, change one thing, the prompt or a part of the test, never both.
9. *While making.* Where a test fails, open its record and look first at the test's own parts, and change the prompt only for a cause in the prompt.
