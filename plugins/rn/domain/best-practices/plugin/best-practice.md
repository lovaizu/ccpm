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
| C3 | The person decides only what's theirs, and reads each question as the role wrote it. |
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

**Thinking**

A developer finds each job where the structure puts it, and what the plugin knows outlives the agent it runs on. Alistair Cockburn's [hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/) keeps the core apart from the adapters that connect it to the outside. Take each file's place from the architecture's Directory structure, and decide where each file goes by asking whether Claude Code fixes its form. Skills, agents, hooks, and scripts take the form Claude Code fixes, each named as its caller calls it, such as the command a person types, and hand the job to the file in `domain/` that does it. `domain/` holds the knowledge of the work in one folder, with no folders split by role, and names no tool of an agent, such as the Agent tool or `AskUserQuestion`: only the entries name them. Two entries for one job then can't drift apart. Keep what only the developers need, such as the tests and the architecture, outside the plugin's folder, since installing copies only that folder.

**Steps**

1. Search `domain/` for the name of each tool of an agent, and move each line it finds to the entry that uses the tool.

### N2

Does each role receive its whole part before its first call, with every file the part names found wherever Claude Code installs the plugin?

**Thinking**

A role works from all it has to do only when it holds its whole part from its first call. Three facts of Claude Code decide how. It makes an agent's body its system prompt and reads no other file into it. It replaces `${CLAUDE_PLUGIN_ROOT}` with the plugin's folder only in an entry's own body, not in what the Bash tool runs or in a file that Read reads, as [environment variables](https://code.claude.com/docs/en/plugins/manifest-reference#environment-variables) says. After `/compact`, a part that a skill names comes back whole, while the skill's own body survives only as the summary retells it. So each entry names its part, and the guard or the skill delivers the part whole at the start.

**Steps**

1. Have each entry's body say that the plugin's folder is `${CLAUDE_PLUGIN_ROOT}` and name the role's part in `domain/`, and have the part name each file as `${CLAUDE_PLUGIN_ROOT}/<path>`.
2. Have the guard give an agent its part whole as the agent starts, through the `SubagentStart` hook's `additionalContext` with the folder filled in, and have the skill's body make the main conversation read its part whole first.
3. Run `lay.py print` on the plugin's proposal, and check in what it prints that it found each role's part. The trace: `python3 ${dependency:lane}/scripts/lay.py print {proposal}` run.

### N3

Does each role's part hold only what the role must do and which practices it carries out, with no copy of their steps?

**Thinking**

A role follows whatever its part says, so steps copied into the part drift from the practices they came from, and the role follows the copy. A role's part says what the role has to do, what a machine can see once it's done, what it's given, the best practice and the conditions whose practices it carries out, and what it gives as it ends, as `domain/role.md` shows. The steps of the work are those practices, and the guard holds them one by one.

**Steps**

1. Search each part for a numbered list, and replace each step it holds with the condition whose practice the step carries out.

### N4

Does each job have a role of its own, as the architecture's Components names it, with only the tools and the context that the job needs?

**Thinking**

A role starts in a fresh context, so nothing from other work leads it astray, as [subagents](https://code.claude.com/docs/en/sub-agents) says. Take the roles from the architecture's Components, and decide each role's tools by asking which context and which tools its job needs. Jobs that need different context or tools get a role each: an agent whose `tools` name only what the job needs. Roles that run at the same time each work in a workspace of their own, such as a git worktree and a temporary folder that no other role writes. Their results join only through the one who started them, since two makers in one workspace overwrite each other's files unseen.

**Steps**

1. Set each agent's `tools` to the tools that its part's practices use, and `background: true`, since the guard counts a start once its role ends.

### N5

Does a machine check what passes between the main conversation and each role at each start, resume, and end, in forms that carry the data the architecture's sequences hand on?

**Thinking**

A machine can check a fixed form, while words written freely leave each reader to guess. Keep each role's input and output to JSON Schemas in `domain/`, drawn from `domain/role-in.schema.json` and `domain/role-out.schema.json`. A role starts with one JSON line of run values, the values that the guard holds its calls to. Each form carries the data that the architecture's sequences hand on at that start, resume, or end, as the data model names it. It resumes with a message that holds the main conversation's own grounds, and the person's words word for word where it has them. It ends by giving a result, a fixed word such as `asks` or `done`, by Lane's result script, and its last message begins with `For the person:` where it holds a question for the person. A role that judges a work by questions writes its answers with the lines of the work that meet each question.

**Steps**

1. Write each role's two schemas, and have the script that a role runs before it gives its result hold the role's answers to them.

### N6

Does each file that the plugin reads keep a form that a script checks?

**Thinking**

A script finds a file out of form before anyone reads it. Decide each file's form by how the plugin uses it. A document that the plugin rewrites, such as a design tree, keeps a form that a script checks, such as JSON with a [JSON Schema](https://json-schema.org). A record that it only adds to, such as Lane's calls, is an append-only log, such as [JSON Lines](https://jsonlines.org), so that adding a record never rewrites what's there. A file that shows the form of a deliverable, such as a template or an example, keeps the deliverable's own format, since a template in another format shows a form that the deliverable can't take. The guard checks the nodes around each change to a tree, so that the parts around it don't drift.

**Steps**

1. Have each script that reads a file hold it to its schema, and write a unit test that gives the script a file out of form and checks that the script fails with the schema's error.

### N7

Where a run goes in fixed moves, does code hold the order of the moves and keep the run's state in a file?

**Thinking**

Code follows a course the same way every time, while a conversation that's told the course drifts from it. Ask whether a run goes in fixed moves. If it does, its routes keep the course. Lane lays them in `hooks/lanes.json` from the plugin's proposal, and gives the main conversation each next start from the role that ended and the result it gave. Lane keeps each run's state in a file, so that a compacted or stopped conversation goes on from its last move. If the course changes with what the run finds, the orchestrator's part keeps the course instead.

**Steps**

1. Write the routes in the plugin's proposal, run `lay.py print` on it and read what it prints, and then run `lay.py write`. The trace: `python3 ${dependency:lane}/scripts/lay.py write {proposal}` run.

### N8

Does a hook hold each step, and each rule of the architecture's principles, that an instruction alone doesn't, by stopping a role that drifts and giving it the step again?

**Thinking**

A hook runs every time, while an instruction is only advice. The plugin's hooks are its guard, laid by [Lane](../../../../lane/README.md) from the plugin's proposal as lanes and routes. For each step of the practices, and each rule of the architecture's principles, ask whether its drift shows in a tool call or in how a role ends. If it does, lay a lane on it: its hook stops what would break the step and gives the role the step again. Branch protection or permission rules hold what's hard to undo. Keep all hooks in `hooks/hooks.json`. Hooks fire on the main conversation's calls with no `agent_type`, and on a role's with the role's, as [hooks](https://code.claude.com/docs/en/hooks) says. A plugin's agent ignores `hooks`, `mcpServers`, and `permissionMode` in its own frontmatter, as [plugin agents](https://code.claude.com/docs/en/plugins/components#frontmatter-fields-in-plugin-agents) says, and a `SubagentStop` hook in a skill's frontmatter didn't fire in a trial on Claude Code 2.1.318.

**Steps**

1. Name in each step of the best practices that the roles use a trace that a machine can check, such as a command run, a file read, or a test made, and lay a lane on it in the proposal. The trace: `{proposal}` made.

### N9

Does each check report a pass, a failure, and a check that couldn't run as three different results?

**Thinking**

A reader takes a check that stays silent when it couldn't check for one that found nothing. End each check in one of three results: no problem, a problem, or couldn't check, such as the exit codes 0, 1, and 2. Decide beforehand what follows each, and test it. A hook whose command fails stops the call, by `onFailure: block`, and a hook that finds no Python 3.9 stops each call of the plugin's own roles and says why. A skipped test, a job that didn't run, or a command that failed counts as no pass, as [fail securely](https://owasp.org/www-community/Fail_securely) says.

**Steps**

1. Write a unit test for each of the three results of each check, and an architecture test that runs each hook with its script missing.

### N10

Does a script or a tool check everything that a machine can check, leaving to the AI only what no machine can?

**Thinking**

A tool finds the same thing every time, at once, while an AI finds only some, and spends a round on each. Take the conditions that the best practice of each role's work sets. For each condition, ask whether a machine can see it. If it can, give it to a script, a hook, or the project's own tools, such as a formatter, a linter, or a type checker. Leave to an AI only what no machine can check.

**Steps**

1. Give each condition that a machine can see to a script that the role runs before it gives its result.

### N11

Does the main conversation hold the talk with the person, have the roles do the work, and check each role's result before it acts on it?

**Thinking**

Only the main conversation can ask the person, and a subagent's last message reaches only the one who started it, as [subagents](https://code.claude.com/docs/en/sub-agents#available-tools) says. So the skill makes the main conversation the orchestrator, which holds the talk with the person: it asks them each point that's theirs, one at a time with a recommendation, and settles the rest by the purpose and the best practices. It makes nothing itself, so that its conversation keeps room for the talk and the judgments. It starts each role that the routes name for the work, and resumes a role by SendMessage, which keeps the role's whole conversation, as [resume subagents](https://code.claude.com/docs/en/sub-agents#resume-subagents) says. A role's result is a claim, and the role may have read the work wrong. So the orchestrator checks each result against the purpose and the best practices before it acts on it, and sends a role back with the ground where the result falls short. An AI calls the plugin by the same skill, since its own orchestrator also runs in the main conversation.

**Steps**

1. Write an architecture test that runs the orchestrator's part through a start, a result sent back, and a resume of each role, and check that each prompt holds only the run values, the person's words, and the orchestrator's grounds.

### N12

Does the plugin count a point that's the caller's, such as a merge, as approved only by the caller's own act?

**Thinking**

An AI that decides for the caller leaves them answerable for what they never saw, and an approval that an agent can give itself stops nothing. List the points that are the caller's, such as what's hard to undo, like a merge. Make each count as approved only by the caller's own act, such as a skill that the AI can't call.

**Steps**

1. Set `disable-model-invocation: true` in the frontmatter of each skill that approves such a point.

### N13

Does each role ask the person only what's theirs to decide, one question at a time, with a recommendation?

**Thinking**

A point settled before the work doesn't come back as rework, and a question about what the person doesn't care about spends their time on the plugin's job. Matt Pocock's [grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) gives the method. For each point the work needs, ask whether facts can settle it. If they can, the role finds them itself and shows each fact the work rests on. Ask whether the purpose and the best practices settle it. If they do, the role decides it and reports it at the end. Only a point that's left goes to the person: one point per message, with a recommendation.

**Steps**

1. Write an architecture test that resumes the role with an answer, and check that its next message holds one point.

### N14

When something outside the work stops a role, such as a permission or a tool, does the role ask for it and go on with the rest?

**Thinking**

The person clears a missing permission or tool in a moment, while a way around it leaves the work checked on other terms than its purpose set. When something outside the work stops a role, the role asks for it, goes on with the rest meanwhile, and doesn't look for a way around.

**Steps**

1. Write an architecture test whose double of Claude Code denies a call, and check that the role's message asks for it.

### N15

Does the plugin talk with the person in their language, and write the repository in the repository's language?

**Thinking**

The person approves what they read, and others read the repository later. Talk with the person in their language, and write the repository in the repository's language, or English where it has none. Show the person exactly what the plugin writes.

### N16

Before the work reaches its users, does a role that didn't make it check it as the users would?

**Thinking**

The maker reads what it meant, not what it wrote, so a role that didn't make the work checks it first, given only what the work's users have, as Anthropic's [harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps) describes. Ask whether the users get something that no machine can check. If they do, an evaluator checks it. It answers each condition as met, with the lines that meet it, or as not met, with what the users still lack, and never how to fix it, since the maker holds the sources and decides the fix. A hunt for defects finds something in every work and never ends. Where the caller reads the whole work to approve it, such as a plan, no evaluator reads it first, since the caller is its first reader.

**Steps**

1. Give the evaluator's agent only the tools to read the work and write its answers, and lay a lane that holds it to reading only what the work's users have.

### N17

After each run, does the plugin find what fell short and why, and put each lesson where later runs use it?

**Thinking**

A lesson met once should improve every later run, and the user chooses what leaves their project. After the caller approves the work, the main conversation asks once where the run fell short of its goal or cost the user time, and finds why in the records, quoting each cause. For each lesson, ask whether it's the project's own or general. A lesson of the project's own goes into the project's rules. A general lesson goes to the plugin's repository as an issue, only when the user says yes.

**Steps**

1. Have the orchestrator's part read the run's records with Read before it ends, and quote each cause it names.

### N18

Does the plugin write each file where its user chooses whether git keeps it, and nothing in the plugin's own folder?

**Thinking**

One folder named after the plugin lets the user decide with one line of `.gitignore` whether git keeps it. For each file the plugin writes, ask how long it must last. What the user may keep goes in `.<plugin>/<yyyymmdd>-<name>/` at the root of the repository. What the plugin uses only while it runs, its tests' files among them, goes in `<plugin>/<yyyymmdd>-<name>/` in the folder that `tempfile.gettempdir()` gives, which `TMPDIR` moves, and the system clears it. What must outlast an update goes in `${CLAUDE_PLUGIN_DATA}`. Nothing goes in `${CLAUDE_PLUGIN_ROOT}`, which changes with each update. An agent reads without asking only inside the working folder, as [working directories](https://code.claude.com/docs/en/permissions#working-directories) says.

**Steps**

1. Search the plugin for each path it writes, and check that each lies under `.<plugin>/`, the system's temporary folder, or `${CLAUDE_PLUGIN_DATA}`.

### N19

Does the plugin need nothing on the user's machine beyond a runtime that's already there and its standard library?

**Thinking**

A plugin that needs a package the user lacks fails on their machine. Where users' machines may lack other runtimes or packages, run only on a runtime that's already there and its standard library, such as Python 3.9 or later, which is wherever git is, and install no packages. Run the checks in CI on the oldest runtime that the plugin supports and on the newest. Only a run on the oldest shows that the code still runs there, and only a run on the newest shows what a new release breaks.

**Steps**

1. Run the checks in CI on the oldest runtime that the plugin supports and on the newest, such as Python 3.9 and the newest Python.

### N20

Does the marketplace keep code that more than one of its plugins needs in one place?

**Thinking**

Developers write, test, and fix code kept in one place only once. Keep code that more than one plugin needs in the plugin whose job it does, such as Lane's hooks. The others take it in through a relative symbolic link, since installing copies a link's target into the plugin, as [symlinks in a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace#share-files-within-a-marketplace-with-symlinks) documents.

**Steps**

1. Run a check for copied code, such as `pylint --enable=duplicate-code`, over the marketplace's Python.

### N21

Where another plugin already does a job, does the plugin use that plugin's part instead of writing its own?

**Thinking**

The other plugin runs as its makers built and tested it, and nobody writes it again. Name it in `dependencies` of the plugin's `plugin.json`. Then ask whether the job is one role of the other plugin or its whole run. For one role, a route names it as `<dependency>:<role>`, and the main conversation starts it as one of its own and puts its questions to the person, while the other plugin's guard holds its calls. For the whole run, a route names its skill as `<dependency>:<skill>`, and the main conversation calls the skill as one move, which ends once the other plugin gives its result. Meanwhile the other plugin's guard holds the conversation, and this plugin's guard checks nothing, since two guards on one conversation would stop each other's moves.

**Steps**

1. Name the dependency in `plugin.json`, and run `lay.py print` on the routes that name it.

### N22

Do the plugin and the marketplace pass Claude Code's check of their manifests?

**Thinking**

A malformed manifest fails every user at install. Check each plugin and the marketplace with Claude Code's own validator.

**Steps**

1. Run `claude plugin validate --strict` on the plugin and on the marketplace. The trace: `claude plugin validate {deliverable} --strict` run.

### N23

Does each release have a version and a changelog entry that tell users what changed for them?

**Thinking**

Users decide whether to update by what changed for them, and get an update only when the version rises. Release only when whoever decides what reaches users says so. Keep `version` once, in `plugin.json`, in [Semantic Versioning](https://semver.org), since `plugin.json` wins over the marketplace entry. Let the largest change that users see decide which part of the version rises. Give each change that users notice one line in the CHANGELOG, with why it helps them, as [Keep a Changelog](https://keepachangelog.com) does. Tag each release `<plugin>--v<version>`, since a dependency's version range resolves against these tags, and list it in the marketplace and the root README.

**Steps**

1. Tag each release with `claude plugin tag --push`.

### N24

Does the plugin ship a README made for its users by the readme best practice?

**Thinking**

A user learns from the README what they achieve with the plugin and how. Make `README.md` as a deliverable of its own, of the kind [readme](../readme/best-practice.md), from the plugin's product vision and before the plugin's architecture. Keep it in the plugin's folder, so that it reaches each user with the plugin.

### N25

Does each test level say what of Claude Code runs real and what a double replaces, as the architecture's Tests sets?

**Thinking**

Every path should hold on every push, and the trials should meet what users meet. The test levels are those of the [architecture best practice](../architecture/best-practice.md), and the architecture's Tests sets what each runs real for this plugin. No level runs a prompt, a skill, or an agent alone on a model, since a trial of one role alone meets only the cases its developer set up, and finds no fault that a real request brings out. Instead, the guard holds each rule of a role's steps that must hold on every run, and the architecture tests run the guard on each path, with a double in each role's place. The cost: a fault in a prompt shows only in a product vision trial.

**Steps**

1. Write the architecture tests with a double of Claude Code that runs each hook's entry and script in the test's own process, as a new process of Python would run it, and sends what its documentation says or what a recorded run of the real Claude Code showed. Run them with the unit tests before each push.
2. Check each configuration written by hand, such as `hooks.json`, with `claude plugin validate`, since no test runs its commands.
3. Start each Claude Code of a product vision trial on a configuration folder of its own that holds only the plugins under test, with the developer's login as `CLAUDE_CODE_OAUTH_TOKEN`, as [multiple accounts](https://code.claude.com/docs/en/authentication#log-in-with-multiple-accounts) says, since the developer's own settings would change what the trial tries.
4. Have the stand-in answer each request to allow a call from what the screen shows, as a person would.
