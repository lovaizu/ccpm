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

- T50: pin, a plugin of its own in ccpm, pins a plan down from its purpose: a design tree from the goal down, the user asked only what is theirs, one point at a time, nothing left assumed; Turn and rn take it in by dependencies. Builds on none.

  - pin's skill, pin:down, made from Matt Pocock's grilling skill (MIT, credited) and turn-rebuild.md's Design tree, and its script checking a design-tree.json: every question served, every decision reaching the root, the order following builds_on. Serves AC1.
  - tried first: a role of Turn runs the script of pin, its dependency, and Lane checks that call; if it cannot, where the script lies is decided again. Serves AC1.
  - pin is built by .claude/rules/dev.md: check.sh pin 100%, mutate.sh pin 0 survivors, and its trials passing. Serves AC1 and AC2.

- T41: turn rebuilt on the concept and roles agreed in turn-rebuild.md. Builds on T49 and T50.

  - turn's UX, README and architecture are rewritten from turn-rebuild.md and agreed by the user, each written after its kind's template, the Format and the Checklist, is remade by planner's steps and the user has approved the kind's purpose and conditions. Serves AC1 and AC2.
  - turn's code, with its comments and docstrings, is written after the code template is remade the same way, and passes its questions. Serves AC1.
  - turn is built by .claude/rules/dev.md: check.sh turn 100%, mutate.sh turn 0 survivors, and its acceptance trials passing. Serves AC1.

- T47: lane's UX, README, architecture and code comments rewritten on the templates T41 makes. Builds on T41.

  - dev/lane/ux.md, plugins/lane/README.md, dev/lane/architecture.md and the comments and docstrings of lane's code each pass their template's questions and are agreed by the user; code is changed only where the rewritten documents show it must be, added to this task then. Serves AC1.

- T48: dev/architecture.md rewritten on the architecture template T41 makes. Builds on T41.

  - It passes the architecture template's questions and is agreed by the user: it holds what every plugin follows and why, the rules of making, testing and releasing moved to .claude/rules/dev.md or to the scripts that check them, the history of how it was reached gone, and no term of its own where a common word serves. Serves AC1.

- T51: users who update get Lane, pin and Turn, with rn held at 0.8.0 and writ gone, before rn is rebuilt. Builds on T41, T47 and T48.

  - the marketplace lists Lane, pin and Turn at their new versions, rn pinned to the tag rn--v0.8.0 (5adb39ae), which needs no writ and holds no links, and no writ; 0.9.0 is left unused, as it does not work (the user, 2026-11-03). Serves AC1.
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

- T15: users who update get rn 0.10.0, rebuilt, its pin to 0.8.0 removed. Builds on T45 and T51.

  - Released on the user's instruction. Serves AC1 and AC2.

## Where it stands

Stage: build.

Next: Where it stands, 2026-11-04: Lane and pin built and on rebuild; Turn's documents and code on rebuild; check.sh exit 0 and CI green at 1cab0703. The test design was remade (the user, 2026-11-04): Turn's architecture best practice (Q11 to Q13) tests at three levels named by what they check against, unit (a part's contract: classes, edges, decision-table rules), architecture (every path of each sequence, what joins the parts run real, each role an AI runs and Claude Code a double built from its contract's form) and ux (each objective's scenario at a real request's size, a stand-in with a hidden intent, confirming only); a fault found higher is tested first at the level that missed it. dev/architecture.md's Test, .claude/rules/dev.md steps 5 to 7, and the Test sections, Sequences and path lists of dev/lane, dev/pin, dev/turn and dev/rn architecture.md follow it; tests lie in unit/, architecture/ and ux/ (rn's stay flat until T46). Turn's E2E rounds were stopped, as they found design faults one at a time; branch e2e-finish holds 9a6156d3 (parts split around shared ground) and 5d12e281 (a goal not asked twice), not merged, to be judged against the new tests. readme.json's walkthrough now shows one real run, not steps to follow, and Q6 asks only the install (the user, 2026-11-04). Lane's architecture tests cover every path of its table, with the double of Claude Code in dev/lane/testing.py, and its five case trials are gone (3fdeabf1); the paths showed three faults, fixed with the architecture: a result no route is on is stopped by the hook, a run that ended with no result is not resumed and counts no more once one is started in its place, and the guard holds laid routes to lay.py print's check. pin's architecture tests cover each path (eed62d27, 8c0c13b0). The pinner's trials failed mostly by their own faults (a judge that miscounts, a stand-in that sees only the last turn, a case that never arose), written at once and run whole; how to make a prompt's trials is now prompt.json's trials part, Q14 to Q16 (6a8c35a3), and the user's feedback kept only in notes is now in .claude/rules (76c09465). The user asked (2026-11-04) that the repository's rules link to the best practices as far as they can, keeping only what is the repository's own, such as versions and names: prompt.json's Q17 now holds how a decision is put to the person, for rn, Turn, pin and the assistant, and output.md points to it. The rules link to the best practices as far as they can: dev.md to meta.json's Q8, code.json's Q6 and prompt.json's Q14 to Q16 (d1368596); output.md's Verification to prompt.json's Q18, a claim reported as far as it was checked, keeping only check.sh by its exit code and a push done once its CI is read; refactor-doc.json's Q3 draws a diagram as an SVG that follows the page's color-scheme (the user, 2026-11-04). Issues and pull requests get no best practice of their own, as they are short forms whose writing prompt.json's Q17 and refactor-doc.json already hold (the user, 2026-11-04): rn's prompts hold the steps of making them, and issue.md and final-check.md point there once T46 makes them. Every figure carries the one style of dev/images/figures.css, held by dev/figures.py in check.sh (c5ec46d9). CI stops a run when a push follows on the same branch, and checks from the last commit whose run passed (c70536bb); CI green at c70536bb. The documents go before the trials (the user, 2026-11-04), as the trials follow dev/architecture.md's test rules and the templates T47 and T48 wait for exist: Next: 1. T48, dev/architecture.md rewritten on architecture.json and refactor-doc.json, its test and trial rules settled, shown to the user for agreement. 2. T47, lane's UX, README and architecture, each shown and agreed before the next. 3. The trial's own parts rebuilt once in dev/lane/trials/trying.py, which pin's and Turn's trials share, each checked on a record kept from a first run, as no record is kept yet; then the pinner's trials by prompt.json Q14 to Q16 one case at a time, pinner.md's and planner.md's five labelled lines becoming prompt.json's Q17 and pinner.md:86's patched line taken out; then Turn's trials the same way, judging e2e-finish's two commits by them. 4. A check in check.sh that each test-table cell and path has its test in its level's folder. 5. Turn's ux trials once, each trial's runs at once, written while trials run. Then T51. Push only once the run before has been read.

Open:

None.
