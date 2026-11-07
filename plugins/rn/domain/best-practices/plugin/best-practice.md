# `plugin`

## Goal

The developer builds a Claude Code plugin whose roles work together to make something, with which its users achieve what they're after.

## Template

[template](template)

## Inputs

- [architecture](../../../../turn/core/domain/best-practices/architecture/best-practice.md)

## Intents

| ID | About | Question |
| --- | --- | --- |
| Q1 | domain, skills, agents, hooks, scripts | Placing a file of the plugin, does the developer see which part takes the form Claude Code fixes and which holds the work's own knowledge, so that each job lies in one place and what the plugin knows outlives the agent it runs on? |
| Q2 | agents, skills, domain | Starting a role, does the developer have it hold its whole part before its first call, each file the part names found wherever Claude Code installs the plugin, so that the role works from all it has to do? |
| Q3 | domain | Writing a role's part, does the developer put in it only what the role has to do and which parts of the best practice it uses, so that the role takes the practices as the steps of its work and no copy of them drifts? |
| Q4 | agents | Splitting the work into roles, does the developer give each job a role of its own with only what the job needs, so that nothing from other work leads a role astray? |
| Q5 | skills, agents | Following a run from the person's request, does the developer see the main conversation start each role, put each point a role has for the person to them as given, and take the answer back word for word, so that no agent between them rewords a question or sums up an answer? |
| Q6 | domain | Starting, resuming, or ending a role, do the main conversation and the guard find what passes between them in one fixed form, so that a machine checks each start and each end? |
| Q7 | domain | Choosing how to keep a file that the plugin reads, does the developer keep it in a form that a script checks, so that a file out of form shows before anyone reads it? |
| Q8 | hooks | Following a run from a role's end to the next start, does the developer find the course in routes that the guard holds, so that every run takes the same moves and a stopped one goes on from its last? |
| Q9 | hooks | Where an instruction alone doesn't hold a step, does the developer have a hook stop the role and tell it the step again when it drifts, so that the step holds on every run? |
| Q10 | hooks, scripts | Reading what a check gave, does the developer tell a pass from a check that couldn't run, so that nothing passes unchecked? |
| Q11 | scripts | Checking a role's work, does the developer have a script or the project's own tools check all that a machine can see, so that an AI reads only for what no machine can? |
| Q12 | scripts | Writing a file as it runs, does the plugin put it where its user chooses whether git keeps it, so that a stopped run leaves nothing behind and an update loses nothing? |
| Q13 | scripts, hooks | Running on a user's machine, does the plugin need only what's already there, so that it runs wherever git does? |
| Q14 | hooks, scripts | Needing code that another plugin of the marketplace has, does the developer take it in through a link, so that the developer writes, tests, and fixes it in one place? |
| Q15 | .claude-plugin, hooks | Having another plugin do a job, does the developer take the part of it that does the job, so that the other runs as its makers built and tested it and nobody writes it again? |
| Q16 | skills | Reaching a point that's the caller's, such as a merge, does the plugin take it as approved only by the caller's own act, so that no AI decides for them? |
| Q17 | domain | Meeting a point that the work needs, does a role put to the person only what's theirs, one point at a time with a recommendation, so that a point settled before the work doesn't come back as rework? |
| Q18 | domain | When something outside the work stops a role, such as a permission or a tool, does the role ask for it and go on with the rest, so that the work stays checked on the terms its purpose set? |
| Q19 | domain | Reading what the plugin says and writes, do the person and the repository's later readers each find it in their own language, so that the person approves what they read? |
| Q20 | agents | Before the work reaches its user, does a role that didn't make it check it in the user's place, so that the work's user gets what they're after and not what its maker meant? |
| Q21 | skills, domain | Once a run ends, does the plugin take in what fell short and why, so that a lesson met once improves every later run? |
| Q22 | skills, agents, hooks | Testing the plugin at each level that its architecture names, does the developer know what of Claude Code to run real and what to stand in for, so that every path holds on every push and the trials meet what users meet? |
| Q23 | .claude-plugin | Installing the plugin, does each user get a manifest that Claude Code reads, so that the install never fails on its form? |
| Q24 | .claude-plugin, CHANGELOG.md | Deciding whether to update, does a user find what changed for them in a version they get, so that they update knowing what it gives? |
| Q25 | README.md | Coming to the plugin, does its user find a README made for them, so that they learn from it what they achieve with the plugin and how? |
| Q26 | the whole | Using a plugin built by this best practice, do its users achieve what they're after? |

## Practices

### Q1

Placing a file of the plugin, does the developer see which part takes the form Claude Code fixes and which holds the work's own knowledge, so that each job lies in one place and what the plugin knows outlives the agent it runs on?

**Thinking**

Skills, agents, hooks, and scripts take the form Claude Code fixes, each named as its caller calls it, such as the command a person types, and hand the job to the file in `domain/` that does it. `domain/` holds the knowledge of the work in one folder, with no folders split by role, and names no tool of an agent, such as the Agent tool or `AskUserQuestion`: only the entries name them. What only the developers need, such as the tests and the architecture, lies outside the plugin's folder, as installing copies only that folder. A developer then finds a job where the structure puts it, two entries to one job don't drift apart, and what the plugin knows outlives the agent it runs on, as [hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/) says.

**Steps**

1. Grep `domain/` for the name of each tool of an agent, and move each line it finds to the entry that uses the tool.

### Q2

Starting a role, does the developer have it hold its whole part before its first call, each file the part names found wherever Claude Code installs the plugin, so that the role works from all it has to do?

**Thinking**

An entry's body says that the plugin's folder is `${CLAUDE_PLUGIN_ROOT}` and names the role's part in `domain/`. The guard gives a role its part whole as the role starts, through the `SubagentStart` hook's `additionalContext`, with the folder put in, and the skill's body has the main conversation read its part whole first. The part names each file as `${CLAUDE_PLUGIN_ROOT}/<path>`. Claude Code makes an agent's body its system prompt and reads no other file into it. It puts the folder in place of `${CLAUDE_PLUGIN_ROOT}` only in an entry's own body, not in what the Bash tool runs nor in a file that Read reads, as [environment variables](https://code.claude.com/docs/en/plugins/manifest-reference#environment-variables) says. After `/compact`, a part that a skill names comes back whole, while the skill's own body survives only as the summary retells it.

**Steps**

1. Run `lay.py print` on the plugin's proposal, and read in what it prints that it found each role's part.

### Q3

Writing a role's part, does the developer put in it only what the role has to do and which parts of the best practice it uses, so that the role takes the practices as the steps of its work and no copy of them drifts?

**Thinking**

A role's part says what the role has to do, what a machine can see once it's done, what it's given, the best practice and the intents whose practices it carries out, and what it gives as it ends, as `domain/role.md` shows. The steps of the work are those practices, which the guard holds one by one. Steps copied into a part drift from the practices they came from, and the role then follows the copy.

**Steps**

1. Grep each part for a numbered list, and replace each step it holds with the intent whose practice the step carries out.

### Q4

Splitting the work into roles, does the developer give each job a role of its own with only what the job needs, so that nothing from other work leads a role astray?

**Thinking**

Where a work has jobs that need different context or tools, each job has a role of its own, an agent whose `tools` name only what the job needs. A role starts in a fresh context, so nothing from other work leads it astray, as [subagents](https://code.claude.com/docs/en/sub-agents) says.

**Steps**

1. Set each agent's `tools` to the tools that its part's practices use, and `background: true`, as the guard counts a start once its role ends.

### Q5

Following a run from the person's request, does the developer see the main conversation start each role, put each point a role has for the person to them as given, and take the answer back word for word, so that no agent between them rewords a question or sums up an answer?

**Thinking**

Where a plugin has roles, its skill makes the main conversation the orchestrator. Nobody relays: the main conversation starts each role the routes name, so each role's point reaches it, and it puts the point to the person as given and resumes the role with their answer word for word by SendMessage. It makes, judges, and decides nothing of the work. A subagent's last message reaches only the one who started it, and only the main conversation can ask the person, as [subagents](https://code.claude.com/docs/en/sub-agents#available-tools) says. So an agent between them would only carry points: a point reworded on the way is a question that no role asked, and an answer summed up loses what the person meant. A resumed role keeps its whole conversation, as [resume subagents](https://code.claude.com/docs/en/sub-agents#resume-subagents) says. An AI calls the plugin by the same skill, as its own orchestrator runs in the main conversation too.

**Steps**

1. Write an architecture test that runs the skill's part through a start and a resume of each role, and check that each prompt holds only the run values and the person's words.

### Q6

Starting, resuming, or ending a role, do the main conversation and the guard find what passes between them in one fixed form, so that a machine checks each start and each end?

**Thinking**

Each role's in and out keep to JSON Schemas in `domain/`, drawn from `domain/role-in.schema.json` and `domain/role-out.schema.json`. A role starts with one JSON line of run values, the values that the guard holds its calls to, and resumes with a message whose first line is `The person's answer, word for word:`. It ends by giving a result, a fixed word such as `asks` or `done`, by Lane's result script, and its last message begins with `For the person:` where it holds a point for the person. A role that judges a work by questions writes its answers with the lines of the work that meet each question. A machine checks a fixed form, while words written freely leave each reader to guess.

**Steps**

1. Write each role's two schemas, and have the script that a role runs before it gives its result hold the role's answers to them.

### Q7

Choosing how to keep a file that the plugin reads, does the developer keep it in a form that a script checks, so that a file out of form shows before anyone reads it?

**Thinking**

A file that a plugin reads is JSON held to a JSON Schema, with a tree nested in it, such as a design tree. A document that the plugin rewrites, such as the design tree or a round's answers, is JSON. A record that it only adds to, such as Lane's calls, is JSON Lines, so that adding a record never rewrites what's there. A script finds a file out of form before anyone reads it, and the guard checks the nodes around a change to a tree, so the parts around it don't drift. A file that shows the form of a deliverable, such as a template or an example, keeps the deliverable's own format, as a template in another format shows a form that the deliverable can't take.

**Steps**

1. Have each script that reads a file hold it to its schema, and write a unit test that gives the script a file out of form and checks that the script fails with the schema's error.

### Q8

Following a run from a role's end to the next start, does the developer find the course in routes that the guard holds, so that every run takes the same moves and a stopped one goes on from its last?

**Thinking**

Where a run goes in fixed moves, its routes keep the course. Lane lays them in `hooks/lanes.json` from the plugin's proposal, and gives the main conversation each next start from the role that ended and the result it gave. Code follows a course the same way every time, where a conversation told the course drifts from it. Lane keeps each run's state in a file, so a compacted or stopped conversation goes on from its last move. Where a run's course changes with what it finds, the skill's part keeps the course instead.

**Steps**

1. Write the routes in the plugin's proposal, run `lay.py print` on it and read what it prints, and then run `lay.py write`.

### Q9

Where an instruction alone doesn't hold a step, does the developer have a hook stop the role and tell it the step again when it drifts, so that the step holds on every run?

**Thinking**

A lane holds each practice step whose drift shows in a tool call or in how a role ends: its hook stops what would break the step and gives the role the step again. Branch protection or permission rules hold what's hard to undo. A hook runs every time, while an instruction is only advice. Hooks fire on the main conversation's calls with no `agent_type`, and on a role's with the role's, as [hooks](https://code.claude.com/docs/en/hooks) says, so one `hooks/hooks.json` holds both. A plugin's agent ignores `hooks`, `mcpServers`, and `permissionMode` in its own frontmatter, as [plugin agents](https://code.claude.com/docs/en/plugins/components#frontmatter-fields-in-plugin-agents) says, and a `SubagentStop` hook in a skill's frontmatter didn't fire in a trial on Claude Code 2.1.318, so the plugin keeps its hooks in `hooks/hooks.json`.

**Steps**

1. Name in each step of the best practices that the roles use a trace that a machine can check, such as a command run, a file read, or a test made, and lay a lane on it in the proposal.

### Q10

Reading what a check gave, does the developer tell a pass from a check that couldn't run, so that nothing passes unchecked?

**Thinking**

A check ends in one of three results: no problem, a problem, or couldn't check, such as the exit codes 0, 1, and 2. The developer decides beforehand what follows each, and tests it. A hook whose command fails stops the call, by `onFailure: block`, and a hook that finds no Python 3.9 stops each call of the plugin's own roles with why. A skipped test, a job that didn't run, or a command that failed counts as no pass. A reader takes a check that stays silent when it couldn't check for one that found nothing.

**Steps**

1. Write a unit test for each of the three results of each check, and an architecture test that runs each hook with its script missing.

### Q11

Checking a role's work, does the developer have a script or the project's own tools check all that a machine can see, so that an AI reads only for what no machine can?

**Thinking**

A script, a hook, or the project's own tools, such as a formatter, a linter, or a type checker, check what a machine can check. An AI reads only for what no machine can. A tool finds the same thing every time, at once. An AI finds only some, and spends a round on each.

**Steps**

1. List what each role's work must hold, and give each item a machine can see to a script that the role runs before it gives its result.

### Q12

Writing a file as it runs, does the plugin put it where its user chooses whether git keeps it, so that a stopped run leaves nothing behind and an update loses nothing?

**Thinking**

A plugin writes what the user may keep in `.<plugin>/<yyyymmdd>-<name>/` at the root of the repository. It writes what it uses only while it runs, its tests' files among them, in `<plugin>/<yyyymmdd>-<name>/` in the folder that `tempfile.gettempdir()` gives, which TMPDIR moves. It writes what must outlast an update in `${CLAUDE_PLUGIN_DATA}`, and nothing in `${CLAUDE_PLUGIN_ROOT}`. One folder named after the plugin lets the user choose with one line of `.gitignore` whether git keeps it. The system clears its temporary folder, so a stopped run leaves nothing behind. An agent reads without asking only inside the working folder, as [working directories](https://code.claude.com/docs/en/permissions#working-directories) says. `${CLAUDE_PLUGIN_ROOT}` changes with each update.

**Steps**

1. Grep the plugin for each path it writes, and check that each lies under `.<plugin>/`, the system's temporary folder, or `${CLAUDE_PLUGIN_DATA}`.

### Q13

Running on a user's machine, does the plugin need only what's already there, so that it runs wherever git does?

**Thinking**

Where users' machines may lack other runtimes or packages, what runs there needs only Python 3.9 or later and its standard library. python3 is wherever git is, and a plugin installs no packages. CI runs the checks on Python 3.9 and on the newest Python: only a run on 3.9 shows that the code still runs there, and only a run on the newest shows what a new Python breaks.

**Steps**

1. Run the checks in CI on Python 3.9 and on the newest Python.

### Q14

Needing code that another plugin of the marketplace has, does the developer take it in through a link, so that the developer writes, tests, and fixes it in one place?

**Thinking**

A plugin keeps code that more than one plugin needs once, in the plugin whose job that code does, such as Lane's hooks. The others take it in through a relative symbolic link, as installing copies a link's target into the plugin, which [symlinks in a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace#share-files-within-a-marketplace-with-symlinks) documents.

**Steps**

1. Run a check for copied code, such as `pylint --enable=duplicate-code`, over the marketplace's Python.

### Q15

Having another plugin do a job, does the developer take the part of it that does the job, so that the other runs as its makers built and tested it and nobody writes it again?

**Thinking**

Where another plugin already does a job, the plugin names it in `dependencies` of its `plugin.json`. Where one role of the other does the job, a route names the role as `<dependency>:<role>`, and the main conversation starts it as one of its own and puts its points to the person, while the other's guard holds its calls. Where the job is the other's whole run, a route names its skill as `<dependency>:<skill>`, and the main conversation calls the skill as one move, which ends once the other gives its result. Meanwhile the other's guard holds the conversation, and the plugin's own checks nothing, as two guards on one conversation would stop each other's moves.

**Steps**

1. Name the dependency in `plugin.json`, and run `lay.py print` on routes that name it.

### Q16

Reaching a point that's the caller's, such as a merge, does the plugin take it as approved only by the caller's own act, so that no AI decides for them?

**Thinking**

The caller decides what's theirs, and what's hard to undo, such as a merge. Such a point counts as approved only by the caller's own act, such as a skill the AI can't call. An AI that decides for the caller leaves them answerable for what they never saw, and an approval that an agent can give itself stops nothing.

**Steps**

1. Set `disable-model-invocation: true` in the frontmatter of each skill that approves such a point.

### Q17

Meeting a point that the work needs, does a role put to the person only what's theirs, one point at a time with a recommendation, so that a point settled before the work doesn't come back as rework?

**Thinking**

Where a plugin talks with a person, a role puts to them every point that only they can decide, one point a message, with a recommendation. It finds facts itself, and shows each fact the work rests on. It decides everything else, and reports it at the end. A point settled before the work doesn't come back as rework, and a question about what the person doesn't care about spends their time on the plugin's job, as [grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) says.

**Steps**

1. Write an architecture test that resumes the role with an answer, and check that its next message holds one point.

### Q18

When something outside the work stops a role, such as a permission or a tool, does the role ask for it and go on with the rest, so that the work stays checked on the terms its purpose set?

**Thinking**

When something outside the work stops it, the role asks for it, goes on with the rest meanwhile, and never looks for a way round. The person clears such a cause in a moment. A way round leaves the work checked on other terms than its purpose set.

**Steps**

1. Write an architecture test whose double of Claude Code denies a call, and check that the role's message asks for it.

### Q19

Reading what the plugin says and writes, do the person and the repository's later readers each find it in their own language, so that the person approves what they read?

**Thinking**

Where a plugin talks with a person, it talks in the person's language, and writes the repository in the repository's language, English where it has none. It shows the person exactly what it writes. The person approves what they read, and others read the repository later.

### Q20

Before the work reaches its user, does a role that didn't make it check it in the user's place, so that the work's user gets what they're after and not what its maker meant?

**Thinking**

Where the work's user gets something no machine can check, an evaluator, a role that didn't make the work, checks it first, given only what the user has. It answers each question as met, with the lines that meet it, or as not met, with what the user still lacks, never how to make it. Where the caller reads the whole work to approve it, such as a plan, no evaluator reads it first, as the caller is its first reader. The maker reads what it meant, not what it wrote. A hunt for defects finds something in every work, and never ends. The maker holds the sources, so how to mend is its call, as [harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps) says.

**Steps**

1. Give the evaluator's agent only the tools to read the work and write its answers, and lay a lane that holds it to reading only what the work's user has.

### Q21

Once a run ends, does the plugin take in what fell short and why, so that a lesson met once improves every later run?

**Thinking**

Where a person calls the plugin, the main conversation looks once, after the caller approves the work, through what the run kept, for what fell short and why, quoting each cause from the records. It puts a lesson of the project's own into the project's rules, and sends a general lesson to the plugin's repository as an issue, only when the user says yes. A lesson met once improves every later run, and the user chooses what leaves their project.

**Steps**

1. Have the skill's part read the run's records with Read before it ends, and quote each cause it names.

### Q22

Testing the plugin at each level that its architecture names, does the developer know what of Claude Code to run real and what to stand in for, so that every path holds on every push and the trials meet what users meet?

**Thinking**

The test levels are the [architecture best practice](../../../../turn/core/domain/best-practices/architecture/best-practice.md)'s. No level runs a prompt, a skill, or an agent alone on a model: the guard holds each rule of a role's steps that must hold on every run, and the architecture tests run the guard on each path, with a double in each role's place. A trial of one role alone meets only the cases that its developer set up, so it finds no fault that a real request brings out. A double of Claude Code runs each hook's entry and script in the test's own process, as a new process of Python would run it, and sends what its documentation says or what a recorded try of the real Claude Code showed. `claude plugin validate` checks a configuration written by hand, such as `hooks.json`, and no test runs its commands. Each Claude Code that a product vision trial starts runs on a configuration folder of its own, holding only the plugins under test, with the developer's login as `CLAUDE_CODE_OAUTH_TOKEN`, as [multiple accounts](https://code.claude.com/docs/en/authentication#log-in-with-multiple-accounts) says, and the stand-in answers each ask to allow a call from what the screen shows, as a person would. The developer's own settings would change what the trial tries. The cost: a fault in a prompt shows only in a product vision trial.

**Steps**

1. Write the architecture tests with a double of Claude Code that runs each hook's entry in the test's own process, and run them with the unit tests before each push.

### Q23

Installing the plugin, does each user get a manifest that Claude Code reads, so that the install never fails on its form?

**Thinking**

Each plugin and the marketplace pass Claude Code's own check of their manifests, as a malformed manifest fails every user at install.

**Steps**

1. Run `claude plugin validate --strict` on the plugin and on the marketplace.

### Q24

Deciding whether to update, does a user find what changed for them in a version they get, so that they update knowing what it gives?

**Thinking**

A plugin gets a release only when whoever decides what reaches users says so. `plugin.json` holds `version` once, in semver, and the largest change that users see decides which part of it rises, as users get an update only when the version rises and `plugin.json` wins over the marketplace entry. The CHANGELOG gives each change that users notice one line, with why it helps them. Each release has a tag `<plugin>--v<version>`, as a dependency's version range resolves against these tags, and the marketplace and the root README list it.

**Steps**

1. Tag each release by `claude plugin tag --push`.

### Q25

Coming to the plugin, does its user find a README made for them, so that they learn from it what they achieve with the plugin and how?

**Thinking**

`README.md` is a deliverable of its own, of the kind [readme](../../../../turn/core/domain/best-practices/readme/best-practice.md), made from the plugin's product vision before the plugin's architecture. The plugin keeps it in its folder, so the README reaches each user with the plugin.

### Q26

Using a plugin built by this best practice, do its users achieve what they're after?

**Thinking**

Each practice is the ideal for the case it names. A plugin takes what its architecture calls for, and where it differs from a practice, its architecture says why. Build each next plugin by this best practice, and mend each place where it falls short where the shortfall lies, in the goal, the template, a question, or a practice, as only a plugin built and used shows whether the whole works.
