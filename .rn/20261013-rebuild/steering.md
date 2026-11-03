# rn that achieves a purpose from a request alone

## Goals

- G1: Whoever wants to hand a whole piece of work to an agent asks for it without preparing anything, only answers what they are asked, and their purpose is achieved; rn 0.10.0 brings this to them.

  Work that takes days then reaches a merged result with the user called only for their own decisions, deciding each sign-off from the proposal alone and going on from the record the next day, as issue #54 says.

## Acceptance criteria

- AC1: On real requests, the user sends back few changes at the deliverable sign-off, none once G1 is reached. Serves G1.

- AC2: On the same requests, the user spends little time from asking to their purpose achieved, with AC1 no worse. Serves G1.

## Tasks

- T49: lane holds a plugin's flow: the plugin declares the order its roles go in, and lane gives each next move and holds the orchestrator to it. Builds on none.

  - lane's README, UX and architecture promise and design the flow, each passing its template's questions and agreed by the user. Serves AC1.
  - lane depends on no plugin: no code, document or example of it names turn, rn or another ccpm plugin. Serves AC1.
  - check.sh lane 100%, mutate.sh lane 0 survivors, and its trials passing. Serves AC1.

- T41: turn rebuilt on the concept and roles agreed in turn-rebuild.md. Builds on T49.

  - turn's UX, README and architecture are rewritten from turn-rebuild.md and agreed by the user, each written after its kind's template, the Format and the Checklist, is remade by planner's steps and the user has approved the kind's purpose and conditions. Serves AC1 and AC2.
  - turn's code, with its comments and docstrings, is written after the code template is remade the same way, and passes its questions. Serves AC1.
  - turn is built by .claude/rules/dev.md: check.sh turn 100%, mutate.sh turn 0 survivors, and its acceptance trials passing. Serves AC1.

- T47: lane's UX, README, architecture and code comments rewritten on the templates T41 makes. Builds on T41.

  - dev/lane/ux.md, plugins/lane/README.md, dev/lane/architecture.md and the comments and docstrings of lane's code each pass their template's questions and are agreed by the user; code is changed only where the rewritten documents show it must be, added to this task then. Serves AC1.

- T48: dev/architecture.md rewritten on the architecture template T41 makes. Builds on T41.

  - It passes the architecture template's questions and is agreed by the user: it holds what every plugin follows and why, the rules of making, testing and releasing moved to .claude/rules/dev.md or to the scripts that check them, the history of how it was reached gone, and no term of its own where a common word serves. Serves AC1.

- T42: rn's meta-checklist and every checklist remade as templates that turn's planner keeps. Builds on T41.

  - Each template holds a kind's Format and Checklist in JSON, and the user approved each kind's purpose and conditions. Serves AC1.

- T46: rn remade on T41's turn: it carries a run over many turns without drift to a work of value to the user, by grilling the user down a design tree and by ACC, keeping its state compressed from move to move, and calls turn for each work. Builds on T42.

  - A request in rough words reaches the plan sign-off with the user asked only the points that are theirs, one per message. Serves AC1 and AC2.
  - The user approves each sign-off from the proposal alone, and meets at the deliverable sign-off a finished work that does every acceptance criterion. Serves AC1 and AC2.
  - The steering holds only what is left and where the session stands, replanned from each move's facts; check.sh rn 100%, mutate.sh rn 0 survivors. Serves AC1.
  - rn's UX, README, architecture and the comments and docstrings of its code pass their templates' questions. Serves AC1.

- T43: rn drops a stopped task. Builds on T46.

  - dev/rn/architecture.md says it as intent and the case is derived from it, dev/rn/ux.md agreeing. Serves AC1.

- T44: rn's checklists back under Vale. Builds on T42.

  - Once the user has merged ccpm#64, plugins/rn/checklists/ pass Vale and .vale.ini's list is shrunk. Serves AC1.

- T34: rn's acceptance test, run whole as its user does on lovaizu/playground. Builds on T46.

  - The user is stood in for by an AI holding what the user truly wants, written beforehand and not shown to rn, and AC1 and AC2 are shown from the records. Serves AC1 and AC2.

- T14: AC1 and AC2 shown on a real request of about an hour. Builds on T34.

  - A command-line tool that tidies a Downloads folder, with its README, design and tests, run once by T34's test, then tried once by the user. Serves AC1 and AC2.

- T45: nothing left that no purpose needs. Builds on T14.

  - The result's work lists no __pycache__/*.pyc and rn's README shows a Walkthrough output from a real run. Serves AC1 and AC2.

- T15: users who update get rn 0.10.0 and turn 0.2.0. Builds on T45.

  - Released on the user's instruction. Serves AC1 and AC2.

## Where it stands

Stage: build.

Next: Done 2026-11-03: Lane's UX, README, architecture, docs/lanes.md and docs/routes.md (was flow.md) rewritten on the settled shape and pushed, each derived from the settled shape and not put to the user, who reviews Lane once it is built (the user, 2026-11-03); the decisions taken meanwhile: routes and a result script that lay.py puts into hooks/lane/, a result counted only from a run of it that succeeded, run_only in place of hands_off, hold in place of wait_for, the lanes of the end checked as the result is given, start_with, as_printed and follow_next gone, a subagent's part given whole at SubagentStart with ${CLAUDE_PLUGIN_ROOT} put in, Lane's logic in hooks/lane/core/domain/, Claude Code 2.1.316 required. Tried on Claude Code 2.1.316 (2026-11-03): SubagentStop fires at a resumed run's end, with the same agent_id, and SubagentStart fires again; a resume by SendMessage returns at once and its end reaches the caller as a task notification; a PreToolUse ask is put to the person interactively even under bypassPermissions, and is a denial in -p; UserPromptExpansion fires on a typed plugin skill command and not on the Skill tool; a forked skill's hooks carry agent_type <plugin>:<agent> only when agent: names it so, the bare name running general-purpose; ${CLAUDE_PLUGIN_ROOT} is put in in a plugin agent's and skill's body before the model reads it; a Bash call that exits non-zero gives PostToolUseFailure, its exit code only in the error text. Next: Lane's code (T49) on the rewritten documents, in three units: U1 run_only and write_only laid and checked (O1), given to a subagent on 2026-11-03; U2 routes, the result script and follow_routes (O2); U3 the other lanes, the part at SubagentStart, values, adapters, lay.py up and hold; each by tests first, then the code, the trial plugin and trials; dev/lane/tests/test_lanes_json.py fails meanwhile, as it reads docs/flow.md. dev/architecture.md:318 says an orchestrator in a skill is held by its own steps; a forked skill runs as a subagent, so T48 rewrites that. dev/package.json pins Claude Code 2.1.310 below the README's 2.1.316. Then turn (T41), whose architecture is rewritten with every decision below. Settled with the user, 2026-11-03: a plugin keeps outside Claude Code's fixed folders a core/ of pure logic that depends on no agent such as Claude Code or Codex, in core/domain (knowledge and rules: turn's best practices) and core/roles (each role's flow, turn's as core/roles/up.md), each placing its prompts, scripts and assets as it needs; dev/architecture.md fixes only these two paths and says the principles (no dependence on outer technology; domain and use cases apart); images sit in images/ beside the document that shows them; tests sit in dev/<plugin>/tests/ by the levels of the architecture's test table, unit/ by the path of what they test, integration/ and e2e/, test_*.py for code and trial_*.py for runs of an AI; a subagent that needs the person's answer ends and is resumed by SendMessage with its context, so wait.py goes; Lane's flow becomes routing, renamed when Lane is rebuilt: from a declaration of routes (from a role, on a result, to a role) it takes each role's result, tells the next and stops any other start; a role's result is given by its calling a script of its own plugin with the result as argument, the script checking the work's form, and Lane lets the role stop only once that call succeeded; the names of results are each plugin's (turn's evaluator: good, more); a command held for the person's approval is put to the person by Claude Code's own permission prompt, a PreToolUse hook answering ask, so wait_for and its search of messages for a word go, and an approval of what a work says is a role's ask answered. To try before building: SubagentStop on a resumed run's end, the same agent ID across a resume, and whether a hook's ask still prompts under bypassPermissions. Decided by what each should be, 2026-11-03 (the user: what is plain from best practice is decided, not asked): Lane judges only from documented hook input and from calls of a plugin's own scripts, never from the model's text, a parse of a shell string or Claude Code's undocumented record, so record.py's reading of the record goes; rn's /rn:ty approval is recorded by a UserPromptExpansion hook, which fires only on a command the person types; a role's Bash runs only the commands its plugin declares for it, matched whole, and it reads and writes by Read, Grep, Write and Edit, whose paths the hook input gives, so read_only, write_only and hands_off check documented fields; as_printed goes, a script handing on what it prints by a file it writes; every_item and end_when go into the end script, which checks the work's form and that each question has its answer; follow_flow and follow_next go into routing; start_with goes, the orchestrator's script making the run ready before it starts a role; test_after becomes the plugin's test script recording the tree it tested with the result, which the end script compares; in_form stays; a role's part reaches it whole by a SubagentStart hook's additionalContext, and reading a work whole is checked from Read's file_path, offset and limit; turn:up is also given to the person as a skill with context: fork and agent turn:up; Workflow is not used, as it takes no answer from the person mid-run; every plugin hook runs on every tool call, as a plugin's agent cannot hold hooks of its own. To try before building, besides: UserPromptExpansion on a plugin skill's command, and hooks seeing agent_type in a forked skill. Gaps settled with the user: no bin/, as no official plugin uses it and claude.ai and Cowork do not install a plugin with it, so executables that depend on Claude Code sit in scripts/ at the plugin's root; Lane stays laid into each plugin whole, a link in the ccpm marketplace and a copy elsewhere, not called as a dependency's MCP server, whose tools the AI could call itself, and its shared code shrinks as the record and shell parsing go. practices.py passes check.sh and every ground that is no PDF holds its title and words (2026-11-03); the 32 PDF grounds are not checked by the script. Left: the user has yet to read the six documents and the best practices.

Open:

- Whether the design-tree way of thinking, wanted for every plan, task breakdown and way of going, is kept as a skill or a rule outside the plugins (the user, 2026-10-31: not a plugin matter).
- Whether turn's way of moving a work follows the plugin architecture as it stands (turn-rebuild.md, What turn takes and gives).
- Whether prose-lint, hposal-plugin and worktree-aiya, branches of other work, are still needed (the user's to judge).
