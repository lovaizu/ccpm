# `plugin`

## Goal

The developers build a Claude Code plugin whose roles work together to make what its users need.

## Template

[template](template)

## Inputs

- [architecture](../architecture/best-practice.md)

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | Each role holds everything its job needs, and nothing else. |
| C2 | Every run follows the same steps, and nothing passes unchecked. |
| C3 | The person who uses the plugin decides only what's theirs, and reads each question as the role wrote it. |
| C4 | The work reaches its users as they need it, and each run improves the next. |
| C5 | The plugin installs, runs, and updates cleanly on every user's machine. |
| C6 | The developers know that the plugin works before users try it. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | Does each file sit where the architecture's Directory structure puts its job: the entries in the form Claude Code fixes, and the knowledge of the work in `domain/`? | domain, skills, agents, hooks, scripts |
| N2 | C1 | Does each role receive its whole part before its first call, with every file the part names found wherever Claude Code installs the plugin? | agents, skills, domain |
| N3 | C1 | Does each role's part hold only what the role must do and which practices it carries out, with no copy of their steps? | domain |
| N4 | C1 | Does each job have a role of its own, as the architecture's Components names it, with only the tools and the context that the job needs? | agents |
| N5 | C2 | Does a machine check what passes between the main conversation and each role at each start, resume, and end, in forms that carry the data the architecture's sequences hand on? | domain |
| N6 | C2 | Does each file that the plugin reads keep a form that a script checks? | domain |
| N7 | C2 | Where a run goes in fixed moves, does code hold the order of the moves and keep the run's state in a file? | hooks |
| N8 | C2 | Does a hook hold each step, and each rule of the architecture's principles, that an instruction alone doesn't, by stopping a role that drifts and giving it the step again? | hooks |
| N9 | C2 | Does each check report a pass, a failure, and a check that couldn't run as three different results? | hooks, scripts |
| N10 | C2 | Does a script or a tool check everything that a machine can check, leaving to the AI only what no machine can? | scripts |
| N11 | C3 | Does the main conversation hold the talk with the person, have the roles do the work, and check each role's result before it acts on it? | skills, agents |
| N12 | C3 | Does the plugin count a point that's the caller's, such as a merge, as approved only by the caller's own act? | skills |
| N13 | C3 | Does each role ask the person only what's theirs to decide, one question at a time, with a recommendation? | domain |
| N14 | C3 | When something outside the work stops a role, such as a permission or a tool, does the role ask for it and go on with the rest? | domain |
| N15 | C3 | Does the plugin talk with the person in their language, and write the repository in the repository's language? | domain |
| N16 | C4 | Before the work reaches its users, does a role that didn't make it check it as the users would? | agents |
| N17 | C4 | After each run, does the plugin find what fell short and why, and put each lesson where later runs use it? | skills, domain |
| N18 | C5 | Does the plugin write each file where its user chooses whether git keeps it, and nothing in the plugin's own folder? | scripts |
| N19 | C5 | Does the plugin need nothing on the user's machine beyond a runtime that's already there and its standard library? | scripts, hooks |
| N20 | C5 | Does the marketplace keep code that more than one of its plugins needs in one place? | hooks, scripts |
| N21 | C5 | Where another plugin already does a job, does the plugin use that plugin's part instead of writing its own? | .claude-plugin, hooks |
| N22 | C5 | Do the plugin and the marketplace pass Claude Code's check of their manifests? | .claude-plugin |
| N23 | C5 | Does each release have a version and a changelog entry that tell users what changed for them? | .claude-plugin, CHANGELOG.md |
| N24 | C5 | Does the plugin ship a README made for its users by the readme best practice? | README.md |
| N25 | C6 | Does each test level say what of Claude Code runs real and what a double replaces, as the architecture's Tests sets? | skills, agents, hooks |

## Practices

### N1

Does each file sit where the architecture's Directory structure puts its job: the entries in the form Claude Code fixes, and the knowledge of the work in `domain/`?

A developer finds each job where the structure puts it, and what the plugin knows outlives the agent it runs on. The method is Alistair Cockburn's [hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/), which keeps the core apart from the adapters that connect it to the outside.

1. *While deciding.* Take each file's place from the architecture's Directory structure, and decide where each file goes by asking whether Claude Code fixes its form: a file whose form it fixes is an entry, and the knowledge of the work goes in `domain/`. The trace: `{inputs}` read to its end.
2. *While making.* Give skills, agents, hooks, and scripts the form Claude Code fixes, each named as its caller calls it, such as the command a person types, and have each hand the job to the file in `domain/` that does it.
3. *While making.* Keep the knowledge of the work in `domain/`, in one folder with no folders split by role, and name no tool of an agent there, such as the Agent tool or `AskUserQuestion`: only the entries name them, so that two entries for one job can't drift apart.
4. *While making.* Keep what only the developers need, such as the tests and the architecture, outside the plugin's folder, since installing copies only that folder.
5. *While making.* Search `domain/` for the name of each tool of an agent, and move each line it finds to the entry that uses the tool.

### N2

Does each role receive its whole part before its first call, with every file the part names found wherever Claude Code installs the plugin?

A role works from all it has to do only when it holds its whole part from its first call. The method is the hybrid strategy of Anthropic's [effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), which puts what an agent always needs into its context up front, as Claude Code does with `CLAUDE.md`.

1. *While deciding.* Have each entry name its part, and have the guard or the skill deliver the part whole at the start, since Claude Code makes an agent's body its system prompt and reads no other file into it, and after `/compact` a part that a skill names comes back whole, while the skill's own body survives only as the summary retells it.
2. *While making.* Have each entry's body say that the plugin's folder is `${CLAUDE_PLUGIN_ROOT}` and name the role's part in `domain/`, since Claude Code replaces `${CLAUDE_PLUGIN_ROOT}` with the plugin's folder only in an entry's own body, not in what the Bash tool runs or in a file that Read reads, as [environment variables](https://code.claude.com/docs/en/plugins/manifest-reference#environment-variables) says.
3. *While making.* Have the part name each file as `${CLAUDE_PLUGIN_ROOT}/<path>`, which the role reads with the folder that the entry's body gave.
4. *While making.* Have the guard give an agent its part whole as the agent starts, through the `SubagentStart` hook's `additionalContext` with the folder filled in.
5. *While making.* Have the skill's body make the main conversation read its part whole first.

### N3

Does each role's part hold only what the role must do and which practices it carries out, with no copy of their steps?

A role follows whatever its part says, so steps copied into the part drift from the practices they came from, and the role follows the copy. The method is the Don't Repeat Yourself (DRY) principle of Andrew Hunt and David Thomas's *The Pragmatic Programmer*, under which each piece of knowledge has one authoritative place.

1. *While deciding.* Make a role's part say what the role has to do, what a machine can see once it's done, what it's given, the best practice and the conditions whose practices it carries out, and what it gives as it ends, as `domain/role.md` shows. The steps of the work are those practices, and the guard holds them one by one.
2. *While making.* Search each part for a numbered list, and replace each step it holds with the condition whose practice the step carries out.

### N4

Does each job have a role of its own, as the architecture's Components names it, with only the tools and the context that the job needs?

A role starts in a fresh context, so nothing from other work leads it astray, as [subagents](https://code.claude.com/docs/en/sub-agents) says, and it can change only what its tools reach. The method is the principle of least privilege of Jerome Saltzer and Michael Schroeder's [The Protection of Information in Computer Systems](https://doi.org/10.1109/PROC.1975.9939).

1. *While deciding.* Take the roles from the architecture's Components, and decide each role's tools by asking which context and which tools its job needs: jobs that need different context or tools get a role each, an agent whose `tools` name only what the job needs.
2. *While deciding.* Have roles that run at the same time each work in a workspace of their own, such as a git worktree and a temporary folder that no other role writes.
3. *While deciding.* Join their results only through the one who started them, since two makers in one workspace overwrite each other's files unseen.
4. *While making.* Set each agent's `tools` to the tools that its part's practices use.
5. *While making.* Set each agent's `background: true`, since the guard counts a start once its role ends.

### N5

Does a machine check what passes between the main conversation and each role at each start, resume, and end, in forms that carry the data the architecture's sequences hand on?

A machine can check a fixed form, while words written freely leave each reader to guess. The method is Bertrand Meyer's [Design by Contract](https://doi.org/10.1109/2.161279), which checks what each side of a call must give as the call starts and as it returns.

1. *While deciding.* Keep each role's input and output to JSON Schemas in `domain/`, drawn from `domain/role-in.schema.json` and `domain/role-out.schema.json`.
2. *While deciding.* Have a role start with one JSON line of run values, the values that the guard holds its calls to.
3. *While deciding.* Have each form carry the data that the architecture's sequences hand on at that start, resume, or end, as the data model names it.
4. *While deciding.* Have a role resume with a message that holds the main conversation's own grounds, and the person's words word for word where it has them.
5. *While deciding.* Have a role end by giving a result, a fixed word such as `asks` or `done`, by Lane's result script.
6. *While deciding.* Have a role's last message begin with `For the person:` where it holds a question for the person.
7. *While deciding.* Have a role that judges a work by questions write its answers with the lines of the work that meet each question.
8. *While deciding.* Have each role's result name the IDs of the practice items it took, of the conditions its part names. The orchestrator's result names those it takes while it settles the decisions, and the generator's those it takes while it makes the deliverable.
9. *While deciding.* Have the guard stop an end whose result leaves out an item.
10. *While making.* Write each role's two schemas, and have the script that a role runs before it gives its result hold the role's answers to them.

### N6

Does each file that the plugin reads keep a form that a script checks?

A script finds a file out of form before anyone reads it. The method is Jim Shore's [fail fast](https://doi.org/10.1109/MS.2004.1331296), which stops at the first sign of a fault instead of carrying it on.

1. *While deciding.* Decide each file's form by how the plugin uses it. A document that the plugin rewrites, such as a design tree, keeps a form that a script checks, such as JSON with a [JSON Schema](https://json-schema.org). A record that it only adds to, such as Lane's calls, is an append-only log, such as [JSON Lines](https://jsonlines.org), so that adding a record never rewrites what's there. A file that shows the form of a deliverable, such as a template or an example, keeps the deliverable's own format, since a template in another format shows a form that the deliverable can't take.
2. *While deciding.* Have the guard check the nodes around each change to a tree, so that the parts around it don't drift.
3. *While making.* Have each script that reads a file hold it to its schema.
4. *While making.* Write a unit test that gives each such script a file out of form, and check that the script fails with the schema's error.

### N7

Where a run goes in fixed moves, does code hold the order of the moves and keep the run's state in a file?

Code follows a course the same way every time, while a conversation that's told the course drifts from it. The method is the split of Anthropic's [building effective agents](https://www.anthropic.com/engineering/building-effective-agents) between a workflow, which runs on code paths set beforehand, and an agent, which directs its own course.

1. *While deciding.* Ask whether a run goes in fixed moves. If it does, its routes keep the course. If the course changes with what the run finds, the orchestrator's part keeps the course instead.
2. *While making.* Write the routes, and the lanes that the practices of N8 and N16 call for, in the plugin's proposal, in the form that [the lanes](../../../../lane/docs/lanes.md#the-proposal) gives. The trace: `{proposal}` made.
3. *While making.* Run `lay.py print` on the proposal, read what it prints, and check in it that it found each role's part. The trace: `python3 ${dependency:lane}/scripts/lay.py print {proposal}` run.
4. *While making.* Lay the proposal with `lay.py write`. Lane lays the routes in `hooks/lanes.json`, gives the main conversation each next start from the role that ended and the result it gave, and keeps each run's state in a file, so that a compacted or stopped conversation goes on from its last move. The trace: `python3 ${dependency:lane}/scripts/lay.py write {proposal}` run.

### N8

Does a hook hold each step, and each rule of the architecture's principles, that an instruction alone doesn't, by stopping a role that drifts and giving it the step again?

A hook runs every time, while an instruction is only advice. The method is Shigeo Shingo's poka-yoke, from *Zero Quality Control*, which stops a process at a slip and signals it, as Claude Code's [best practices](https://code.claude.com/docs/en/best-practices#enforce-the-rules-that-cant-have-exceptions) do for a rule that can't have exceptions.

1. *While deciding.* For each step of the practices, and each rule of the architecture's principles, ask whether its drift shows in a tool call or in how a role ends. If it does, lay a lane on it: its hook stops what would break the step and gives the role the step again. The plugin's hooks are its guard, laid by [Lane](../../../../lane/README.md) from the plugin's proposal as lanes and routes.
2. *While deciding.* Hold what's hard to undo by branch protection or permission rules.
3. *While deciding.* Keep all hooks in `hooks/hooks.json`. Hooks there fire on the main conversation's calls with no `agent_type`, and on a role's with the role's, as [hooks](https://code.claude.com/docs/en/hooks) says. A plugin's agent ignores `hooks`, `mcpServers`, and `permissionMode` in its own frontmatter, as [plugin agents](https://code.claude.com/docs/en/plugins/components#frontmatter-fields-in-plugin-agents) says, and a `SubagentStop` hook in a skill's frontmatter didn't fire in a trial on Claude Code 2.1.318.
4. *While deciding.* Have each role read in full each best practice its part names before its first change.
5. *While deciding.* Lay a lane on that read by the read's trace.
6. *While making.* Write a hook's message as the role's next instruction, as Claude Code delivers it: the sentence of the step or the item that the role broke or skipped, and why it matters, as work to do on the deliverable. Never name the check's own record, such as the result's list of items, which the role would mend instead of doing the step.
7. *While making.* Name in each step of the best practices that the roles use a trace that a machine can check, such as a command run, a file read, or a test made, for the lane that N7.2 writes in the proposal.

### N9

Does each check report a pass, a failure, and a check that couldn't run as three different results?

A reader takes a check that stays silent when it couldn't check for one that found nothing. The method is the [fail securely](https://owasp.org/www-community/Fail_securely) principle, under which a check that can't decide denies.

1. *While deciding.* End each check in one of three results: no problem, a problem, or couldn't check, such as the exit codes 0, 1, and 2.
2. *While deciding.* Decide beforehand what follows each result.
3. *While deciding.* Have a hook whose command fails stop the call, by `onFailure: block`.
4. *While deciding.* Have a hook that finds no Python 3.9 stop each call of the plugin's own roles and say why.
5. *While deciding.* Count a skipped test, a job that didn't run, or a command that failed as no pass.
6. *While making.* Write a unit test for each of the three results of each check, which checks that what you decided to follow the result follows it.
7. *While making.* Write an architecture test that runs each hook with its script missing.

### N10

Does a script or a tool check everything that a machine can check, leaving to the AI only what no machine can?

A tool finds the same thing every time, at once, while an AI finds only some, and spends a round on each. The method is the split of Claude Code's [best practices](https://code.claude.com/docs/en/best-practices#deterministic-and-non-deterministic-instructions) between what the harness runs every time, such as tests and a type check, and what the model weighs.

1. *While deciding.* Take the conditions that the best practice of each role's work sets.
2. *While deciding.* For each condition, ask whether a machine can see it. If it can, give it to a script, a hook, or the project's own tools, such as a formatter, a linter, or a type checker. Leave to an AI only what no machine can check.
3. *While making.* Give each condition that a machine can see to a script that the role runs before it gives its result.

### N11

Does the main conversation hold the talk with the person, have the roles do the work, and check each role's result before it acts on it?

Only the main conversation can ask the person, and a subagent's last message reaches only the one who started it, as [subagents](https://code.claude.com/docs/en/sub-agents#available-tools) says. The method is the orchestrator-workers pattern of Anthropic's [building effective agents](https://www.anthropic.com/engineering/building-effective-agents), in which a central model breaks the task down, hands each piece to a worker, and joins their results.

1. *While deciding.* Have the skill make the main conversation the orchestrator, which holds the talk with the person: it asks them each point that's theirs, one at a time with a recommendation, and settles the rest by the purpose and the best practices.
2. *While deciding.* Have the orchestrator make nothing itself, so that its conversation keeps room for the talk and the judgments.
3. *While deciding.* Have it start each role that the routes name for the work, and resume a role by SendMessage, which keeps the role's whole conversation, as [resume subagents](https://code.claude.com/docs/en/sub-agents#resume-subagents) says.
4. *While deciding.* Have it check each result against the purpose and the best practices before it acts on it, since a role's result is a claim and the role may have read the work wrong, and send a role back with the ground where the result falls short.
5. *While deciding.* Have an AI call the plugin by the same skill, since its own orchestrator also runs in the main conversation.
6. *While making.* Write an architecture test that runs the orchestrator's part through a start, a result sent back, and a resume of each role, and check that each prompt holds only the run values, the person's words, and the orchestrator's grounds.

### N12

Does the plugin count a point that's the caller's, such as a merge, as approved only by the caller's own act?

An AI that decides for the caller leaves them answerable for what they never saw, and an approval that an agent can give itself stops nothing. The method is the separation of privilege of Jerome Saltzer and Michael Schroeder's [The Protection of Information in Computer Systems](https://doi.org/10.1109/PROC.1975.9939), under which an act needs a key that the one who asks for it doesn't hold.

1. *While deciding.* List the points that are the caller's, such as what's hard to undo, like a merge, and make each count as approved only by the caller's own act, such as a skill that the AI can't call.
2. *While making.* Set `disable-model-invocation: true` in the frontmatter of each skill that approves such a point.

### N13

Does each role ask the person only what's theirs to decide, one question at a time, with a recommendation?

A point settled before the work doesn't come back as rework, and a question about what the person doesn't care about spends their time on the plugin's job. The method is Matt Pocock's [grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md).

1. *While deciding.* For each point the work needs, ask first whether facts can settle it, and then whether the purpose and the best practices settle it. Where facts can, the role finds them itself and shows each fact the work rests on. Where the purpose and the best practices do, the role decides it. It reports the decision at the end. Only a point that's left goes to the person: one point per message, with a recommendation.
2. *While making.* Write an architecture test that resumes the role with an answer, and check that its next message holds one point.

### N14

When something outside the work stops a role, such as a permission or a tool, does the role ask for it and go on with the rest?

The person clears a missing permission or tool in a moment, while a way around it leaves the work checked on other terms than its purpose set. The method is the checkpoint of Anthropic's [building effective agents](https://www.anthropic.com/engineering/building-effective-agents), where an agent pauses for human feedback when it meets a blocker.

1. *While deciding.* When something outside the work stops a role, have the role ask for it, go on with the rest meanwhile, and not look for a way around.
2. *While making.* Write an architecture test whose double of Claude Code denies a call, and check that the role's message asks for it.

### N15

Does the plugin talk with the person in their language, and write the repository in the repository's language?

The person approves what they read, and others read the repository later.

1. *While making.* Talk with the person in their language.
2. *While making.* Write the repository in the repository's language, or English where it has none.
3. *While making.* Show the person exactly what the plugin writes.

### N16

Before the work reaches its users, does a role that didn't make it check it as the users would?

The maker reads what it meant, not what it wrote, so a role that didn't make the work checks it first, given only what the work's users have. The method is the separate evaluator of Anthropic's [harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps).

1. *While deciding.* Ask whether the users get something that no machine can check. If they do, an evaluator checks it, unless the caller reads the whole work to approve it, such as a plan, since the caller is then its first reader.
2. *While deciding.* Have the evaluator answer each condition as met, with the lines that meet it, or as not met, with what the users still lack, since a hunt for defects finds something in every work and never ends. Have it never say how to fix the work, since the maker holds the sources and decides the fix.
3. *While making.* Give the evaluator's agent only the tools to read the work and write its answers.
4. *While making.* Lay a lane that holds the evaluator to reading only what the work's users have.

### N17

After each run, does the plugin find what fell short and why, and put each lesson where later runs use it?

A lesson met once should improve every later run, and the user chooses what leaves their project. The method is the blameless postmortem of Google's [Site Reliability Engineering](https://sre.google/sre-book/postmortem-culture/), which finds each cause in the records and puts its fix where it stops a repeat.

1. *While deciding.* After the caller approves the work, have the main conversation ask once where the run fell short of its goal or cost the user time.
2. *While deciding.* Have it find why in the records, quoting each cause.
3. *While deciding.* For each lesson, ask whether it's the project's own or general. A lesson of the project's own goes into the project's rules. A general lesson goes to the plugin's repository as an issue, only when the user says yes.
4. *While making.* Have the orchestrator's part read the run's records with Read before it ends.
5. *While making.* Have each lesson quote the cause it names from those records.

### N18

Does the plugin write each file where its user chooses whether git keeps it, and nothing in the plugin's own folder?

One folder named after the plugin lets the user decide with one line of `.gitignore` whether git keeps it. The method is the split of the [Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/fhs.shtml) between static files, which no program writes, such as those in `/usr`, and variable files, placed by how long they last: state that programs keep between runs in `/var/lib`, and files that no run may count on finding again in `/tmp`.

1. *While deciding.* For each file the plugin writes, ask how long it must last. What the user may keep goes in `.<plugin>/<yyyymmdd>-<name>/` at the root of the repository, since an agent reads without asking only inside the working folder, as [working directories](https://code.claude.com/docs/en/permissions#working-directories) says. What the plugin uses only while it runs, its tests' files among them, goes in `<plugin>/<yyyymmdd>-<name>/` in the folder that `tempfile.gettempdir()` gives, which `TMPDIR` moves, and the system clears it. What must outlast an update goes in `${CLAUDE_PLUGIN_DATA}`. Nothing goes in `${CLAUDE_PLUGIN_ROOT}`, which changes with each update.
2. *While making.* Search the plugin for each path it writes, and check that each lies under `.<plugin>/`, the system's temporary folder, or `${CLAUDE_PLUGIN_DATA}`.

### N19

Does the plugin need nothing on the user's machine beyond a runtime that's already there and its standard library?

A plugin that needs a package the user lacks fails on their machine.

1. *While deciding.* Where users' machines may lack other runtimes or packages, run only on a runtime that's already there and its standard library, such as Python 3.9 or later, which is wherever git is, and install no packages.
2. *While making.* Run the checks in CI on the oldest runtime that the plugin supports and on the newest, such as Python 3.9 and the newest Python, since only a run on the oldest shows that the code still runs there, and only a run on the newest shows what a new release breaks.

### N20

Does the marketplace keep code that more than one of its plugins needs in one place?

Developers write, test, and fix code kept in one place only once. The method is the Don't Repeat Yourself (DRY) principle of Andrew Hunt and David Thomas's *The Pragmatic Programmer*, under which each piece of knowledge has one authoritative place.

1. *While deciding.* Keep code that more than one plugin needs in the plugin whose job it does, such as Lane's hooks.
2. *While deciding.* Have the others take it in through a relative symbolic link, since installing copies a link's target into the plugin, as [symlinks in a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace#share-files-within-a-marketplace-with-symlinks) documents.
3. *While making.* Run a check for copied code, such as `pylint --enable=duplicate-code`, over the marketplace's Python.

### N21

Where another plugin already does a job, does the plugin use that plugin's part instead of writing its own?

The other plugin runs as its makers built and tested it, and nobody writes it again.

1. *While deciding.* Ask whether the job is one role of the other plugin or its whole run. For one role, a route names it as `<dependency>:<role>`, and the main conversation starts it as one of its own and puts its questions to the person, while the other plugin's guard holds its calls. For the whole run, a route names its skill as `<dependency>:<skill>`, and the main conversation calls the skill as one move, which ends once the other plugin gives its result. Meanwhile the other plugin's guard holds the conversation, and this plugin's guard checks nothing, since two guards on one conversation would stop each other's moves.
2. *While making.* Name the other plugin in `dependencies` of the plugin's `plugin.json`.
3. *While making.* Run `lay.py print` on the routes that name the dependency.

### N22

Do the plugin and the marketplace pass Claude Code's check of their manifests?

A malformed manifest fails every user at install, so each plugin and the marketplace pass Claude Code's own validator.

1. *While making.* Run `claude plugin validate --strict` on the plugin and on the marketplace. The trace: `claude plugin validate {deliverable} --strict` run.

### N23

Does each release have a version and a changelog entry that tell users what changed for them?

Users decide whether to update by what changed for them, and get an update only when the version rises. The method is [Semantic Versioning](https://semver.org) for the version and [Keep a Changelog](https://keepachangelog.com) for the entry.

1. *While deciding.* Release only when whoever decides what reaches users says so.
2. *While deciding.* Let the largest change that users see decide which part of the version rises.
3. *While making.* Keep `version` once, in `plugin.json`, in Semantic Versioning, since `plugin.json` wins over the marketplace entry.
4. *While making.* Give each change that users notice one line in the CHANGELOG, with why it helps them.
5. *While making.* Tag each release `<plugin>--v<version>` with `claude plugin tag --push`, since a dependency's version range resolves against these tags.
6. *While making.* List each release in the marketplace and the root README.

### N24

Does the plugin ship a README made for its users by the readme best practice?

A user learns from the README what they achieve with the plugin and how.

1. *While making.* Make `README.md` as a deliverable of its own, of the kind [readme](../readme/best-practice.md), from the plugin's product vision and before the plugin's architecture.
2. *While making.* Keep it in the plugin's folder, so that it reaches each user with the plugin.

### N25

Does each test level say what of Claude Code runs real and what a double replaces, as the architecture's Tests sets?

Every path should hold on every push, and the trials should meet what users meet. The method is Gerard Meszaros's [test double](https://martinfowler.com/bliki/TestDouble.html), from *xUnit Test Patterns*, which stands in a test for a real part that the test can't run.

1. *While deciding.* Take the test levels from the [architecture best practice](../architecture/best-practice.md), and what each runs real for this plugin from the architecture's Tests.
2. *While deciding.* Run no prompt, skill, or agent alone on a model at any level, since a trial of one role alone meets only the cases its developer set up, and finds no fault that a real request brings out. In its place, the guard holds each rule of a role's steps that must hold on every run, and the architecture tests run the guard on each path, with a double in each role's place. The cost: a fault in a prompt shows only in a product vision trial.
3. *While making.* Write the architecture tests with a double of Claude Code that runs each hook's entry and script in the test's own process, as a new process of Python would run it, and sends what its documentation says or what a recorded run of the real Claude Code showed.
4. *While making.* Run the architecture tests with the unit tests before each push.
5. *While making.* Check each configuration written by hand, such as `hooks.json`, with `claude plugin validate`, since no test runs its commands.
6. *While making.* Start each Claude Code of a product vision trial on a configuration folder of its own that holds only the plugins under test, with the developer's login as `CLAUDE_CODE_OAUTH_TOKEN`, as [multiple accounts](https://code.claude.com/docs/en/authentication#log-in-with-multiple-accounts) says, since the developer's own settings would change what the trial tries.
7. *While making.* Have the stand-in answer each request to allow a call from what the screen shows, as a person would.
8. *While making.* Compare what each double made from a recorded run sends with that recorded run of the real Claude Code on the same call, and check that it sends what the real one sent.
