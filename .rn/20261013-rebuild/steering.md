# rn that achieves a purpose from a request alone

## Goals

- G1: Whoever wants to hand a whole piece of work to an agent asks for it without preparing anything, only answers what they are asked, and their purpose is achieved; rn 0.10.0 brings this to them.

  Work that takes days then reaches a merged result with the user called only for their own decisions, deciding each sign-off from the proposal alone and going on from the record the next day, as issue #54 says.

## Acceptance criteria

- AC1: On real requests, the user sends back few changes at the deliverable sign-off, none once G1 is reached. Serves G1.

- AC2: On the same requests, the user spends little time from asking to their purpose achieved, with AC1 no worse. Serves G1.

## Tasks

- T41: turn rebuilt on the concept and roles agreed in turn-rebuild.md. Builds on none.

  - The user agrees to builder's and evaluator's steps, then to turn's README and architecture rewritten from turn-rebuild.md. Serves AC1 and AC2.
  - turn is built by .claude/rules/dev.md: check.sh turn 100%, mutate.sh turn 0 survivors, and its acceptance trials passing. Serves AC1.

- T42: rn's meta-checklist and every checklist remade as templates that turn's planner keeps. Builds on T41.

  - Each template holds a kind's Format and Checklist in JSON, and the user approved each kind's purpose and conditions. Serves AC1.

- T46: rn remade on T41's turn. Builds on T42.

  - A request in rough words reaches the plan sign-off with the user asked only the points that are theirs, one per message. Serves AC1 and AC2.
  - The user approves each sign-off from the proposal alone, and meets at the deliverable sign-off a finished work that does every acceptance criterion. Serves AC1 and AC2.
  - The steering holds only what is left and where the session stands, replanned from each move's facts; check.sh rn 100%, mutate.sh rn 0 survivors. Serves AC1.

- T43: rn drops a stopped task. Builds on T46.

  - dev/rn/architecture.md says it as intent and the case is derived from it, dev/rn/ux.md agreeing. Serves AC1.

- T44: rn's checklists back under Vale. Builds on T42.

  - Once the user has merged ccpm#64, plugins/rn/checklists/ pass Vale and .vale.ini's list is shrunk. Serves AC1.

- T34: rn's acceptance test, run whole as its user does on lovaizu/playground. Builds on T46.

  - The user is stood in for by an AI holding what the user truly wants, written beforehand and not shown to rn, and AC1 and AC2 are shown from the records. Serves AC1 and AC2.

- T14: AC1 and AC2 shown on a real request of about an hour. Builds on T34.

  - A command-line tool that tidies a Downloads folder, with its README, design and tests, run once by T34's test, then tried once by the user. Serves AC1 and AC2.

- T45: nothing left that no purpose needs. Builds on T14.

  - The result's work lists no __pycache__/*.pyc, rn's README shows a Walkthrough output from a real run, and plugins/rn/hooks/adapters/items-checklist.py is used or gone. Serves AC1 and AC2.

- T15: users who update get rn 0.10.0 and turn 0.2.0. Builds on T45.

  - Released on the user's instruction. Serves AC1 and AC2.

## Where it stands

Stage: build.

Next: On resume, propose to the user how to go on with T41 from turn-rebuild.md, one decision at a time; the step open is planner's step 4 for the readme template, made from its root down, each level shown to the user: the root put to the user, README's kind purpose: whoever meets the product first decides whether it is for them, gets their first result if it is, and knows where to ask when stuck (GitHub Docs, About READMEs; Google's README guide).

Open:

- Whether the design-tree way of thinking, wanted for every plan, task breakdown and way of going, is kept as a skill or a rule outside the plugins (the user, 2026-10-31: not a plugin matter).
- Whether turn's way of moving a work follows the plugin architecture as it stands (turn-rebuild.md, What turn takes and gives).
