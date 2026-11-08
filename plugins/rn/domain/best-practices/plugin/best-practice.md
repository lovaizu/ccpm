# `plugin`

## Goal

The user, a person or an AI working in Claude Code, installs the plugin and gets from it, on every run, the work its README promises.

## Inputs

- [architecture](../architecture/best-practice.md)

## Preconditions

- [code](../code/best-practice.md)
- [prompt](../prompt/best-practice.md)

## Parts

- **manifest**: what Claude Code and the user read to install, enable, and update the plugin: its `.claude-plugin/plugin.json` and its entry in its marketplace, with its permanent name, its version, what it does, who made it, where its source and license lie, and each plugin it depends on.
- **skills**: each skill the user or Claude calls, its frontmatter saying who may call it and what it may run without asking, and its body a prompt the prompt best practice makes.
- **agents**: each subagent, a role with a context of its own, its frontmatter naming the tools it may use, and its body a prompt the prompt best practice makes.
- **hooks**: what Claude Code runs at its events, in `hooks/hooks.json` or a skill's frontmatter: each hook's event, its matcher, what it runs, and what happens to the call when it fails.
- **code**: the scripts, executables, and servers the other parts run, each made by the code best practice, with what each needs on the user's machine.
- **data**: what the plugin writes as it runs, each thing where it lasts as long as its user needs it: the user's work in their project, what outlasts an update in `${CLAUDE_PLUGIN_DATA}`, and what serves one run in the system's temporary folder.
- **evals**: the cases of the plugin's real use, each a request a user would make with a check of what they're after, run in fresh sessions with and without the plugin, and the record of each run.
- **changelog**: `CHANGELOG.md`: for each version, what changed for the user, a line each, with what they gain or must change.
- **readme**: `README.md`: what the user reads to choose the plugin and start with it, a deliverable of the readme kind, kept in the plugin's folder so that it reaches each user with the plugin.

## Intents

| ID | About | Question |
| --- | --- | --- |
| Q1 | evals | Before making the plugin's components, does the maintainer hold cases of its real use, each a request a user would make with a check of what they're after, run in fresh sessions with and without the plugin, so that each component answers a shortfall the cases show, and the maintainer knows from the cases when to stop? |
| Q2 | skills, agents, hooks, code | Choosing what carries each job, does the maintainer give it to the least powerful kind of component that holds it as firmly as it must, such as code for what a machine decides the same way each time, a hook for a rule that must hold on every call, a skill for work that needs judgment, and a subagent only for work that needs a context of its own, so that nothing that must hold rests on the AI's attention and nothing costs more than its job? |
| Q3 | skills, agents | Reaching a point that's the user's, such as an act that's hard to undo or a choice only they can make, does the plugin put it to the user from the main conversation and act only on their answer, so that no AI decides what's theirs? |
| Q4 | agents, skills, hooks, code | Giving each component what it may do, does the maintainer grant only the tools, commands, and files its job uses, so that a slip of the AI, or an order hidden in what it reads, can't reach past its job? |
| Q5 | hooks | When a hook that holds a rule can't run, as when its script is missing, crashes, or times out, does the call it guards stop with why, so that no rule passes because its check never ran? |
| Q6 | manifest, skills, agents, hooks | In a session where the user never calls the plugin, does it add to Claude's context only what Claude needs to find it, and start no process on an event where it has no work, so that having it enabled costs the user next to nothing? |
| Q7 | data | Writing what a run keeps, does the plugin put each thing where it lasts as long as its user needs it and no longer, so that an update loses nothing and a run leaves nothing behind that the user didn't ask for? |
| Q8 | data, skills, agents | When a run stops, Claude Code compacts its conversation, or a new session takes it up, does the plugin go on from what it wrote down, so that the user loses no work, no step runs twice, and no point the user settled comes back? |
| Q9 | manifest, code, readme | Installed from its marketplace on a fresh machine that holds only what its README asks for, does every component find each file and tool it uses, so that the plugin works for its users as it did for its maintainer? |
| Q10 | manifest, code | Needing what another plugin does, does the maintainer depend on it by name, with the range of its versions they tested against, and keep each piece of shared code in one plugin, so that a release of the other never breaks the user's install and a fix lands in one place? |
| Q11 | manifest, changelog | Deciding whether to update, does the user get each release under a version that rises by what changed for them, with a changelog that says in a line each what they gain or must change, so that they update knowing what it gives and what it breaks? |
| Q12 | the whole | Using a plugin made by this best practice, for cases held back from its making, do its users get the work its README promises, on every run? |

## Practices

### Q1

Before making the plugin's components, does the maintainer hold cases of its real use, each a request a user would make with a check of what they're after, run in fresh sessions with and without the plugin, so that each component answers a shortfall the cases show, and the maintainer knows from the cases when to stop?

**Name**

Evaluation-driven development, also known as evals first, baseline comparison, and no-plugin baseline

**Thinking**

Write the cases before the components. Take each from a use the README promises, as a request a user would type, with a check of the outcome they're after, such as a file the run makes or what the reply says. Add cases where the plugin must stay out of the way, such as a near request it isn't made for, as a set of only the cases where it should act trains a plugin that acts everywhere. Run each case in a fresh session with the plugin and again without it, several times each, as one run of an agent says little, and only the difference shows what the plugin gives. Then make each component to close a shortfall the runs without it show, and nothing more. Grade the outcome, not the path. Grade with a script wherever a script can check it, and keep a model's judgment for what only a reader can judge. Read the transcripts of failing runs, as a grader can fail for its own fault. Claude Code's `claude plugin eval` runs a case in an isolated session with only the plugin loaded, three times with it and three without, and scores each against its graders. Where a use spans turns in which the user answers the plugin, a case of one prompt can't carry it, so run that use through a driver that plays the user, such as a stand-in that holds an intent the plugin isn't given.

**Applies**

Every plugin, before its first component, and again before each release and each change of a component or of the model it runs on. Where the plan makes a part as a deliverable of its own, such as the plugin's code, its cases come with the architecture that the plan makes the part from.

**Excludes**

A case of the plugin's whole use doesn't test one function or one hook alone. The code best practice tests those, and the architecture best practice says what each test level runs real.

**Cost**

Each run of a case makes real model calls on the maintainer's account: three runs with the plugin and three without, by default. The cases come before any component works, and a driver that plays the user is code of its own to make and test.

**Sources**

- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Test plugins with evals, in the Claude Code docs](https://code.claude.com/docs/en/plugin-evals)
- [Extend Claude with skills, in the Claude Code docs](https://code.claude.com/docs/en/skills)
- [Anthropic, Demystifying evals for AI agents, 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic, Equipping agents for the real world with Agent Skills, 2025](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### Q2

Choosing what carries each job, does the maintainer give it to the least powerful kind of component that holds it as firmly as it must, such as code for what a machine decides the same way each time, a hook for a rule that must hold on every call, a skill for work that needs judgment, and a subagent only for work that needs a context of its own, so that nothing that must hold rests on the AI's attention and nothing costs more than its job?

**Name**

Rule of least power

**Thinking**

For each job of the plugin, take the least powerful kind of component that holds it as firmly as the job must hold, as what a less powerful means does is easier to foresee, check, and secure. A machine decides the same way each time, so give code whatever it can decide, such as reading a file into its form or checking a result, and have the prompt run it. A rule that must hold on every call goes to a hook, as Claude Code runs a hook on each of its events whether or not Claude follows the skill, while an instruction in a skill or in `CLAUDE.md` is a request. A skill carries work that needs judgment, loads its body only when called, and runs in the conversation that calls it. A subagent carries work that needs a context of its own, such as reading many files to report a little, and costs a context and a summary on the way back. A skill that runs on its own needs no subagent, and work whose steps you can fix in advance needs a workflow, not an agent that plans them. A Model Context Protocol (MCP) server connects to a system outside, and a skill says how to use it. Keep each job in one component, and have the others reach it only through what it takes and gives, such as a script's arguments and output or a role's start and end, as the plug-in or microkernel architecture keeps each plug-in apart from the others behind a contract.

**Applies**

Each job of the plugin, as its architecture names them, when it's placed and whenever it moves.

**Excludes**

The body of a skill or an agent is the prompt best practice's. The code best practice divides the code inside each component.

**Cost**

A rule moved to a hook or a script is code to write and test, and each subagent costs a fresh context and a handoff.

**Sources**

- [Berners-Lee and Mendelsohn, The Rule of Least Power, W3C, 2006](https://www.w3.org/2001/tag/doc/leastPower.html)
- [Anthropic, Building effective agents, 2024](https://www.anthropic.com/engineering/building-effective-agents)
- [Extend Claude Code, in the Claude Code docs](https://code.claude.com/docs/en/features-overview)
- [Add components to a plugin, in the Claude Code docs](https://code.claude.com/docs/en/plugins/components)
- [Extend Claude with skills, in the Claude Code docs](https://code.claude.com/docs/en/skills)
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic, Equipping agents for the real world with Agent Skills, 2025](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Richards, Software Architecture Patterns, O'Reilly 2015, Microkernel Architecture](https://www.oreilly.com/content/software-architecture-patterns/)

### Q3

Reaching a point that's the user's, such as an act that's hard to undo or a choice only they can make, does the plugin put it to the user from the main conversation and act only on their answer, so that no AI decides what's theirs?

**Name**

Human in the loop, also known as human oversight

**Thinking**

A point is the user's where only they can know the answer, where ways that serve alike are theirs to pick, or where an act is hard to undo, such as a deploy, a merge, or a message sent for them. Put each such point to the user before the act, and act only on their answer. Only the main conversation can ask the user: a subagent has no `AskUserQuestion`, and its last message reaches only the conversation that started it. So a role in a subagent that meets the user's point ends with the point, and the main conversation puts it to the user as given and resumes the role with their answer word for word, as a point reworded on the way is a question no role asked. A skill whose act is the user's to start takes `disable-model-invocation: true`, so that Claude can't call it on its own judgment, and Claude Code blocks Claude's attempt to call it. Points of fact, and points where one way serves the goal more than the others, aren't the user's: the plugin finds or decides them, and says so in its report.

**Applies**

Each point of a run that's the user's, and each skill whose act has effects outside the conversation that the user decides on.

**Excludes**

Where a run has no one to ask, such as in `claude -p`, the plugin stops before such an act and reports the point, and never takes it on its own judgment.

**Cost**

Each point waits for the user, so a run that asks too often costs their time, and the plugin must tell their points from its own.

**Sources**

- [Extend Claude with skills, in the Claude Code docs](https://code.claude.com/docs/en/skills)
- [Create custom subagents, in the Claude Code docs](https://code.claude.com/docs/en/sub-agents)
- [Extend Claude Code, in the Claude Code docs](https://code.claude.com/docs/en/features-overview)

### Q4

Giving each component what it may do, does the maintainer grant only the tools, commands, and files its job uses, so that a slip of the AI, or an order hidden in what it reads, can't reach past its job?

**Name**

Principle of least privilege, also known as least authority

**Thinking**

Every program should run with the least set of privileges its job needs. Give each subagent `tools` that name only what its job uses, such as a reviewer with Read, Grep, and Glob and no Write, and leave out `Agent` where it mustn't start subagents of its own. Give each skill `allowed-tools` only for the commands it runs without asking, each matched as narrowly as the command allows. A plugin's agent ignores `permissionMode`, `hooks`, and `mcpServers` in its frontmatter, so a limit that a role needs beyond `tools` goes to the plugin's hooks. Hooks, monitors, and servers run with the user's own permissions and outside the sandbox, and permission rules don't reach them, so they read only what their event gives them and treat it as data, quoting each variable and refusing a path that leaves the project. Content that a component reads, such as a web page, can carry an order to the AI, and a narrow grant is what keeps such an order from reaching past the job.

**Applies**

Every component that can act: each subagent, each skill that runs commands, each hook, and each server.

**Excludes**

A grant the user gives in their own settings is theirs, and the plugin neither widens nor assumes it.

**Cost**

A grant that's too narrow stops the work at a missing tool, so try each grant on the cases of real use.

**Sources**

- [Saltzer and Schroeder, The Protection of Information in Computer Systems, 1975](https://www.cs.virginia.edu/~evans/cs551/saltzer/)
- [Create custom subagents, in the Claude Code docs](https://code.claude.com/docs/en/sub-agents)
- [Add components to a plugin, in the Claude Code docs](https://code.claude.com/docs/en/plugins/components)
- [Plugin security and trust, in the Claude Code docs](https://code.claude.com/docs/en/plugins/security)
- [Hooks reference, in the Claude Code docs](https://code.claude.com/docs/en/hooks)

### Q5

When a hook that holds a rule can't run, as when its script is missing, crashes, or times out, does the call it guards stop with why, so that no rule passes because its check never ran?

**Name**

Fail-safe defaults, also known as fail closed

**Thinking**

A check that couldn't run is no pass. On most events, when a hook fails, times out, or can't start, Claude Code still carries out the action, so a guard with a wrong path or a crashing script lets everything through. Set `onFailure: "block"` on each command hook that holds a rule, so that the call stops with why. Deny with exit code 2 or with a JSON decision, as exit code 1 is a non-blocking error and lets the call go on. Where the hook needs a runtime the user may lack, check for it first and stop the guarded call with a message that says what to install. Give each check three results, such as passed, failed, and couldn't check, and decide in advance what follows each, as a reader takes a silent check for one that found nothing. Try each hook once with its script missing and once timing out, and see the call stop.

**Applies**

Each hook that holds a rule, such as one that stops a write or holds a role's end until it finishes its steps.

**Excludes**

A hook that only reports, such as one that formats a file or logs a call, can fail open, as the call needs nothing from it. Leave `onFailure` unset there, so that a broken formatter never stops the user's work.

**Cost**

A broken guard stops every call it matches until it's mended, so its matcher stays narrow and its failure says what to fix.

**Sources**

- [Saltzer and Schroeder, The Protection of Information in Computer Systems, 1975](https://www.cs.virginia.edu/~evans/cs551/saltzer/)
- [Hooks reference, in the Claude Code docs](https://code.claude.com/docs/en/hooks)

### Q6

In a session where the user never calls the plugin, does it add to Claude's context only what Claude needs to find it, and start no process on an event where it has no work, so that having it enabled costs the user next to nothing?

**Name**

Progressive disclosure

**Thinking**

An enabled plugin is part of every session, not only the sessions where it's used. The name and description of each skill, agent, and command that Claude can call on its own stay in Claude's context on every turn, and its hooks fire on their events from the moment the session loads it. So keep each description to what the plugin does and when to use it, with its key use first, as Claude matches requests against it and Claude Code cuts it short when the listing overflows. Set `disable-model-invocation: true` on a skill only the user starts, as its description then leaves the context. Narrow each hook's matcher to the calls it has work in, and where the hook serves only the plugin's own runs, register it in the skill's frontmatter, which Claude Code reads only once the user or Claude calls the skill. Each body loads only when used, and each file it names only when read. `claude plugin details` shows the always-on cost of each component, and Anthropic's official marketplace shows users that cost before they install.

**Applies**

Each description, each hook's event and matcher, and each server the plugin starts.

**Excludes**

A hook that must hold on calls outside the plugin's own runs, such as one that guards a protected file in every session, matches those calls, as the user installed the plugin for it.

**Cost**

A shorter description can keep Claude from choosing a skill, so check its choosing in the cases of real use after each trim. A hook that a skill registers runs only after a call of the skill, and stays for the rest of the session.

**Sources**

- [Plugins overview, in the Claude Code docs](https://code.claude.com/docs/en/plugins/overview)
- [Measure plugin cost and usage, in the Claude Code docs](https://code.claude.com/docs/en/plugins/measure)
- [Extend Claude Code, in the Claude Code docs](https://code.claude.com/docs/en/features-overview)
- [Extend Claude with skills, in the Claude Code docs](https://code.claude.com/docs/en/skills)
- [Add components to a plugin, in the Claude Code docs](https://code.claude.com/docs/en/plugins/components)
- [Anthropic, Equipping agents for the real world with Agent Skills, 2025](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

### Q7

Writing what a run keeps, does the plugin put each thing where it lasts as long as its user needs it and no longer, so that an update loses nothing and a run leaves nothing behind that the user didn't ask for?

**Name**

Separation of code and state, also known as stateless processes

**Thinking**

The plugin's code and its state live apart, as each update replaces the code. `${CLAUDE_PLUGIN_ROOT}` is the installed version's own folder, and it changes with each update, with the old folder removed 14 days later, so write nothing there. Keep what must outlast an update, such as installed packages or a cache, in `${CLAUDE_PLUGIN_DATA}`, which survives updates and goes when the user uninstalls the plugin from the last place it's installed. Keep the user's work, and what they may want git to keep, in their project, in one folder named after the plugin, so that one line of `.gitignore` decides it. Keep what serves only one run, the tests' files among them, in the system's temporary folder, and remove it as the run ends, so that a finished run leaves nothing behind and a run stopped halfway leaves nothing the user must clean up.

**Applies**

Each file, folder, or record the plugin writes as it runs, and each that its tests write.

**Excludes**

A file the user asks the plugin to write, such as a document it drafts, goes where the user says.

**Cost**

The plugin finds each place through a variable or the system's call, never a fixed path, and its tests run it with each place moved.

**Sources**

- [Plugin manifest reference, in the Claude Code docs](https://code.claude.com/docs/en/plugins/manifest-reference)
- [Add components to a plugin, in the Claude Code docs](https://code.claude.com/docs/en/plugins/components)
- [Plugin loading reference, in the Claude Code docs](https://code.claude.com/docs/en/plugins/loading)
- [Wiggins, The Twelve-Factor App, VI. Processes](https://12factor.net/processes)

### Q8

When a run stops, Claude Code compacts its conversation, or a new session takes it up, does the plugin go on from what it wrote down, so that the user loses no work, no step runs twice, and no point the user settled comes back?

**Name**

Durable state, also known as progress file, checkpointing, and resumable workflow

**Thinking**

A run that outlasts one context keeps its state in files, not in the conversation, as a compacted conversation keeps only a summary and a new session starts with nothing. After compaction, Claude Code re-attaches only the first 5,000 tokens of each skill called, so the instructions that must last stand near the top of the skill. Write each step's result as the step ends, in a form a script reads, such as JSON held to a schema, as a model changes a Markdown file it shouldn't more often than a JSON one. Have each start of the plugin read that state and take up the next step, and record each point the user settled with their answer, so that a new session asks nothing twice. Commit the user's work to git as each piece ends, where the plugin works in a repository, so that a bad step can be undone. SendMessage resumes a subagent with its whole conversation within its session, and a new session finds the role's state only in what it wrote.

**Applies**

A run whose work outlasts one turn or one session, or whose steps a stop between them would break.

**Excludes**

A plugin whose every run ends in one turn, such as a formatter, keeps no state.

**Cost**

Each step writes its state and each start reads it, and the state's form is a contract to keep through each release.

**Sources**

- [Anthropic, Effective harnesses for long-running agents, 2025](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Extend Claude with skills, in the Claude Code docs](https://code.claude.com/docs/en/skills)
- [Create custom subagents, in the Claude Code docs](https://code.claude.com/docs/en/sub-agents)
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

### Q9

Installed from its marketplace on a fresh machine that holds only what its README asks for, does every component find each file and tool it uses, so that the plugin works for its users as it did for its maintainer?

**Name**

Smoke test, also known as build verification test

**Thinking**

Each user gets a copy of the plugin's folder and nothing else. Claude Code copies a marketplace plugin into its cache, leaves out each file outside the plugin's folder, and rejects a component path that leaves it, so a script that reads `../shared` finds nothing after an install. Name each file a component uses through `${CLAUDE_PLUGIN_ROOT}`, which Claude Code puts in place in hook and server commands and in skill and agent bodies, though not in what the Bash tool runs. Declare each runtime and tool the plugin needs, in the README, which reaches each user in the plugin's folder, and in a check that says what's missing, as a plugin that assumes a tool on the maintainer's machine fails on the user's. Bundle what you can't ask the user to install, or install it on first use into `${CLAUDE_PLUGIN_DATA}`, as a `SessionStart` hook can. Before each release, add the marketplace from a local path, install the plugin from it on a machine that holds only what the README asks for, and run a case of its real use. Validate each manifest with Claude Code's own check, which reports a path out of the plugin and a field it doesn't know.

**Applies**

Every plugin, before each release, the first among them.

**Excludes**

A plugin loaded with `--plugin-dir` or from a marketplace added from a local path loads in place, not as a copy, so a run there doesn't show what an install gives the user.

**Cost**

A fresh machine for each release, such as a container, and a case run on it.

**Sources**

- [Plugin loading reference, in the Claude Code docs](https://code.claude.com/docs/en/plugins/loading)
- [Add components to a plugin, in the Claude Code docs](https://code.claude.com/docs/en/plugins/components)
- [Plugin manifest reference, in the Claude Code docs](https://code.claude.com/docs/en/plugins/manifest-reference)
- [Publish and distribute a plugin, in the Claude Code docs](https://code.claude.com/docs/en/plugins/publish)
- [Wiggins, The Twelve-Factor App, II. Dependencies](https://12factor.net/dependencies)
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

**Steps**

1. Run Claude Code's own check of the plugin's manifests after your last change to them. The trace: `claude plugin validate {deliverable} --strict` run.

### Q10

Needing what another plugin does, does the maintainer depend on it by name, with the range of its versions they tested against, and keep each piece of shared code in one plugin, so that a release of the other never breaks the user's install and a fix lands in one place?

**Name**

Declared dependencies, also known as version constraints

**Thinking**

Where another plugin already does a job, depend on it, not on a copy of it, so that it runs as its makers built and tested it. Name it in `dependencies` of `plugin.json`, and Claude Code installs and enables it with the plugin. Give it a range of versions you tested against, such as `~2.1.0`, as a bare name follows each new release of it the next time users update, and one that renames what the plugin calls breaks every install. The range resolves against the other plugin's git tags, `<name>--v<version>`, so a plugin that others depend on tags each release. A dependency from another marketplace installs only where the root marketplace allows that marketplace. Where plugins of one marketplace share code, keep it once, in the plugin whose job it does, and have the others take it through a relative symbolic link, which Claude Code dereferences into the copy it installs. Code copied between plugins gets a fix in one and stays broken in the other, as don't repeat yourself warns.

**Applies**

Each plugin the plugin calls, and each piece of code that more than one plugin of a marketplace needs.

**Excludes**

Claude Code skips a symbolic link to a file outside the marketplace at install, and keeps only links inside the plugin's own folder for a plugin installed from a local path. Code shared with no other plugin stays in the plugin.

**Cost**

Each widened range is a release of the plugin, tested against the other's new version first.

**Sources**

- [Plugin dependencies, in the Claude Code docs](https://code.claude.com/docs/en/plugins/dependencies)
- [Host and maintain a marketplace, in the Claude Code docs](https://code.claude.com/docs/en/plugins/host-marketplace)
- [Publish and distribute a plugin, in the Claude Code docs](https://code.claude.com/docs/en/plugins/publish)
- [Plugin manifest reference, in the Claude Code docs](https://code.claude.com/docs/en/plugins/manifest-reference)
- [Richards, Software Architecture Patterns, O'Reilly 2015, Microkernel Architecture](https://www.oreilly.com/content/software-architecture-patterns/)

### Q11

Deciding whether to update, does the user get each release under a version that rises by what changed for them, with a changelog that says in a line each what they gain or must change, so that they update knowing what it gives and what it breaks?

**Name**

Semantic Versioning

**Thinking**

A user gets an update only when the version in `plugin.json` changes, as a version set there pins the plugin until it rises, and that version wins over the marketplace entry's. So raise it with each release, by what changed for the user: the major part for a change that breaks what they did before, the minor part for something added, and the patch part for a fix. A version under 1.0.0 may change anything, so leave it once users rely on the plugin. Keep each fact of the plugin in one place, such as its description in `plugin.json`, as two copies drift. Never rename a published plugin, as Claude Code records each install under its name, and change `displayName` instead. Keep `CHANGELOG.md` as Keep a Changelog says: an entry for each version, newest first, with its date, its changes grouped as Added, Changed, Deprecated, Removed, Fixed, and Security, and each change in a line that says what the user gains or must change, as a changelog is for people, not machines. List each deprecation, removal, and breaking change first, as those are what users must act on. Fill in what users read before they install, `description`, `author`, `homepage`, `repository`, and `license`, as installing copies only the plugin's folder.

**Applies**

Each release of the plugin, and each change that users notice.

**Excludes**

In a git-hosted marketplace a plugin may leave `version` out, and each commit then reaches users as an update, which suits a plugin that has no releases. A change that users never notice, such as a test, gets no changelog line.

**Cost**

Each release takes a judgment of what changed for users, and a line for each change.

**Sources**

- [Preston-Werner, Semantic Versioning 2.0.0](https://semver.org/)
- [Lacan, Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
- [Publish and distribute a plugin, in the Claude Code docs](https://code.claude.com/docs/en/plugins/publish)
- [Plugin manifest reference, in the Claude Code docs](https://code.claude.com/docs/en/plugins/manifest-reference)
- [Plugin loading reference, in the Claude Code docs](https://code.claude.com/docs/en/plugins/loading)

### Q12

Using a plugin made by this best practice, for cases held back from its making, do its users get the work its README promises, on every run?

**Name**

Pilot testing, also known as held-out evaluation

**Thinking**

Hold back some cases of real use from the making, as a plugin made to pass its cases may pass only those. Have a user, or a stand-in that holds an intent the plugin isn't given, use the plugin on each case held back, on each model its users run, from a fresh install. Read what each run made and its transcript, not only the counts, and trace each shortfall to the part it lies in and to the question that should have caught it. Mend it there, add the case to the kept ones, and hold back new ones for the next trial. Watch how users use the plugin after its release, such as a skill that never triggers or a file Claude never reads, and take each finding back the same way.

**Applies**

Every plugin, before its first release and after each change that its cases didn't cover.

**Excludes**

A pilot shows whether the whole works for its users. It doesn't show which question judges a part right, which the kept cases beside this best practice show.

**Cost**

Cases held back can't shape the plugin, so the maintainer needs more cases than they build from, and each trial is real runs.

**Sources**

- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic, Demystifying evals for AI agents, 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic, Equipping agents for the real world with Agent Skills, 2025](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Rajasekaran, Harness design for long-running apps, Anthropic, 2026](https://www.anthropic.com/engineering/harness-design-long-running-apps)
