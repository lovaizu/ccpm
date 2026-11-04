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

- T50: Pin, a plugin of its own in ccpm, pins a plan down from its purpose: a design tree from the goal down, the user asked only what is theirs, one point at a time, nothing left assumed; Turn and rn take it in by dependencies. Builds on none.

  - Pin's skill, pin:down, made from Matt Pocock's grilling skill (MIT, credited) and turn-rebuild.md's Design tree, and its script checking a design-tree.json: every question served, every decision reaching the root, the order following builds_on. Serves AC1.
  - tried first: a role of Turn runs the script of Pin, its dependency, and Lane checks that call; if it cannot, where the script lies is decided again. Serves AC1.
  - Pin is built by .claude/rules/dev.md: check.sh Pin 100%, mutate.sh Pin 0 survivors, and its trials passing. Serves AC1 and AC2.

- T41: turn rebuilt on the concept and roles agreed in turn-rebuild.md. Builds on T49 and T50.

  - turn's UX, README and architecture are rewritten from turn-rebuild.md and agreed by the user, each written after its kind's template, the Format and the Checklist, is remade by planner's steps and the user has approved the kind's purpose and conditions. Serves AC1 and AC2.
  - turn's code, with its comments and docstrings, is written after the code template is remade the same way, and passes its questions. Serves AC1.
  - turn is built by .claude/rules/dev.md: check.sh turn 100%, mutate.sh turn 0 survivors, and its acceptance trials passing. Serves AC1.

- T47: lane's UX, README, architecture and code comments rewritten on the templates T41 makes. Builds on T41.

  - dev/lane/ux.md, plugins/lane/README.md, dev/lane/architecture.md and the comments and docstrings of lane's code each pass their template's questions and are agreed by the user; code is changed only where the rewritten documents show it must be, added to this task then. Serves AC1.

- T51: users who update get Lane, Pin and Turn, with rn held at 0.8.0 and writ gone, before rn is rebuilt. Builds on T41 and T47.

  - the marketplace lists Lane, Pin and Turn at their new versions, rn pinned to the tag rn--v0.8.0 (5adb39ae), which needs no writ and holds no links, and no writ; 0.9.0 is left unused, as it does not work (the user, 2026-11-03). Serves AC1.
  - released on the user's instruction, the branch merged once Turn is rebuilt. Serves AC1 and AC2.

- T42: rn's meta-checklist and every checklist remade as templates that turn's planner keeps. Builds on T41.

  - Each template holds a kind's Format and Checklist in JSON, and the user approved each kind's purpose and conditions. Serves AC1.

- T46: rn remade on T41's turn: it carries a run over many turns without drift to a work of value to the user, by grilling the user down a design tree and by ACC, keeping its state compressed from move to move, and calls turn for each work. Builds on T42 and T50.

  - A request in rough words reaches the plan sign-off with the user asked only the points that are theirs, one per message. Serves AC1 and AC2.
  - The user approves each sign-off from the proposal alone, and meets at the deliverable sign-off a finished work that does every acceptance criterion. Serves AC1 and AC2.
  - The steering holds only what is left and where the session stands, replanned from each move's facts; check.sh rn 100%, mutate.sh rn 0 survivors. Serves AC1.
  - rn's UX, README, architecture and the comments and docstrings of its code pass their templates' questions. Serves AC1.
  - rn's commands named again from what each does once rebuilt, as rn:gm, which sends back feedback, reads as good morning (the user, 2026-11-03: names fit each command's essence, not one another). Serves AC1.
  - rn's prompts hold the steps of writing an issue and a pull request and of the check before a pull request is marked ready, and .claude/rules/issue.md and final-check.md point to them, keeping only ccpm's own (the user, 2026-11-04). Serves AC1.

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

- T15: users who update get rn 0.10.0, rebuilt, its Pin to 0.8.0 removed. Builds on T45 and T51.

  - Released on the user's instruction. Serves AC1 and AC2.

## Where it stands

Stage: build.

Next: Where it stands, 2026-11-04: T48 done. The user asked (2026-11-04) to remake, before release, the UX, README and architecture of Lane, Pin and Turn, each from a design tree in Pin's form, by the right use of the best practice, then build and test to them until the three can be released (T51). The right use, agreed with the user: a best practice holds the Standard (goal, parts, questions) and, for each question, its Practice (thinking, steps, grounds). 1. Design: the document's goal at the root of a design tree in .rn/20261013-rebuild/design/<plugin>-<kind>.json, the template's questions under it, and under each the decisions that make it yes, each decided by that question's Practice, thinking and steps, its grounds as the reason; Pin's check.py passes; the decisions shown to the user in short lines and approved before any sentence is written. 2. Make: the decisions written along the template's parts, the small points by the Practice's steps; then every question answered as the document's user, a shortfall mended at its decision. 3. Finish: refactor-doc's questions and their Practice steps, the paraphrase test of Q3 among them, the parts kept. 4. Show the finished document; the user agrees before the next. A document is checked by its questions as its reader, never against the code (the user, 2026-11-04). Figures: a sequence in Mermaid (no semicolon inside a message, as Mermaid ends a statement there); every other figure, and a table taken in whole at a glance such as the test table with its ●●● weights, as an SVG in dev/images or beside the document in the style of dev/images/figures.css (python3 dev/scripts/figures.py write); a table looked up by row stays Markdown (refactor-doc.json Q3). A UX scenario shows the user's way from need to gain, the product one closed box, each arrow a few words, never the spec. Turn has two making roles, generator and evaluator: the refactoring phase runs them with the refactoring template, the phase a run value; refactorer and proofreader go, and Lane and the router serve that design, never the reverse. Order: Lane, then Pin, then Turn; in each, UX, README, architecture. Lane's UX too is made again, as 29ebc382 was written before its decisions were settled. The user does not review (2026-11-04): the best practices and the three plugins carry the intent, so every point is decided from them and best practice and the work goes through to release-ready; step 4's agreement and step 1's showing are the assistant's own check, each told at the end. Then the code, tests and lanes changed to the documents by .claude/rules/dev.md steps 5 to 8 (code unit tests and architecture tests with doubles; no unit trial of a prompt, the user decided 2026-11-04: a prompt written by prompt.json leaves only the AI's variance and design faults, the rules that must hold are held by Lane's hooks and tested at architecture, and the ux trials, E2E on a subject big enough to bring out the frequent cases, find design faults and measure the variance by the key results; so first change dev/plugin-best-practice.md's Test and its figure, prompt.json Q14 to Q16, and .claude/rules/dev.md step 6c to say so, every file that rests on them with them; e2e-finish's 9a6156d3 and 5d12e281 judged by the E2E), a check in check.sh that each test-table cell and path has its test, Turn's ux trials once, then T51 on the user's word. Also left: the writing pass over every prose file of Lane, Pin and Turn not yet done (hooks' messages, skills, agents, forms, test prompts, changelogs, every comment and docstring), as a bad form left anywhere spreads. rn is out of scope (the user, 2026-11-04): held at 0.8.0, nothing under plugins/rn or dev/rn changed; only the marketplace entry points it to the tag. Well-known OSS tools under a licence such as MIT may be installed for development without asking (the user, 2026-11-04), such as mermaid-cli to check that each Mermaid figure renders. Push with git -c core.hooksPath=dev/scripts/githooks push, retried on a remote error, and read its CI before the next push.

Open:

None.
